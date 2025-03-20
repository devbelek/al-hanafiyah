from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet, PushSubscriptionViewSet


notification_router = DefaultRouter()
notification_router.register(r'notifications', NotificationViewSet, basename='notification')

push_router = DefaultRouter()
push_router.register(r'notifications/push-subscriptions', PushSubscriptionViewSet, basename='push-subscription')

urlpatterns = [
    path('api/', include(notification_router.urls)),
    path('api/', include(push_router.urls)),
]