from django.urls import path
from . import views, korapay_views, admin_views

app_name = 'transactions'

urlpatterns = [
    # Transaction list and summary
    path('', views.TransactionListView.as_view(), name='transaction-list'),
    path('summary/', views.transaction_summary, name='transaction-summary'),
    
    # Generic endpoints (for frontend compatibility)
    path('deposit/', views.generic_deposit, name='generic-deposit'),
    path('withdraw/', views.generic_withdraw, name='generic-withdraw'),
    
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

# Admin endpoints - separate URL pattern for clarity
admin_urlpatterns = [
    # Deposits
    path('admin/deposits/', admin_views.admin_get_deposits, name='admin-deposits'),
    path('admin/deposits/<int:deposit_id>/approve/', admin_views.admin_approve_deposit, name='admin-approve-deposit'),
    path('admin/deposits/<int:deposit_id>/reject/', admin_views.admin_reject_deposit, name='admin-reject-deposit'),
    
    # Withdrawals
    path('admin/withdrawals/', admin_views.admin_get_withdrawals, name='admin-withdrawals'),
    path('admin/withdrawals/<int:withdrawal_id>/approve/', admin_views.admin_approve_withdrawal, name='admin-approve-withdrawal'),
    path('admin/withdrawals/<int:withdrawal_id>/reject/', admin_views.admin_reject_withdrawal, name='admin-reject-withdrawal'),
    
    # Investments
    path('admin/investments/', admin_views.admin_get_investments, name='admin-investments'),
    
    # Transactions
    path('admin/transactions/', admin_views.admin_get_transactions, name='admin-transactions'),
]

urlpatterns += admin_urlpatterns

