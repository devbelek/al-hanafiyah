from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import OfflineEvent
from .serializers import OfflineEventSerializer


class OfflineEventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OfflineEvent.objects.filter(
        event_date__gte=timezone.now()
    )
    serializer_class = OfflineEventSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['title', 'description', 'location']

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        upcoming_events = self.get_queryset().order_by('event_date')[:5]
        serializer = self.get_serializer(upcoming_events, many=True)
        return Response(serializer.data)
