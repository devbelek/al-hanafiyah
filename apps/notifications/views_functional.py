from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Notification, PushSubscription, NotificationSettings
from .serializers import NotificationSerializer, PushSubscriptionSerializer, NotificationSettingsSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_list(request):
    notifications = Notification.objects.filter(user=request.user)
    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_detail(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    serializer = NotificationSerializer(notification)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_as_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    return Response({'status': 'success'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_all_as_read(request):
    Notification.objects.filter(user=request.user).update(is_read=True)
    return Response({'status': 'success'})


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def notification_settings(request):
    settings, created = NotificationSettings.objects.get_or_create(user=request.user)

    if request.method == 'GET':
        serializer = NotificationSettingsSerializer(settings)
        return Response(serializer.data)

    serializer = NotificationSettingsSerializer(settings, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def push_subscription_list_create(request):
    if request.method == 'GET':
        subscriptions = PushSubscription.objects.filter(user=request.user)
        serializer = PushSubscriptionSerializer(subscriptions, many=True)
        return Response(serializer.data)

    serializer = PushSubscriptionSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def push_subscription_delete(request, pk):
    subscription = get_object_or_404(PushSubscription, pk=pk, user=request.user)
    subscription.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)