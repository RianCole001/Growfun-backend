from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    # User endpoints
    path('', views.notification_list, name='notification-list'),
    path('<int:notification_id>/read/', views.mark_notification_read, name='mark-read'),
    path('mark-all-read/', views.mark_all_read, name='mark-all-read'),
    path('<int:notification_id>/delete/', views.delete_notification, name='delete-notification'),
    path('stats/', views.notification_stats, name='notification-stats'),
    path('create-welcome/', views.create_welcome_notifications, name='create-welcome'),
    
    # Admin endpoints
    path('admin/send/', views.admin_send_notification, name='admin-send-notification'),
    path('admin/notifications/', views.admin_get_notifications, name='admin-get-notifications'),
    path('admin/notifications/<int:notification_id>/', views.admin_delete_notification, name='admin-delete-notification'),
]
