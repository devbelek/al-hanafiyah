from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet, PushSubscriptionViewSet

router = DefaultRouter()
router.register(r'', NotificationViewSet, basename='notifications')
router.register(r'push-subscriptions', PushSubscriptionViewSet, basename='push-subscriptions')

urlpatterns = [
    path('', include(router.urls)),
]