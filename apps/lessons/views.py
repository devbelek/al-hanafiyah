from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Topic, Module, Lesson, Comment, UstazProfile, LessonProgress
from .serializers import (
    CategorySerializer, TopicSerializer, ModuleSerializer,
    LessonSerializer, CommentSerializer, UstazProfileSerializer
)


class UstazProfileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UstazProfile.objects.all()
    serializer_class = UstazProfileSerializer

    def list(self, request):
        profile = UstazProfile.objects.first()
        serializer = self.get_serializer(profile)
        return Response(serializer.data)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class TopicViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category']
    search_fields = ['name']


class ModuleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['topic']
    search_fields = ['name']

    @action(detail=False, methods=['post'])
    def reorder(self, request):
        for item in request.data:
            Module.objects.filter(id=item['id']).update(order=item['order'])
        return Response({'status': 'success'})


class LessonViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['module', 'media_type', 'is_intro']
    search_fields = ['module__name']

    @action(detail=True, methods=['post'])
    def add_comment(self, request, slug=None):
        lesson = self.get_object()
        serializer = CommentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(lesson=lesson)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def mark_helpful(self, request, slug=None):
        comment_id = request.data.get('comment_id')
        try:
            comment = Comment.objects.get(id=comment_id, lesson=self.get_object())
            comment.helpful_count += 1
            comment.save()
            return Response({'status': 'success'})
        except Comment.DoesNotExist:
            return Response(
                {'error': 'Comment not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['post'])
    def reorder(self, request):
        """
        Принимает массив: [{"id": 1, "order": 1}, {"id": 2, "order": 2}]
        """
        for item in request.data:
            Lesson.objects.filter(id=item['id']).update(order=item['order'])
        return Response({'status': 'success'})

    """
    # Функционал сохранения прогресса просмотра урока

    ## Как это работает:
    1. Фронтенд генерирует уникальный hash устройства при первом посещении:
    ```javascript
    // Пример генерации hash на фронтенде
    const generateDeviceHash = () => {
        const hash = Math.random().toString(36).substring(2) + Date.now().toString(36);
        localStorage.setItem('device_hash', hash);
        return hash;
    };

    // Получение существующего hash или генерация нового
    const getDeviceHash = () => {
        return localStorage.getItem('device_hash') || generateDeviceHash();
    };
    ```

    2. При просмотре видео/аудио периодически сохраняется прогресс:
    ```javascript
    // Сохранение прогресса каждые 5 секунд
    const videoPlayer = document.querySelector('video');
    setInterval(() => {
        fetch(`/api/lessons/${lessonSlug}/save_progress/`, {
            method: 'POST',
            headers: {
                'X-Device-Hash': getDeviceHash(),
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                timestamp: Math.floor(videoPlayer.currentTime)
            })
        });
    }, 5000);
    ```

    3. При открытии урока проверяется сохраненный прогресс:
    ```javascript
    // Проверка прогресса при загрузке страницы
    const checkProgress = async () => {
        const response = await fetch(`/api/lessons/${lessonSlug}/get_progress/`, {
            headers: {
                'X-Device-Hash': getDeviceHash()
            }
        });
        const data = await response.json();

        if (data.timestamp > 0) {
            // Показываем уведомление
            const minutes = Math.floor(data.timestamp / 60);
            const seconds = data.timestamp % 60;

            if (confirm(`Продолжить просмотр с ${minutes}:${seconds.toString().padStart(2, '0')}?`)) {
                videoPlayer.currentTime = data.timestamp;
            }
        }
    };
    ```
    """

    @action(detail=True, methods=['post'])
    def save_progress(self, request, slug=None):
        """
        Сохранение прогресса просмотра.

        Принимает:
        - Header: X-Device-Hash - уникальный идентификатор устройства
        - Body: {"timestamp": integer} - позиция в секундах

        Пример запроса:
        POST /api/lessons/lesson-slug/save_progress/
        Headers: {
            "X-Device-Hash": "abc123def456",
            "Content-Type": "application/json"
        }
        Body: {
            "timestamp": 407
        }
        """
        lesson = self.get_object()
        device_hash = request.headers.get('X-Device-Hash')
        timestamp = request.data.get('timestamp')

        if device_hash and timestamp:
            LessonProgress.objects.update_or_create(
                lesson=lesson,
                device_hash=device_hash,
                defaults={'timestamp': timestamp}
            )
            return Response({'status': 'success'})
        return Response({'error': 'Invalid data'}, status=400)

    @action(detail=True, methods=['get'])
    def get_progress(self, request, slug=None):
        """
        Получение сохраненного прогресса.

        Принимает:
        - Header: X-Device-Hash - уникальный идентификатор устройства

        Возвращает:
        {
            "timestamp": integer,  // позиция в секундах
            "last_viewed": datetime  // когда последний раз смотрели
        }

        Пример запроса:
        GET /api/lessons/lesson-slug/get_progress/
        Headers: {
            "X-Device-Hash": "abc123def456"
        }

        Пример ответа:
        {
            "timestamp": 407,
            "last_viewed": "2025-01-16T10:30:00Z"
        }
        """
        lesson = self.get_object()
        device_hash = request.headers.get('X-Device-Hash')

        if device_hash:
            progress = LessonProgress.objects.filter(
                lesson=lesson,
                device_hash=device_hash
            ).first()

            if progress:
                return Response({
                    'timestamp': progress.timestamp,
                    'last_viewed': progress.last_viewed
                })
        return Response({'timestamp': 0})
