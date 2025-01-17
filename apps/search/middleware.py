from django.http import JsonResponse
from elasticsearch.exceptions import ConnectionError
from .exceptions import ElasticsearchConnectionError


class ElasticsearchMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if '/api/search' in request.path:
            try:
                response = self.get_response(request)
                return response
            except ConnectionError:
                return JsonResponse(
                    {'error': 'Сервис поиска временно недоступен'},
                    status=503
                )
        return self.get_response(request)