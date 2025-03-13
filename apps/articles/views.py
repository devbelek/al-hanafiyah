from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Article
from .serializers import ArticleSerializer, ArticleListSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API для работы со статьями.
    """
    queryset = Article.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['title', 'content']
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'list':
            return ArticleListSerializer
        return ArticleSerializer

    @swagger_auto_schema(
        operation_description="Получение списка всех статей",
        manual_parameters=[
            openapi.Parameter(
                'search',
                openapi.IN_QUERY,
                description="Поиск по заголовку и содержанию",
                type=openapi.TYPE_STRING
            )
        ],
        responses={
            200: ArticleListSerializer(many=True)
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Получение подробной информации о статье",
        responses={
            200: ArticleSerializer(),
            404: "Статья не найдена"
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Получение похожих статей",
        responses={
            200: ArticleListSerializer(many=True),
            404: "Статья не найдена"
        }
    )
    @action(detail=True, methods=['get'])
    def similar(self, request, slug=None):
        """
        Получение похожих статей для указанной статьи.
        """
        article = self.get_object()
        similar_articles = Article.objects.exclude(id=article.id)[:5]
        serializer = ArticleListSerializer(similar_articles, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Получение последних статей",
        responses={
            200: ArticleListSerializer(many=True)
        }
    )
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """
        Получение последних добавленных статей.
        """
        latest_articles = self.get_queryset().order_by('-created_at')[:5]
        serializer = ArticleListSerializer(latest_articles, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Поиск статей по тегам",
        manual_parameters=[
            openapi.Parameter(
                'tags',
                openapi.IN_QUERY,
                description="Теги через запятую",
                type=openapi.TYPE_STRING
            )
        ],
        responses={
            200: ArticleListSerializer(many=True)
        }
    )
    @action(detail=False, methods=['get'])
    def by_tags(self, request):
        """
        Поиск статей по тегам.
        """
        tags = request.query_params.get('tags', '').split(',')
        if not tags or tags[0] == '':
            return Response([])

        # Логика может отличаться в зависимости от реализации вашей модели статей с тегами
        # Примерный код:
        # articles = Article.objects.filter(tags__name__in=tags).distinct()

        # В данном случае просто вернем все статьи, так как в исходной модели нет поля тегов
        articles = self.get_queryset()[:5]
        serializer = ArticleListSerializer(articles, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Поиск статей по категории",
        manual_parameters=[
            openapi.Parameter(
                'category',
                openapi.IN_QUERY,
                description="ID категории",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: ArticleListSerializer(many=True),
            400: "Не указана категория"
        }
    )
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """
        Поиск статей по категории.
        """
        category_id = request.query_params.get('category')
        if not category_id:
            return Response({"error": "Не указана категория"}, status=400)

        # Логика может отличаться в зависимости от реализации вашей модели статей с категориями
        # Примерный код:
        # articles = Article.objects.filter(category_id=category_id)

        # В данном случае просто вернем все статьи, так как в исходной модели нет поля category
        articles = self.get_queryset()[:5]
        serializer = ArticleListSerializer(articles, many=True)
        return Response(serializer.data)