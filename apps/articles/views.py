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

    def get_serializer_context(self):
        context = super().get_serializer_context()
        return context

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
            200: openapi.Response(
                description="Список статей",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'title': openapi.Schema(type=openapi.TYPE_STRING),
                            'slug': openapi.Schema(type=openapi.TYPE_STRING),
                            'content': openapi.Schema(type=openapi.TYPE_STRING),
                            'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                            'author_name': openapi.Schema(type=openapi.TYPE_STRING),
                            'image': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
                            'image_url': openapi.Schema(type=openapi.TYPE_STRING, nullable=True)
                        }
                    )
                )
            )
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Получение подробной информации о статье",
        responses={
            200: openapi.Response(
                description="Подробная информация о статье",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'title': openapi.Schema(type=openapi.TYPE_STRING),
                        'content': openapi.Schema(type=openapi.TYPE_STRING),
                        'image': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
                        'image_url': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
                        'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                        'updated_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                        'slug': openapi.Schema(type=openapi.TYPE_STRING),
                        'similar_articles': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'title': openapi.Schema(type=openapi.TYPE_STRING),
                                    'slug': openapi.Schema(type=openapi.TYPE_STRING),
                                    'content': openapi.Schema(type=openapi.TYPE_STRING),
                                    'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                                    'author_name': openapi.Schema(type=openapi.TYPE_STRING),
                                    'image': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
                                    'image_url': openapi.Schema(type=openapi.TYPE_STRING, nullable=True)
                                }
                            )
                        ),
                        'author': openapi.Schema(type=openapi.TYPE_INTEGER, nullable=True),
                        'author_details': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'biography': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
                                'achievements': openapi.Schema(type=openapi.TYPE_STRING),
                                'photos': openapi.Schema(
                                    type=openapi.TYPE_ARRAY,
                                    items=openapi.Schema(
                                        type=openapi.TYPE_OBJECT,
                                        properties={
                                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                            'image': openapi.Schema(type=openapi.TYPE_STRING),
                                            'description': openapi.Schema(type=openapi.TYPE_STRING)
                                        }
                                    )
                                )
                            },
                            nullable=True
                        ),
                        'is_moderated': openapi.Schema(type=openapi.TYPE_BOOLEAN)
                    }
                )
            ),
            404: "Статья не найдена"
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Получение похожих статей",
        responses={
            200: openapi.Response(
                description="Список похожих статей",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'title': openapi.Schema(type=openapi.TYPE_STRING),
                            'slug': openapi.Schema(type=openapi.TYPE_STRING),
                            'content': openapi.Schema(type=openapi.TYPE_STRING),
                            'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                            'author_name': openapi.Schema(type=openapi.TYPE_STRING),
                            'image': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
                            'image_url': openapi.Schema(type=openapi.TYPE_STRING, nullable=True)
                        }
                    )
                )
            ),
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
        serializer = ArticleListSerializer(similar_articles, many=True, context=self.get_serializer_context())
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Получение последних статей",
        responses={
            200: openapi.Response(
                description="Список последних статей",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'title': openapi.Schema(type=openapi.TYPE_STRING),
                            'slug': openapi.Schema(type=openapi.TYPE_STRING),
                            'content': openapi.Schema(type=openapi.TYPE_STRING),
                            'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                            'author_name': openapi.Schema(type=openapi.TYPE_STRING),
                            'image': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
                            'image_url': openapi.Schema(type=openapi.TYPE_STRING, nullable=True)
                        }
                    )
                )
            )
        }
    )
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """
        Получение последних добавленных статей.
        """
        latest_articles = self.get_queryset().order_by('-created_at')[:5]
        serializer = ArticleListSerializer(latest_articles, many=True, context=self.get_serializer_context())
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
            200: openapi.Response(
                description="Список статей по тегам",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'title': openapi.Schema(type=openapi.TYPE_STRING),
                            'slug': openapi.Schema(type=openapi.TYPE_STRING),
                            'content': openapi.Schema(type=openapi.TYPE_STRING),
                            'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                            'author_name': openapi.Schema(type=openapi.TYPE_STRING),
                            'image': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
                            'image_url': openapi.Schema(type=openapi.TYPE_STRING, nullable=True)
                        }
                    )
                )
            )
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
        serializer = ArticleListSerializer(articles, many=True, context=self.get_serializer_context())
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
            200: openapi.Response(
                description="Список статей по категории",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'title': openapi.Schema(type=openapi.TYPE_STRING),
                            'slug': openapi.Schema(type=openapi.TYPE_STRING),
                            'content': openapi.Schema(type=openapi.TYPE_STRING),
                            'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                            'author_name': openapi.Schema(type=openapi.TYPE_STRING),
                            'image': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
                            'image_url': openapi.Schema(type=openapi.TYPE_STRING, nullable=True)
                        }
                    )
                )
            ),
            400: "Не указана категория"
        }
    )
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        category_id = request.query_params.get('category')
        if not category_id:
            return Response({"error": "Не указана категория"}, status=400)

        try:
            category_id = int(category_id)

            from apps.lessons.models import Category
            category_exists = Category.objects.filter(id=category_id).exists()

            if not category_exists:
                return Response({"message": f"Категория с id={category_id} не найдена"}, status=200)

            all_articles = Article.objects.all()
            print(f"Всего статей: {all_articles.count()}")

            articles = Article.objects.filter(category_id=category_id, is_moderated=True)
            print(f"Статей в категории {category_id}: {articles.count()}")

            serializer = ArticleListSerializer(articles, many=True, context=self.get_serializer_context())
            return Response(serializer.data)
        except ValueError:
            return Response({"error": "Некорректный ID категории"}, status=400)
        except Exception as e:
            import traceback
            print(f"Ошибка при поиске статей по категории: {e}")
            print(traceback.format_exc())
            return Response({"error": f"Ошибка при поиске статей: {str(e)}"}, status=500)