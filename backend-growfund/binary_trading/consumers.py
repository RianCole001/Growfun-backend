"""
WebSocket Consumers for Real-Time Binary Trading
Handles price streaming and trade updates via WebSockets.
"""
import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from decimal import Decimal
from django.utils import timezone


class PriceStreamConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time price streaming.
    
    Client subscribes to specific assets and receives continuous price updates.
    
    Message format from client:
        {
            "action": "subscribe",
            "symbols": ["EURUSD", "BTC", "GOLD"]
        }
    
    Message format to client:
        {
            "type": "price_update",
            "data": {
                "symbol": "EURUSD",
                "price": "1.0850",
                "timestamp": "2026-05-03T10:30:00Z",
                "change_percent": 0.05
            }
        }
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.subscribed_symbols = set()
        self.price_task = None
        self.user = None
    
    async def connect(self):
        """Handle WebSocket connection"""
        # Get user from scope (set by AuthMiddleware)
        self.user = self.scope.get('user')
        
        # Accept connection (authentication handled by middleware)
        await self.accept()
        
        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection',
            'status': 'connected',
            'message': 'Price stream connected'
        }))
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Stop price streaming task
        if self.price_task:
            self.price_task.cancel()
        
        # Leave all subscribed groups
        for symbol in self.subscribed_symbols:
            await self.channel_layer.group_discard(
                f'prices_{symbol}',
                self.channel_name
            )
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            action = data.get('action')
            
            if action == 'subscribe':
                await self.handle_subscribe(data.get('symbols', []))
            elif action == 'unsubscribe':
                await self.handle_unsubscribe(data.get('symbols', []))
            elif action == 'ping':
                await self.send(text_data=json.dumps({'type': 'pong'}))
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': f'Unknown action: {action}'
                }))
        
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))
    
    async def handle_subscribe(self, symbols):
        """Subscribe to price updates for specific symbols"""
        for symbol in symbols:
            symbol = symbol.upper()
            if symbol not in self.subscribed_symbols:
                self.subscribed_symbols.add(symbol)
                
                # Join channel group for this symbol
                await self.channel_layer.group_add(
                    f'prices_{symbol}',
                    self.channel_name
                )
        
        # Start price streaming if not already running
        if not self.price_task or self.price_task.done():
            self.price_task = asyncio.create_task(self.stream_prices())
        
        await self.send(text_data=json.dumps({
            'type': 'subscribed',
            'symbols': list(self.subscribed_symbols)
        }))
    
    async def handle_unsubscribe(self, symbols):
        """Unsubscribe from price updates"""
        for symbol in symbols:
            symbol = symbol.upper()
            if symbol in self.subscribed_symbols:
                self.subscribed_symbols.remove(symbol)
                
                # Leave channel group
                await self.channel_layer.group_discard(
                    f'prices_{symbol}',
                    self.channel_name
                )
        
        await self.send(text_data=json.dumps({
            'type': 'unsubscribed',
            'symbols': list(symbols)
        }))
    
    async def stream_prices(self):
        """
        Continuously stream price updates for subscribed symbols.
        Generates new ticks every 200-500ms.
        """
        from .price_generator import PriceGeneratorManager
        
        manager = PriceGeneratorManager()
        
        try:
            while self.subscribed_symbols:
                # Generate ticks for all subscribed symbols
                for symbol in list(self.subscribed_symbols):
                    try:
                        # Get generator and generate tick
                        generator = await database_sync_to_async(
                            manager.get_generator
                        )(symbol)
                        
                        tick = await database_sync_to_async(
                            generator.generate_tick
                        )()
                        
                        # Store tick in database (async)
                        await self.store_price_tick(symbol, tick['price'])
                        
                        # Send price update to client
                        await self.send(text_data=json.dumps({
                            'type': 'price_update',
                            'data': {
                                'symbol': symbol,
                                'price': str(tick['price']),
                                'timestamp': tick['timestamp'].isoformat(),
                                'change_percent': tick.get('change_percent', 0),
                                'regime': tick.get('regime', 'unknown')
                            }
                        }))
                    
                    except Exception as e:
                        print(f"⚠️ Error generating tick for {symbol}: {e}")
                
                # Random delay between 200-500ms for realistic streaming
                import random
                delay = random.uniform(0.2, 0.5)
                await asyncio.sleep(delay)
        
        except asyncio.CancelledError:
            # Task was cancelled (client disconnected)
            pass
        except Exception as e:
            print(f"⚠️ Price streaming error: {e}")
    
    @database_sync_to_async
    def store_price_tick(self, symbol, price):
        """Store price tick in database"""
        from .models import TradingAsset, AssetPrice
        
        try:
            asset = TradingAsset.objects.get(symbol=symbol)
            AssetPrice.objects.create(asset=asset, price=price)
        except Exception as e:
            print(f"⚠️ Failed to store price for {symbol}: {e}")
    
    # Handler for group messages (broadcast)
    async def price_broadcast(self, event):
        """Receive price broadcast from channel layer"""
        await self.send(text_data=json.dumps(event['data']))


class TradeUpdatesConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time trade updates.
    
    Sends updates when:
    - Trade is opened
    - Trade expires and is settled
    - Balance changes
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.user_group = None
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.user = self.scope.get('user')
        
        if not self.user or not self.user.is_authenticated:
            await self.close()
            return
        
        # Join user-specific group
        self.user_group = f'trades_{self.user.id}'
        await self.channel_layer.group_add(
            self.user_group,
            self.channel_name
        )
        
        await self.accept()
        
        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection',
            'status': 'connected',
            'message': 'Trade updates connected'
        }))
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        if self.user_group:
            await self.channel_layer.group_discard(
                self.user_group,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """Handle incoming messages"""
        try:
            data = json.loads(text_data)
            action = data.get('action')
            
            if action == 'ping':
                await self.send(text_data=json.dumps({'type': 'pong'}))
            elif action == 'get_active_trades':
                await self.send_active_trades()
        
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))
    
    async def send_active_trades(self):
        """Send list of active trades to client"""
        trades = await self.get_active_trades()
        
        await self.send(text_data=json.dumps({
            'type': 'active_trades',
            'trades': trades
        }))
    
    @database_sync_to_async
    def get_active_trades(self):
        """Get active trades for user"""
        from .models import BinaryTrade
        from .serializers import BinaryTradeSerializer
        
        trades = BinaryTrade.objects.filter(
            user=self.user,
            status='active'
        ).select_related('asset')
        
        serializer = BinaryTradeSerializer(trades, many=True)
        return serializer.data
    
    # Handler for group messages
    async def trade_opened(self, event):
        """Broadcast when trade is opened"""
        await self.send(text_data=json.dumps({
            'type': 'trade_opened',
            'trade': event['trade']
        }))
    
    async def trade_closed(self, event):
        """Broadcast when trade is closed"""
        await self.send(text_data=json.dumps({
            'type': 'trade_closed',
            'trade': event['trade'],
            'new_balance': event.get('new_balance')
        }))
    
    async def balance_update(self, event):
        """Broadcast balance update"""
        await self.send(text_data=json.dumps({
            'type': 'balance_update',
            'balance': event['balance'],
            'is_demo': event.get('is_demo', False)
        }))


class AdminMonitorConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for admin monitoring dashboard.
    
    Provides real-time updates on:
    - Platform-wide trade activity
    - User statistics
    - Risk metrics
    - System health
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.monitor_task = None
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.user = self.scope.get('user')
        
        # Only allow admin users
        if not self.user or not self.user.is_authenticated or not self.user.is_staff:
            await self.close()
            return
        
        # Join admin monitoring group
        await self.channel_layer.group_add(
            'admin_monitor',
            self.channel_name
        )
        
        await self.accept()
        
        # Start monitoring task
        self.monitor_task = asyncio.create_task(self.stream_metrics())
        
        await self.send(text_data=json.dumps({
            'type': 'connection',
            'status': 'connected',
            'message': 'Admin monitor connected'
        }))
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        if self.monitor_task:
            self.monitor_task.cancel()
        
        await self.channel_layer.group_discard(
            'admin_monitor',
            self.channel_name
        )
    
    async def stream_metrics(self):
        """Stream platform metrics every 5 seconds"""
        try:
            while True:
                metrics = await self.get_platform_metrics()
                
                await self.send(text_data=json.dumps({
                    'type': 'metrics_update',
                    'data': metrics
                }))
                
                await asyncio.sleep(5)
        
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"⚠️ Admin monitor error: {e}")
    
    @database_sync_to_async
    def get_platform_metrics(self):
        """Get platform-wide metrics"""
        from .models import BinaryTrade, UserTradingStats
        from django.db.models import Sum, Count, Avg
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        # Active trades
        active_trades = BinaryTrade.objects.filter(status='active', is_demo=False)
        active_count = active_trades.count()
        active_volume = active_trades.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # Today's trades
        from datetime import datetime, timedelta
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_trades = BinaryTrade.objects.filter(
            opened_at__gte=today_start,
            is_demo=False
        )
        today_count = today_trades.count()
        today_volume = today_trades.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # Win/Loss stats
        won_today = today_trades.filter(status='won').count()
        lost_today = today_trades.filter(status='lost').count()
        
        # Platform profit (sum of all losses minus wins)
        platform_profit = today_trades.filter(status='lost').aggregate(
            total=Sum('amount'))['total'] or Decimal('0')
        platform_payout = today_trades.filter(status='won').aggregate(
            total=Sum('profit_loss'))['total'] or Decimal('0')
        net_profit = platform_profit - abs(platform_payout)
        
        # Active users
        active_users = User.objects.filter(
            binary_trades__opened_at__gte=today_start,
            binary_trades__is_demo=False
        ).distinct().count()
        
        return {
            'active_trades': active_count,
            'active_volume': float(active_volume),
            'today_trades': today_count,
            'today_volume': float(today_volume),
            'won_today': won_today,
            'lost_today': lost_today,
            'platform_profit': float(net_profit),
            'active_users': active_users,
            'timestamp': timezone.now().isoformat()
        }
