"""
WebSocket Consumers for Real-Time Price Streaming
Streams synthetic prices and candles to frontend clients
"""
import json
import asyncio
import time
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .synthetic_price_engine import price_engine_manager, CandleBuilder
from .models import BinaryTrade


class PriceStreamConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for streaming real-time prices
    Sends tick updates and candles to connected clients
    """
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.asset_symbol = self.scope['url_route']['kwargs'].get('asset_symbol', 'GOLD')
        self.room_group_name = f'price_{self.asset_symbol}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send initial historical candles
        await self.send_historical_candles()
        
        # Start price streaming
        asyncio.create_task(self.stream_prices())
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def send_historical_candles(self):
        """Send historical candles for chart initialization"""
        candles = price_engine_manager.get_historical_candles(self.asset_symbol, count=100)
        
        await self.send(text_data=json.dumps({
            'type': 'historical',
            'asset': self.asset_symbol,
            'candles': candles
        }))
    
    @database_sync_to_async
    def get_active_trades(self):
        """Get active trades for house edge calculation"""
        trades = BinaryTrade.objects.filter(
            asset_symbol=self.asset_symbol,
            status='open'
        ).values('direction', 'amount')
        return list(trades)
    
    async def stream_prices(self):
        """Stream real-time prices to client"""
        candle_builder = CandleBuilder()
        last_candle_time = int(time.time())
        
        try:
            while True:
                # Get active trades for house edge
                active_trades = await self.get_active_trades()
                
                # Generate new tick
                price = price_engine_manager.generate_tick(self.asset_symbol, active_trades)
                
                # Update candle builder
                candle_builder.update(price)
                
                # Send tick update
                await self.send(text_data=json.dumps({
                    'type': 'tick',
                    'asset': self.asset_symbol,
                    'price': price,
                    'timestamp': time.time()
                }))
                
                # Check if we should send a candle (every 60 seconds)
                current_time = int(time.time())
                if current_time - last_candle_time >= 60:
                    if candle_builder.has_data():
                        candle = candle_builder.get_candle(current_time)
                        if candle:
                            await self.send(text_data=json.dumps({
                                'type': 'candle',
                                'asset': self.asset_symbol,
                                'data': candle.to_dict()
                            }))
                    last_candle_time = current_time
                
                # Wait before next tick (250ms = 4 ticks per second)
                await asyncio.sleep(0.25)
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"Error in price stream: {e}")
    
    async def receive(self, text_data):
        """Handle messages from client"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'subscribe':
                # Client wants to subscribe to specific asset
                new_asset = data.get('asset', 'GOLD')
                if new_asset != self.asset_symbol:
                    # Leave old room
                    await self.channel_layer.group_discard(
                        self.room_group_name,
                        self.channel_name
                    )
                    
                    # Join new room
                    self.asset_symbol = new_asset
                    self.room_group_name = f'price_{self.asset_symbol}'
                    await self.channel_layer.group_add(
                        self.room_group_name,
                        self.channel_name
                    )
                    
                    # Send historical candles for new asset
                    await self.send_historical_candles()
            
            elif message_type == 'ping':
                # Respond to ping for connection keepalive
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': time.time()
                }))
        
        except json.JSONDecodeError:
            pass


class MultiAssetPriceConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for streaming multiple assets simultaneously
    More efficient for clients that need multiple price feeds
    """
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.subscribed_assets = set()
        self.room_group_name = 'multi_asset_prices'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle messages from client"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'subscribe':
                # Add assets to subscription
                assets = data.get('assets', [])
                self.subscribed_assets.update(assets)
                
                # Send historical candles for each asset
                for asset in assets:
                    candles = price_engine_manager.get_historical_candles(asset, count=100)
                    await self.send(text_data=json.dumps({
                        'type': 'historical',
                        'asset': asset,
                        'candles': candles
                    }))
                
                # Start streaming if not already started
                if not hasattr(self, 'streaming_task'):
                    self.streaming_task = asyncio.create_task(self.stream_prices())
            
            elif message_type == 'unsubscribe':
                # Remove assets from subscription
                assets = data.get('assets', [])
                self.subscribed_assets.difference_update(assets)
            
            elif message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': time.time()
                }))
        
        except json.JSONDecodeError:
            pass
    
    @database_sync_to_async
    def get_active_trades_for_assets(self, assets):
        """Get active trades for multiple assets"""
        trades_by_asset = {}
        for asset in assets:
            trades = BinaryTrade.objects.filter(
                asset_symbol=asset,
                status='open'
            ).values('direction', 'amount')
            trades_by_asset[asset] = list(trades)
        return trades_by_asset
    
    async def stream_prices(self):
        """Stream prices for all subscribed assets"""
        candle_builders = {}
        last_candle_times = {}
        
        try:
            while True:
                if not self.subscribed_assets:
                    await asyncio.sleep(1)
                    continue
                
                # Get active trades for house edge
                trades_by_asset = await self.get_active_trades_for_assets(self.subscribed_assets)
                
                # Generate ticks for each subscribed asset
                for asset in list(self.subscribed_assets):
                    # Initialize candle builder if needed
                    if asset not in candle_builders:
                        candle_builders[asset] = CandleBuilder()
                        last_candle_times[asset] = int(time.time())
                    
                    # Generate tick
                    active_trades = trades_by_asset.get(asset, [])
                    price = price_engine_manager.generate_tick(asset, active_trades)
                    
                    # Update candle
                    candle_builders[asset].update(price)
                    
                    # Send tick
                    await self.send(text_data=json.dumps({
                        'type': 'tick',
                        'asset': asset,
                        'price': price,
                        'timestamp': time.time()
                    }))
                    
                    # Check for candle completion
                    current_time = int(time.time())
                    if current_time - last_candle_times[asset] >= 60:
                        if candle_builders[asset].has_data():
                            candle = candle_builders[asset].get_candle(current_time)
                            if candle:
                                await self.send(text_data=json.dumps({
                                    'type': 'candle',
                                    'asset': asset,
                                    'data': candle.to_dict()
                                }))
                        last_candle_times[asset] = current_time
                
                # Wait before next tick batch
                await asyncio.sleep(0.25)
        
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"Error in multi-asset price stream: {e}")
