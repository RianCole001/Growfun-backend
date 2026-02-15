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
    
    # Admin endpoints - Deposits
    path('admin/deposits/', views.admin_deposits_list, name='admin-deposits-list'),
    path('admin/deposits/<int:transaction_id>/approve/', views.admin_approve_deposit, name='admin-approve-deposit'),
    path('admin/deposits/<int:transaction_id>/reject/', views.admin_reject_deposit, name='admin-reject-deposit'),
    
    # Admin endpoints - Withdrawals
    path('admin/withdrawals/', views.admin_withdrawals_list, name='admin-withdrawals-list'),
    path('admin/withdrawals/<int:transaction_id>/process/', views.admin_process_withdrawal, name='admin-process-withdrawal'),
    path('admin/withdrawals/<int:transaction_id>/complete/', views.admin_complete_withdrawal, name='admin-complete-withdrawal'),
    path('admin/withdrawals/<int:transaction_id>/reject/', views.admin_reject_withdrawal, name='admin-reject-withdrawal'),
    
    # Admin endpoints - Stats
    path('admin/stats/', views.admin_transaction_stats, name='admin-transaction-stats'),
]

