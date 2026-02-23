"""
URL configuration for growfund project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/investments/', include('investments.urls')),
    path('api/crypto/', include('investments.urls')),  # Alias for crypto endpoints
    path('api/transactions/', include('transactions.urls')),
    path('api/admin/deposits/', include('transactions.urls')),  # Admin deposits
    path('api/admin/withdrawals/', include('transactions.urls')),  # Admin withdrawals
    path('api/admin/investments/', include('transactions.urls')),  # Admin investments
    path('api/admin/transactions/', include('transactions.urls')),  # Admin transactions
    path('api/referrals/', include('referrals.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/demo/', include('demo.urls')),  # Demo trading system
    path('api/settings/', include('settings_app.urls')),  # Platform settings
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Customize admin site
admin.site.site_header = 'GrowFund Administration'
admin.site.site_title = 'GrowFund Admin'
admin.site.index_title = 'Welcome to GrowFund Admin Portal'
