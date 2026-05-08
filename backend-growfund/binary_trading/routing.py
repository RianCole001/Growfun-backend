"""
WebSocket URL routing for binary trading
"""
from django.urls import path
from . import consumers
from .price_consumers import PriceStreamConsumer, MultiAssetPriceConsumer

websocket_urlpatterns = [
    # Synthetic price streaming WebSocket (single asset)
    path('ws/binary-trading/price/<str:asset_symbol>/', PriceStreamConsumer.as_asgi()),
    
    # Multi-asset price streaming WebSocket
    path('ws/binary-trading/prices/multi/', MultiAssetPriceConsumer.as_asgi()),
    
    # Legacy price streaming WebSocket
    path('ws/binary-trading/prices/', consumers.PriceStreamConsumer.as_asgi()),
    
    # Trade updates WebSocket
    path('ws/binary-trading/trades/', consumers.TradeUpdatesConsumer.as_asgi()),
    
    # Admin monitoring WebSocket
    path('ws/binary-trading/admin/monitor/', consumers.AdminMonitorConsumer.as_asgi()),
]
