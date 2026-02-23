from django.urls import path
from .views import PlatformSettingsView, SettingsHistoryView, PublicSettingsView

app_name = 'settings_app'

urlpatterns = [
    # Public endpoint
    path('public/', PublicSettingsView.as_view(), name='public-settings'),
    
    # Admin endpoints  
    path('admin/settings/', PlatformSettingsView.as_view(), name='admin-settings'),
    path('admin/settings/history/', SettingsHistoryView.as_view(), name='settings-history'),
]
