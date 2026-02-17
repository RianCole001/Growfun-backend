from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from .models import Notification, AdminNotification
from .serializers import NotificationSerializer

User = get_user_model()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_list(request):
    """Get user notifications with pagination"""
    notifications = Notification.objects.filter(user=request.user)
    
    # Filter by read status if specified
    read_status = request.query_params.get('read')
    if read_status is not None:
        read_bool = read_status.lower() == 'true'
        notifications = notifications.filter(read=read_bool)
    
    # Get unread count
    unread_count = Notification.objects.filter(user=request.user, read=False).count()
    
    # Pagination
    page_size = int(request.query_params.get('page_size', 20))
    page = int(request.query_params.get('page', 1))
    
    paginator = Paginator(notifications, page_size)
    page_obj = paginator.get_page(page)
    
    serializer = NotificationSerializer(page_obj.object_list, many=True)
    
    # Return in the format expected by frontend
    return Response({
        'data': serializer.data,
        'unread_count': unread_count,
        'pagination': {
            'current_page': page,
            'total_pages': paginator.num_pages,
            'total_count': paginator.count,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
        },
        'success': True
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_notification_read(request, notification_id):
    """Mark a notification as read"""
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.read = True
        notification.save()
        
        return Response({
            'data': {'success': True, 'message': 'Notification marked as read'},
            'success': True
        }, status=status.HTTP_200_OK)
    
    except Notification.DoesNotExist:
        return Response({
            'error': {'message': 'Notification not found'},
            'success': False
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_all_read(request):
    """Mark all user notifications as read"""
    count = Notification.objects.filter(user=request.user, read=False).update(read=True)
    
    return Response({
        'data': {
            'success': True,
            'message': f'{count} notifications marked as read'
        }
    }, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_notification(request, notification_id):
    """Delete a notification"""
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.delete()
        
        return Response({
            'data': {'success': True, 'message': 'Notification deleted'}
        }, status=status.HTTP_200_OK)
    
    except Notification.DoesNotExist:
        return Response({
            'error': {'message': 'Notification not found'}
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_stats(request):
    """Get notification statistics"""
    total = Notification.objects.filter(user=request.user).count()
    unread = Notification.objects.filter(user=request.user, read=False).count()
    
    return Response({
        'data': {
            'total_notifications': total,
            'unread_notifications': unread,
            'read_notifications': total - unread
        }
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_welcome_notifications(request):
    """Create welcome notifications for new users (for testing)"""
    # Create welcome notifications
    notifications_data = [
        {
            'title': 'Welcome to GrowFund!',
            'message': 'Welcome to GrowFund! Your account has been successfully created. Start investing and growing your wealth today.',
            'type': 'success'
        },
        {
            'title': 'Complete Your Profile',
            'message': 'Complete your profile to get the most out of GrowFund. Add your personal information and upload a profile picture.',
            'type': 'info'
        },
        {
            'title': 'Verify Your Email',
            'message': 'Please verify your email address to secure your account and enable all features.',
            'type': 'warning'
        },
        {
            'title': 'Start Investing',
            'message': 'Ready to start investing? Check out our investment plans and begin your journey to financial growth.',
            'type': 'info'
        }
    ]
    
    created_notifications = []
    for notif_data in notifications_data:
        notification = Notification.create_notification(
            user=request.user,
            title=notif_data['title'],
            message=notif_data['message'],
            notification_type=notif_data['type']
        )
        created_notifications.append(notification)
    
    serializer = NotificationSerializer(created_notifications, many=True)
    
    return Response({
        'success': True,
        'message': f'Created {len(created_notifications)} welcome notifications',
        'data': serializer.data
    }, status=status.HTTP_201_CREATED)


# ============= ADMIN NOTIFICATION ENDPOINTS =============

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def admin_send_notification(request):
    """Send notification with target filtering (admin only)"""
    if not (request.user.is_staff or request.user.is_superuser):
        return Response({
            'success': False,
            'error': 'Admin access required'
        }, status=status.HTTP_403_FORBIDDEN)
    
    title = request.data.get('title')
    message = request.data.get('message')
    notification_type = request.data.get('type', 'info')
    priority = request.data.get('priority', 'normal')
    target = request.data.get('target', 'all')
    target_users = request.data.get('target_users', '')
    
    if not title or not message:
        return Response({
            'success': False,
            'error': 'Title and message are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Determine target users
    users_to_notify = []
    
    if target == 'all':
        users_to_notify = User.objects.filter(is_active=True)
    elif target == 'verified_users':
        users_to_notify = User.objects.filter(is_active=True, is_verified=True)
    elif target == 'specific_users':
        if not target_users:
            return Response({
                'success': False,
                'error': 'target_users is required when target=specific_users'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Parse comma-separated emails
        emails = [email.strip() for email in target_users.split(',')]
        users_to_notify = User.objects.filter(email__in=emails, is_active=True)
    
    # Create admin notification record
    admin_notification = AdminNotification.objects.create(
        title=title,
        message=message,
        type=notification_type,
        priority=priority,
        target=target,
        target_users=target_users,
        created_by=request.user,
        status='sent'
    )
    
    # Send to each user
    sent_count = 0
    for user in users_to_notify:
        Notification.create_notification(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type
        )
        sent_count += 1
    
    # Update sent count
    admin_notification.sent_count = sent_count
    admin_notification.save()
    
    return Response({
        'data': {
            'id': admin_notification.id,
            'title': admin_notification.title,
            'message': admin_notification.message,
            'type': admin_notification.type,
            'priority': admin_notification.priority,
            'target': admin_notification.target,
            'sent_count': admin_notification.sent_count,
            'created_at': admin_notification.created_at.isoformat(),
            'status': admin_notification.status
        },
        'success': True
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_get_notifications(request):
    """Get all admin-created notifications (admin only)"""
    if not (request.user.is_staff or request.user.is_superuser):
        return Response({
            'success': False,
            'error': 'Admin access required'
        }, status=status.HTTP_403_FORBIDDEN)
    
    notifications = AdminNotification.objects.all()
    
    data = []
    for notif in notifications:
        data.append({
            'id': notif.id,
            'title': notif.title,
            'message': notif.message,
            'type': notif.type,
            'priority': notif.priority,
            'target': notif.target,
            'sent_count': notif.sent_count,
            'created_at': notif.created_at.isoformat(),
            'status': notif.status
        })
    
    return Response({
        'data': data,
        'success': True
    }, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def admin_delete_notification(request, notification_id):
    """Delete an admin notification (admin only)"""
    if not (request.user.is_staff or request.user.is_superuser):
        return Response({
            'success': False,
            'error': 'Admin access required'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        notification = AdminNotification.objects.get(id=notification_id)
        notification.delete()
        
        return Response({
            'data': {'message': 'Notification deleted'},
            'success': True
        }, status=status.HTTP_200_OK)
    
    except AdminNotification.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Notification not found'
        }, status=status.HTTP_404_NOT_FOUND)
