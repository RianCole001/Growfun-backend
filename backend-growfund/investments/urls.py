from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TradeViewSet, CapitalInvestmentPlanViewSet, crypto_buy, crypto_sell, crypto_prices, user_crypto_portfolio

app_name = 'investments'

router = DefaultRouter()
router.register(r'trades', TradeViewSet, basename='trade')
router.register(r'investment-plans', CapitalInvestmentPlanViewSet, basename='investment-plan')

urlpatterns = [
    path('', include(router.urls)),
    
    # Crypto-specific endpoints
    path('crypto/buy/', crypto_buy, name='crypto-buy'),
    path('crypto/sell/', crypto_sell, name='crypto-sell'),
    path('crypto/prices/', crypto_prices, name='crypto-prices'),
    path('crypto/portfolio/', user_crypto_portfolio, name='crypto-portfolio'),
]
