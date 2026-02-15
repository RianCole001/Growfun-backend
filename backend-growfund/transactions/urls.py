from django.urls import path
from . import views, korapay_views

app_name = 'transactions'

urlpatterns = [
    # Transaction list
    path('', views.TransactionListView.as_view(), name='transaction-list'),
    
    # MTN MoMo endpoints
    path('momo/deposit/', views.momo_deposit, name='momo-deposit'),
    path('momo/withdrawal/', views.momo_withdrawal, name='momo-withdrawal'),
    path('momo/status/', views.check_payment_status, name='check-payment-status'),
    path('momo/callback/', views.momo_callback, name='momo-callback'),
    
    # Korapay endpoints
    path('korapay/deposit/', korapay_views.korapay_deposit, name='korapay-deposit'),
    path('korapay/withdrawal/bank/', korapay_views.korapay_withdrawal_bank, name='korapay-withdrawal-bank'),
    path('korapay/withdrawal/mobile/', korapay_views.korapay_withdrawal_mobile, name='korapay-withdrawal-mobile'),
    path('korapay/verify/', korapay_views.korapay_verify_transaction, name='korapay-verify'),
    path('korapay/webhook/', korapay_views.korapay_webhook, name='korapay-webhook'),
    path('korapay/banks/', korapay_views.korapay_get_banks, name='korapay-banks'),
    path('korapay/resolve-account/', korapay_views.korapay_resolve_account, name='korapay-resolve-account'),
]

