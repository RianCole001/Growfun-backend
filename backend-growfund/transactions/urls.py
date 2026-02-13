from django.urls import path
from . import views

app_name = 'transactions'

urlpatterns = [
    path('', views.TransactionListView.as_view(), name='transaction-list'),
    path('momo/deposit/', views.momo_deposit, name='momo-deposit'),
    path('momo/withdrawal/', views.momo_withdrawal, name='momo-withdrawal'),
    path('momo/status/', views.check_payment_status, name='check-payment-status'),
    path('momo/callback/', views.momo_callback, name='momo-callback'),
]

