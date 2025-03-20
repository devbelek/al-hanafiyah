from rest_framework import serializers
from .models import Notification, PushSubscription, NotificationSettings


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'notification_type',
                  'is_read', 'created_at', 'url']


class PushSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PushSubscription
        fields = ['id', 'subscription_info', 'browser', 'device', 'created_at']
        read_only_fields = ['id', 'created_at']


class NotificationSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationSettings
        fields = ['push_enabled', 'email_enabled', 'notification_types']