from django.contrib import admin
from .models import Notification, PushSubscription, NotificationSettings

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['user__username', 'title', 'message']
    date_hierarchy = 'created_at'

@admin.register(PushSubscription)
class PushSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'browser', 'device', 'created_at']
    list_filter = ['browser', 'device']
    search_fields = ['user__username']

@admin.register(NotificationSettings)
class NotificationSettingsAdmin(admin.ModelAdmin):
    list_display = ['user', 'push_enabled', 'email_enabled']
    list_filter = ['push_enabled', 'email_enabled']
    search_fields = ['user__username']