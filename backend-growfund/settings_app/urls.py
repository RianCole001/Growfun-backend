from django.urls import path
from .views import PlatformSettingsView, SettingsHistoryView, PublicSettingsView

app_name = 'settings_app'

urlpatterns = [
    # Admin endpoints
    path('admin/settings/', PlatformSettingsView.as_view(), name='admin-settings'),
    path('admin/settings/history/', SettingsHistoryView.as_view(), name='settings-history'),
    
    # Public endpoint
    path('settings/public/', PublicSettingsView.as_view(), name='public-settings'),
]
