from django.contrib import admin
from .models import OfflineEvent


@admin.register(OfflineEvent)
class OfflineEventAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_date', 'location']
    list_filter = ['event_date']
    search_fields = ['title', 'description', 'location']
    readonly_fields = ['created_at']
    date_hierarchy = 'event_date'
