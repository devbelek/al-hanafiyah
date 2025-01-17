from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import OfflineEventViewSet

router = DefaultRouter()
router.register(r'events', OfflineEventViewSet)

urlpatterns = [
    path('', include(router.urls)),
]