from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TradeViewSet, CapitalInvestmentPlanViewSet, crypto_buy, crypto_sell, crypto_prices, user_crypto_portfolio
from .admin_crypto_views import (
    admin_get_crypto_prices, admin_update_crypto_price,
    admin_toggle_crypto_active, admin_get_price_history,
    admin_bulk_update_prices
)

app_name = 'investments'

router = DefaultRouter()
router.register(r'trades', TradeViewSet, basename='trade')
router.register(r'investment-plans', CapitalInvestmentPlanViewSet, basename='investment-plan')

urlpatterns = [
    path('', include(router.urls)),
    
    # Crypto-specific endpoints (users)
    path('crypto/buy/', crypto_buy, name='crypto-buy'),
    path('crypto/sell/', crypto_sell, name='crypto-sell'),
    path('crypto/prices/', crypto_prices, name='crypto-prices'),
    path('crypto/portfolio/', user_crypto_portfolio, name='crypto-portfolio'),
    
    # Admin crypto price management
    path('admin/crypto-prices/', admin_get_crypto_prices, name='admin-crypto-prices'),
    path('admin/crypto-prices/update/', admin_update_crypto_price, name='admin-update-crypto-price'),
    path('admin/crypto-prices/bulk-update/', admin_bulk_update_prices, name='admin-bulk-update-prices'),
    path('admin/crypto-prices/<str:coin>/toggle/', admin_toggle_crypto_active, name='admin-toggle-crypto'),
    path('admin/crypto-prices/<str:coin>/history/', admin_get_price_history, name='admin-price-history'),
]
