from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.db import transaction
from .models import UserProfile
from .serializers import UserSerializer, GoogleAuthSerializer
from apps.lessons.models import LessonProgress
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class AccountViewSet(viewsets.GenericViewSet):
    """
    API для управления аккаунтом пользователя.
    """
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Авторизация через Google OAuth",
        request_body=GoogleAuthSerializer,
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'token': openapi.Schema(type=openapi.TYPE_STRING),
                    'user': openapi.Schema(type=openapi.TYPE_OBJECT),
                    'profile_complete': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'created': openapi.Schema(type=openapi.TYPE_BOOLEAN)
                }
            ),
            400: "Неверный формат запроса или недействительный токен"
        }
    )
    @action(detail=False, methods=['post'])
    def google_auth(self, request):
        """
        Авторизация или регистрация пользователя через Google OAuth
        """
        serializer = GoogleAuthSerializer(data=request.data)
        if serializer.is_valid():
            user_data = serializer.validated_data['user_data']

            user, created = User.objects.get_or_create(
                email=user_data['email'],
                defaults={
                    'username': user_data['username'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                }
            )

            if not created and user.username != user_data['username']:
                user.first_name = user_data['first_name']
                user.last_name = user_data['last_name']
                user.save()

            token, _ = Token.objects.get_or_create(user=user)
            profile_complete = bool(user.profile.telegram)

            return Response({
                'token': token.key,
                'user': UserSerializer(user).data,
                'profile_complete': profile_complete,
                'created': created
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        method='get',
        operation_description="Получение данных текущего пользователя",
        responses={
            200: UserSerializer(),
            401: "Необходима авторизация"
        }
    )
    @swagger_auto_schema(
        method='put',
        operation_description="Обновление данных текущего пользователя",
        request_body=UserSerializer,
        responses={
            200: UserSerializer(),
            400: "Некорректные данные",
            401: "Необходима авторизация"
        }
    )
    @swagger_auto_schema(
        method='patch',
        operation_description="Частичное обновление данных текущего пользователя",
        request_body=UserSerializer,
        responses={
            200: UserSerializer(),
            400: "Некорректные данные",
            401: "Необходима авторизация"
        }
    )
    @action(detail=False, methods=['get', 'put', 'patch'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """
        Получение и обновление данных текущего пользователя
        """
        if getattr(self, 'swagger_fake_view', False):
            return Response({})

        user = request.user

        if request.method == 'GET':
            serializer = UserSerializer(user)
            return Response(serializer.data)

        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Получение истории просмотра уроков",
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'lesson_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'lesson_slug': openapi.Schema(type=openapi.TYPE_STRING),
                        'module_name': openapi.Schema(type=openapi.TYPE_STRING),
                        'topic_name': openapi.Schema(type=openapi.TYPE_STRING),
                        'timestamp': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'last_viewed': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                        'duration_watched': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            401: "Необходима авторизация"
        }
    )
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def viewing_history(self, request):
        """
        Получение истории просмотра уроков пользователя
        """
        if getattr(self, 'swagger_fake_view', False):
            return Response([])

        progress = LessonProgress.objects.filter(user=request.user).order_by('-last_viewed')[:20]

        history = []
        for item in progress:
            history.append({
                'lesson_id': item.lesson.id,
                'lesson_slug': item.lesson.slug,
                'module_name': item.lesson.module.name,
                'topic_name': item.lesson.module.topic.name,
                'timestamp': item.timestamp,
                'last_viewed': item.last_viewed,
                'duration_watched': f"{item.timestamp // 60}:{item.timestamp % 60:02d}"
            })

        return Response(history)

    @swagger_auto_schema(
        operation_description="Проверка статуса Telegram-аккаунта",
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'telegram': openapi.Schema(type=openapi.TYPE_STRING),
                    'is_activated': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'last_activity': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME,
                                                    nullable=True)
                }
            ),
            401: "Необходима авторизация"
        }
    )
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def telegram_status(self, request):
        """
        Проверка статуса активации Telegram-аккаунта пользователя
        """
        # Добавить проверку для Swagger
        if getattr(self, 'swagger_fake_view', False):
            return Response({
                'telegram': '',
                'is_activated': False,
                'last_activity': None
            })

        user = request.user

        # Логика определения активации и последней активности
        is_activated = False
        last_activity = None

        if user.profile.telegram_id:
            is_activated = True
            # Здесь можно добавить логику получения last_activity

        return Response({
            'telegram': user.profile.telegram,
            'is_activated': is_activated,
            'last_activity': last_activity
        })

    @swagger_auto_schema(
        operation_description="Обновление аватара пользователя",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'avatar': openapi.Schema(type=openapi.TYPE_FILE)
            },
            required=['avatar']
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'avatar': openapi.Schema(type=openapi.TYPE_STRING)
                }
            ),
            400: "Некорректный формат файла",
            401: "Необходима авторизация"
        }
    )
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def update_avatar(self, request):
        """
        Обновление аватара пользователя
        """
        if 'avatar' not in request.FILES:
            return Response({'error': 'Не указан файл аватара'}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        user.profile.avatar = request.FILES['avatar']
        user.profile.save()

        return Response({'avatar': user.profile.avatar.url if user.profile.avatar else None})

    @swagger_auto_schema(
        operation_description="Получение общего прогресса обучения",
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'total_lessons': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'completed_lessons': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'progress_percentage': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'by_category': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'category_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'category_name': openapi.Schema(type=openapi.TYPE_STRING),
                                'total_lessons': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'completed_lessons': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'progress_percentage': openapi.Schema(type=openapi.TYPE_INTEGER)
                            }
                        )
                    ),
                    'recently_completed': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'lesson_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'lesson_slug': openapi.Schema(type=openapi.TYPE_STRING),
                                'title': openapi.Schema(type=openapi.TYPE_STRING),
                                'completed_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME)
                            }
                        )
                    )
                }
            ),
            401: "Необходима авторизация"
        }
    )
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def learning_progress(self, request):
        """
        Получение общего прогресса обучения пользователя
        """
        if getattr(self, 'swagger_fake_view', False):
            return Response({
                'total_lessons': 0,
                'completed_lessons': 0,
                'progress_percentage': 0,
                'by_category': [],
                'recently_completed': []
            })