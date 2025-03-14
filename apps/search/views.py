from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .services import SearchService
from .serializers import SearchResultSerializer, SearchSuggestionSerializer
from .documentation import search_response, suggestions_response


class GlobalSearchView(APIView):
    """
    API для глобального поиска по всему контенту платформы.
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Глобальный поиск по всему контенту",
        manual_parameters=[
            openapi.Parameter(
                'q', openapi.IN_QUERY,
                description="Поисковый запрос",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'type', openapi.IN_QUERY,
                description="Тип контента",
                type=openapi.TYPE_STRING,
                enum=['all', 'questions', 'articles', 'lessons', 'events'],
                required=False,
                default='all'
            ),
            openapi.Parameter(
                'page', openapi.IN_QUERY,
                description="Номер страницы",
                type=openapi.TYPE_INTEGER,
                required=False,
                default=1
            ),
            openapi.Parameter(
                'size', openapi.IN_QUERY,
                description="Количество результатов на страницу",
                type=openapi.TYPE_INTEGER,
                required=False,
                default=10
            ),
        ],
        responses={
            200: search_response,
            400: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        example='Поисковый запрос обязателен'
                    )
                }
            )
        }
    )
    def get(self, request):
        """
        Выполняет поиск по всему контенту платформы или по конкретному типу контента.

        Поддерживает пагинацию результатов. При отсутствии поискового запроса возвращает ошибку 400.
        Результаты поиска включают в себя заголовок, тип контента, URL и релевантные фрагменты текста.
        """
        query = request.GET.get('q', '')
        doc_type = request.GET.get('type', 'all')
        page = int(request.GET.get('page', 1))
        size = int(request.GET.get('size', 10))

        if not query:
            return Response(
                {'error': 'Поисковый запрос обязателен'},
                status=400
            )

        results = SearchService.get_search_results(
            query=query,
            doc_type=doc_type,
            page=page,
            size=size
        )

        return Response({
            'results': results,
            'total': len(results),
            'page': page,
            'size': size
        })


class SearchSuggestionsView(APIView):
    """
    API для получения поисковых подсказок на основе частичного ввода.
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Получение поисковых подсказок для введенного текста",
        manual_parameters=[
            openapi.Parameter(
                'q', openapi.IN_QUERY,
                description="Поисковый запрос (частичный ввод)",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'limit', openapi.IN_QUERY,
                description="Максимальное количество подсказок",
                type=openapi.TYPE_INTEGER,
                required=False,
                default=5
            ),
        ],
        responses={
            200: suggestions_response,
            400: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        example='Поисковый запрос слишком короткий'
                    )
                }
            )
        }
    )
    def get(self, request):
        """
        Возвращает список подсказок на основе частичного ввода пользователя.

        Подсказки генерируются из наиболее популярных поисковых запросов и
        релевантных заголовков контента. Если запрос пустой, возвращает пустой массив.
        """
        query = request.GET.get('q', '')
        limit = int(request.GET.get('limit', 5))

        if not query:
            return Response([])

        suggestions = SearchService.get_suggestions(query, limit=limit)
        return Response(suggestions)


class SearchAutocompleteView(APIView):
    """
    API для автодополнения поисковых запросов в реальном времени.
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Автодополнение поисковых запросов в реальном времени",
        manual_parameters=[
            openapi.Parameter(
                'q', openapi.IN_QUERY,
                description="Поисковый запрос (частичный ввод)",
                type=openapi.TYPE_STRING,
                required=True
            ),
        ],
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'text': openapi.Schema(type=openapi.TYPE_STRING),
                        'highlight': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        }
    )
    def get(self, request):
        """
        Возвращает варианты автодополнения для текущего поискового запроса.

        В отличие от подсказок, автодополнение предназначено для завершения
        текущего слова или фразы, а не для предложения альтернативных запросов.
        """
        query = request.GET.get('q', '')

        if not query or len(query) < 2:
            return Response([])

        # Здесь должна быть реализация получения вариантов автодополнения
        # Для примера возвращаем несколько вариантов
        autocomplete = [
            {'text': f"{query} ханафитского мазхаба", 'highlight': f"<em>{query}</em> ханафитского мазхаба"},
            {'text': f"{query} в исламе", 'highlight': f"<em>{query}</em> в исламе"},
            {'text': f"{query} для начинающих", 'highlight': f"<em>{query}</em> для начинающих"}
        ]

        return Response(autocomplete)


class SimilarQuestionsView(APIView):
    """
    API для поиска похожих вопросов при вводе нового вопроса.
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Поиск похожих вопросов при вводе нового",
        manual_parameters=[
            openapi.Parameter(
                'text', openapi.IN_QUERY,
                description="Текст вопроса",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'limit', openapi.IN_QUERY,
                description="Максимальное количество похожих вопросов",
                type=openapi.TYPE_INTEGER,
                required=False,
                default=3
            ),
        ],
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'similar_questions': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'content': openapi.Schema(type=openapi.TYPE_STRING),
                                'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                                'is_answered': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                'similarity_score': openapi.Schema(type=openapi.TYPE_NUMBER,
                                                                   format=openapi.FORMAT_FLOAT)
                            }
                        )
                    )
                }
            ),
            400: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        example='Текст вопроса слишком короткий'
                    )
                }
            )
        }
    )
    def get(self, request):
        """
        Ищет похожие вопросы при вводе нового вопроса.

        Используется для предотвращения дублирования вопросов и помощи
        пользователям в нахождении ответов на уже отвеченные вопросы.
        Возвращает список похожих вопросов с указанием степени схожести.
        """
        text = request.GET.get('text', '')
        limit = int(request.GET.get('limit', 3))

        if not text or len(text) < 10:
            return Response({'similar_questions': []})

        similar_questions = SearchService.find_similar_questions(text, limit=limit)

        return Response({'similar_questions': similar_questions})