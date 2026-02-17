from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notification_list, name='notification-list'),
    path('<int:notification_id>/read/', views.mark_notification_read, name='mark-read'),
    path('mark-all-read/', views.mark_all_read, name='mark-all-read'),
    path('<int:notification_id>/delete/', views.delete_notification, name='delete-notification'),
    path('stats/', views.notification_stats, name='notification-stats'),
]
