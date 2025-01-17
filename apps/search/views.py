from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .services import SearchService
from .serializers import SearchResultSerializer, SearchSuggestionSerializer
from .documentation import search_response, suggestions_response


class GlobalSearchView(APIView):
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
            400: 'Отсутствует поисковый запрос'
        }
    )
    def get(self, request):
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
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Получение поисковых подсказок",
        manual_parameters=[
            openapi.Parameter(
                'q', openapi.IN_QUERY,
                description="Поисковый запрос",
                type=openapi.TYPE_STRING,
                required=True
            ),
        ],
        responses={
            200: suggestions_response
        }
    )
    def get(self, request):
        query = request.GET.get('q', '')

        if not query:
            return Response([])

        suggestions = SearchService.get_suggestions(query)
        return Response(suggestions)
