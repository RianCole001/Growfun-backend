from django.urls import path
from . import views

app_name = 'demo'

urlpatterns = [
    path('account/', views.demo_account, name='demo-account'),
    path('balance/', views.demo_balance, name='demo-balance'),
    path('deposit/', views.demo_deposit, name='demo-deposit'),
    path('withdraw/', views.demo_withdraw, name='demo-withdraw'),
    path('crypto/buy/', views.demo_buy_crypto, name='demo-buy-crypto'),
    path('crypto/sell/', views.demo_sell_crypto, name='demo-sell-crypto'),
    path('invest/', views.demo_invest, name='demo-invest'),
    path('investments/', views.demo_investments, name='demo-investments'),
    path('transactions/', views.demo_transactions, name='demo-transactions'),
]