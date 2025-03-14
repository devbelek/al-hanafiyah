from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Topic, Module, Lesson, Comment, UstazProfile, LessonProgress, CommentLike
from .serializers import (
    CategorySerializer, TopicSerializer, ModuleSerializer,
    LessonSerializer, CommentSerializer, UstazProfileSerializer
)
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class UstazProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Профиль устаза (преподавателя).
    """
    queryset = UstazProfile.objects.all()
    serializer_class = UstazProfileSerializer

    @swagger_auto_schema(
        operation_description="Получение информации о профиле устаза",
        responses={200: UstazProfileSerializer()}
    )
    def list(self, request):
        profile = UstazProfile.objects.first()
        serializer = self.get_serializer(profile)
        return Response(serializer.data)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Категории образовательного контента.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    @swagger_auto_schema(
        operation_description="Получение списка всех категорий",
        manual_parameters=[
            openapi.Parameter(
                'search',
                openapi.IN_QUERY,
                description="Поиск по названию категории",
                type=openapi.TYPE_STRING
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Получение информации о конкретной категории",
        responses={
            200: CategorySerializer(),
            404: "Категория не найдена"
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class TopicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Темы в рамках категорий.
    """
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category']
    search_fields = ['name']

    @swagger_auto_schema(
        operation_description="Получение списка всех тем",
        manual_parameters=[
            openapi.Parameter(
                'category',
                openapi.IN_QUERY,
                description="Фильтр по ID категории",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'search',
                openapi.IN_QUERY,
                description="Поиск по названию темы",
                type=openapi.TYPE_STRING
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Получение информации о конкретной теме",
        responses={
            200: TopicSerializer(),
            404: "Тема не найдена"
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class ModuleViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Модули в рамках тем.
    """
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['topic']
    search_fields = ['name']

    @swagger_auto_schema(
        operation_description="Получение списка всех модулей",
        manual_parameters=[
            openapi.Parameter(
                'topic',
                openapi.IN_QUERY,
                description="Фильтр по ID темы",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'search',
                openapi.IN_QUERY,
                description="Поиск по названию модуля",
                type=openapi.TYPE_STRING
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Получение информации о конкретном модуле",
        responses={
            200: ModuleSerializer(),
            404: "Модуль не найден"
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Изменение порядка модулей",
        request_body=openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID модуля'),
                    'order': openapi.Schema(type=openapi.TYPE_INTEGER, description='Порядковый номер')
                },
                required=['id', 'order']
            )
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING, example='success')
                }
            )
        }
    )
    @action(detail=False, methods=['post'])
    def reorder(self, request):
        """
        Изменение порядка модулей.
        """
        for item in request.data:
            Module.objects.filter(id=item['id']).update(order=item['order'])
        return Response({'status': 'success'})


class LessonViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Уроки в рамках модулей.
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['module', 'media_type', 'is_intro']
    search_fields = ['module__name']

    @swagger_auto_schema(
        operation_description="Получение списка всех уроков",
        manual_parameters=[
            openapi.Parameter(
                'module',
                openapi.IN_QUERY,
                description="Фильтр по ID модуля",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'media_type',
                openapi.IN_QUERY,
                description="Фильтр по типу медиа (video, audio)",
                type=openapi.TYPE_STRING,
                enum=['video', 'audio']
            ),
            openapi.Parameter(
                'is_intro',
                openapi.IN_QUERY,
                description="Фильтр по вводным урокам",
                type=openapi.TYPE_BOOLEAN
            ),
            openapi.Parameter(
                'search',
                openapi.IN_QUERY,
                description="Поиск по названию модуля",
                type=openapi.TYPE_STRING
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Получение информации о конкретном уроке",
        responses={
            200: LessonSerializer(),
            404: "Урок не найден"
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Добавление комментария к уроку",
        request_body=CommentSerializer,
        responses={
            201: CommentSerializer(),
            400: "Некорректные данные",
            401: "Необходима авторизация"
        }
    )
    @action(detail=True, methods=['post'])
    def add_comment(self, request, slug=None):
        """
        Добавление комментария к уроку.
        """
        lesson = self.get_object()
        serializer = CommentSerializer(data=request.data)

        if not request.user.is_authenticated:
            return Response(
                {'error': 'Авторизуйтесь для добавления комментария'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if serializer.is_valid():
            comment = serializer.save(
                lesson=lesson,
                user=request.user,
                telegram=request.user.profile.telegram or ''
            )
            parent_id = request.data.get('parent')
            if parent_id:
                try:
                    parent_comment = Comment.objects.get(id=parent_id)
                    if parent_comment.user and parent_comment.user != request.user:
                        from apps.notifications.services import create_notification
                        create_notification(
                            user=parent_comment.user,
                            title='Ответ на ваш комментарий',
                            message=f'{request.user.username} ответил: {comment.content[:100]}',
                            notification_type='comment_reply',
                            content_object=comment,
                            url=f'/lessons/{lesson.slug}?comment={comment.id}'
                        )
                except Comment.DoesNotExist:
                    pass

            return Response(
                CommentSerializer(comment, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Лайк/анлайк комментария к уроку",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'comment_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID комментария')
            },
            required=['comment_id']
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING, example='success'),
                    'action': openapi.Schema(type=openapi.TYPE_STRING, enum=['liked', 'unliked']),
                    'like_count': openapi.Schema(type=openapi.TYPE_INTEGER)
                }
            ),
            401: "Необходима авторизация",
            404: "Комментарий не найден"
        }
    )
    @action(detail=True, methods=['post'])
    def like_comment(self, request, slug=None):
        """
        Лайк/анлайк комментария к уроку.
        """
        comment_id = request.data.get('comment_id')

        if not request.user.is_authenticated:
            return Response(
                {'error': 'Авторизуйтесь для оценки комментария'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            comment = Comment.objects.get(id=comment_id, lesson=self.get_object())

            like, created = CommentLike.objects.get_or_create(
                comment=comment,
                user=request.user
            )

            if not created:
                like.delete()
                action = 'unliked'
            else:
                action = 'liked'

            return Response({
                'status': 'success',
                'action': action,
                'like_count': comment.likes.count()
            })
        except Comment.DoesNotExist:
            return Response(
                {'error': 'Комментарий не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

    @swagger_auto_schema(
        operation_description="Изменение порядка уроков в модуле",
        request_body=openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID урока'),
                    'order': openapi.Schema(type=openapi.TYPE_INTEGER, description='Порядковый номер')
                },
                required=['id', 'order']
            )
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING, example='success')
                }
            )
        }
    )
    @action(detail=False, methods=['post'])
    def reorder(self, request):
        """
        Изменение порядка уроков в модуле.
        Принимает массив: [{"id": 1, "order": 1}, {"id": 2, "order": 2}]
        """
        for item in request.data:
            Lesson.objects.filter(id=item['id']).update(order=item['order'])
        return Response({'status': 'success'})

    @swagger_auto_schema(
        operation_description="Сохранение прогресса просмотра урока",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'timestamp': openapi.Schema(type=openapi.TYPE_INTEGER, description='Временная метка в секундах')
            },
            required=['timestamp']
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING, example='success')
                }
            ),
            400: "Некорректные данные",
            401: "Необходима авторизация"
        }
    )
    @action(detail=True, methods=['post'])
    def save_progress(self, request, slug=None):
        """
        Сохранение прогресса просмотра урока.
        """
        lesson = self.get_object()
        timestamp = request.data.get('timestamp')

        if not request.user.is_authenticated:
            return Response(
                {'error': 'Авторизуйтесь для сохранения прогресса'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if timestamp:
            LessonProgress.objects.update_or_create(
                lesson=lesson,
                user=request.user,
                defaults={'timestamp': timestamp}
            )
            return Response({'status': 'success'})
        return Response({'error': 'Invalid data'}, status=400)

    @swagger_auto_schema(
        operation_description="Получение сохраненного прогресса просмотра урока",
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'timestamp': openapi.Schema(type=openapi.TYPE_INTEGER, description='Временная метка в секундах'),
                    'last_viewed': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, nullable=True)
                }
            )
        }
    )
    @action(detail=True, methods=['get'])
    def get_progress(self, request, slug=None):
        """
        Получение сохраненного прогресса просмотра урока.
        """
        lesson = self.get_object()

        if getattr(self, 'swagger_fake_view', False):
            return Response({'timestamp': 0})

        if not request.user.is_authenticated:
            return Response({'timestamp': 0})

        progress = LessonProgress.objects.filter(
            lesson=lesson,
            user=request.user
        ).first()

        if progress:
            return Response({
                'timestamp': progress.timestamp,
                'last_viewed': progress.last_viewed
            })
        return Response({'timestamp': 0})