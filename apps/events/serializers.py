from rest_framework import serializers
from .models import OfflineEvent


class OfflineEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfflineEvent
        fields = [
            'id', 'title', 'description', 'event_date',
            'location', 'created_at',
        ]
        read_only_fields = ['created_at']
