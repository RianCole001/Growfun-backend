from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notifications"""
    
    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'message', 'type', 'read', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class CreateNotificationSerializer(serializers.ModelSerializer):
    """Serializer for creating notifications"""
    
    class Meta:
        model = Notification
        fields = ['title', 'message', 'type']
        
    def create(self, validated_data):
        user = self.context['request'].user
        return Notification.objects.create(user=user, **validated_data)