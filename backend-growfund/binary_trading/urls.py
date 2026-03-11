from django.urls import path
from . import views

app_name = 'binary_trading'

urlpatterns = [
    # Assets
    path('assets/', views.get_assets, name='get-assets'),
    path('assets/<str:symbol>/price/', views.get_asset_price, name='get-asset-price'),
    path('prices/', views.get_all_prices, name='get-all-prices'),
    
    # Trading
    path('trades/open/', views.open_trade, name='open-trade'),
    path('trades/active/', views.get_active_trades, name='active-trades'),
    path('trades/history/', views.get_trade_history, name='trade-history'),
    
    # Balances
    path('balances/', views.get_balances, name='get-balances'),
    
    # Stats
    path('stats/', views.get_user_stats, name='user-stats'),
    
    # Admin
    path('admin/close-expired/', views.close_expired_trades, name='close-expired'),
]
