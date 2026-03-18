from django.urls import path
from . import views

app_name = 'demo'

urlpatterns = [
    # Account
    path('account/', views.demo_account, name='demo-account'),
    path('balance/', views.demo_balance, name='demo-balance'),
    path('deposit/', views.demo_deposit, name='demo-deposit'),

    # Crypto
    path('crypto/buy/', views.demo_buy_crypto, name='demo-buy-crypto'),
    path('crypto/sell/', views.demo_sell_crypto, name='demo-sell-crypto'),

    # Capital Plans
    path('capital-plan/', views.demo_invest_capital_plan, name='demo-capital-plan'),

    # Real Estate
    path('real-estate/', views.demo_invest_real_estate, name='demo-real-estate'),

    # Generic invest (backward compat)
    path('invest/', views.demo_invest, name='demo-invest'),

    # Portfolio & History
    path('investments/', views.demo_investments, name='demo-investments'),
    path('portfolio/', views.demo_portfolio, name='demo-portfolio'),
    path('transactions/', views.demo_transactions, name='demo-transactions'),
]
