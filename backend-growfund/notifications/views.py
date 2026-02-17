from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.paginator import Paginator
from .models import Notification
from .serializers import NotificationSerializer


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
    
    # Pagination
    page_size = int(request.query_params.get('page_size', 20))
    page = int(request.query_params.get('page', 1))
    
    paginator = Paginator(notifications, page_size)
    page_obj = paginator.get_page(page)
    
    serializer = NotificationSerializer(page_obj.object_list, many=True)
    
    return Response({
        'data': serializer.data,
        'pagination': {
            'current_page': page,
            'total_pages': paginator.num_pages,
            'total_count': paginator.count,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
        }
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
            'data': {'success': True, 'message': 'Notification marked as read'}
        }, status=status.HTTP_200_OK)
    
    except Notification.DoesNotExist:
        return Response({
            'error': {'message': 'Notification not found'}
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