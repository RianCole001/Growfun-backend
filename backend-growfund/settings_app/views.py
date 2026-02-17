from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db import transaction as db_transaction

from .models import PlatformSettings, SettingsHistory
from .serializers import PlatformSettingsSerializer, SettingsHistorySerializer


class PlatformSettingsView(APIView):
    """
    Get and update platform settings (admin only)
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        """Get current platform settings"""
        settings = PlatformSettings.get_settings()
        serializer = PlatformSettingsSerializer(settings)
        
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    def put(self, request):
        """Update platform settings"""
        settings = PlatformSettings.get_settings()
        
        # Store old values for history
        old_data = PlatformSettingsSerializer(settings).data
        
        serializer = PlatformSettingsSerializer(
            settings, 
            data=request.data, 
            partial=True
        )
        
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        with db_transaction.atomic():
            # Save settings
            updated_settings = serializer.save(updated_by=request.user)
            
            # Log changes to history
            new_data = serializer.data
            for field in new_data:
                if field in old_data and old_data[field] != new_data[field]:
                    SettingsHistory.objects.create(
                        setting_name=field,
                        old_value=str(old_data[field]),
                        new_value=str(new_data[field]),
                        changed_by=request.user
                    )
            
            # Create notification for admin
            try:
                from notifications.models import Notification
                Notification.create_notification(
                    user=request.user,
                    title='Platform Settings Updated',
                    message='Platform settings have been successfully updated',
                    notification_type='info'
                )
            except Exception as e:
                print(f"Warning: Could not create notification: {e}")
        
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Settings updated successfully'
        }, status=status.HTTP_200_OK)


class SettingsHistoryView(APIView):
    """
    Get settings change history (admin only)
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        """Get settings change history"""
        history = SettingsHistory.objects.all()[:50]  # Last 50 changes
        serializer = SettingsHistorySerializer(history, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)


class PublicSettingsView(APIView):
    """
    Get public platform settings (no authentication required)
    Used for maintenance mode check, platform name, etc.
    """
    permission_classes = []
    
    def get(self, request):
        """Get public platform settings"""
        settings = PlatformSettings.get_settings()
        
        return Response({
            'success': True,
            'data': {
                'platformName': settings.platform_name,
                'platformEmail': settings.platform_email,
                'maintenanceMode': settings.maintenance_mode,
                'minDeposit': str(settings.min_deposit),
                'maxDeposit': str(settings.max_deposit),
                'minWithdrawal': str(settings.min_withdrawal),
                'maxWithdrawal': str(settings.max_withdrawal),
                'depositFee': str(settings.deposit_fee),
                'withdrawalFee': str(settings.withdrawal_fee),
                'referralBonus': str(settings.referral_bonus)
            }
        }, status=status.HTTP_200_OK)
