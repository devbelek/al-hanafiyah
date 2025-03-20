from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Notification, PushSubscription, NotificationSettings
from .serializers import NotificationSerializer, PushSubscriptionSerializer, NotificationSettingsSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API для управления уведомлениями пользователя.
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Notification.objects.none()
        return Notification.objects.filter(user=self.request.user)

    @swagger_auto_schema(
        operation_description="Получение списка всех уведомлений пользователя",
        responses={
            200: openapi.Response(
                description="Список уведомлений",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'title': openapi.Schema(type=openapi.TYPE_STRING),
                            'message': openapi.Schema(type=openapi.TYPE_STRING),
                            'notification_type': openapi.Schema(type=openapi.TYPE_STRING),
                            'is_read': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                            'url': openapi.Schema(type=openapi.TYPE_STRING)
                        }
                    )
                )
            ),
            401: "Необходима авторизация"
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Получение детальной информации об уведомлении",
        responses={
            200: openapi.Response(
                description="Детальная информация об уведомлении",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'title': openapi.Schema(type=openapi.TYPE_STRING),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'notification_type': openapi.Schema(type=openapi.TYPE_STRING),
                        'is_read': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                        'url': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            401: "Необходима авторизация",
            404: "Уведомление не найдено"
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Отметить уведомление как прочитанное",
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING, example='success')
                }
            ),
            401: "Необходима авторизация",
            404: "Уведомление не найдено"
        }
    )
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """
        Отметить уведомление как прочитанное
        """
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'success'})

    @swagger_auto_schema(
        operation_description="Отметить все уведомления пользователя как прочитанные",
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING, example='success')
                }
            ),
            401: "Необходима авторизация"
        }
    )
    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """
        Отметить все уведомления пользователя как прочитанные
        """
        self.get_queryset().update(is_read=True)
        return Response({'status': 'success'})

    @swagger_auto_schema(
        method='get',
        operation_description="Получение настроек уведомлений пользователя",
        responses={
            200: NotificationSettingsSerializer(),
            401: "Необходима авторизация"
        }
    )
    @swagger_auto_schema(
        method='put',
        operation_description="Обновление настроек уведомлений пользователя",
        request_body=NotificationSettingsSerializer,
        responses={
            200: NotificationSettingsSerializer(),
            400: "Некорректные данные",
            401: "Необходима авторизация"
        }
    )
    @action(detail=False, methods=['get', 'put'], url_path='settings')
    def settings(self, request):
        """
        Получение и обновление настроек уведомлений пользователя
        """
        settings, created = NotificationSettings.objects.get_or_create(user=request.user)

        if request.method == 'GET':
            serializer = NotificationSettingsSerializer(settings)
            return Response(serializer.data)

        # PUT метод
        serializer = NotificationSettingsSerializer(settings, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PushSubscriptionViewSet(viewsets.ModelViewSet):
    """
    API для управления push-подписками.
    """
    serializer_class = PushSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'delete']  # Явно определяем поддерживаемые методы

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return PushSubscription.objects.none()
        return PushSubscription.objects.filter(user=self.request.user)

    @swagger_auto_schema(
        operation_description="Получение списка push-подписок пользователя",
        responses={
            200: openapi.Response(
                description="Список push-подписок",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'subscription_info': openapi.Schema(type=openapi.TYPE_OBJECT),
                            'browser': openapi.Schema(type=openapi.TYPE_STRING),
                            'device': openapi.Schema(type=openapi.TYPE_STRING),
                            'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME)
                        }
                    )
                )
            ),
            401: "Необходима авторизация"
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Создание новой push-подписки",
        request_body=PushSubscriptionSerializer,
        responses={
            201: openapi.Response(
                description="Созданная push-подписка",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'subscription_info': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'browser': openapi.Schema(type=openapi.TYPE_STRING),
                        'device': openapi.Schema(type=openapi.TYPE_STRING),
                        'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME)
                    }
                )
            ),
            400: "Некорректные данные",
            401: "Необходима авторизация"
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Удаление push-подписки",
        responses={
            204: "Подписка успешно удалена",
            401: "Необходима авторизация",
            404: "Подписка не найдена"
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)