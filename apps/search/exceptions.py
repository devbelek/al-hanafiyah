from rest_framework.exceptions import APIException


class SearchException(APIException):
    status_code = 500
    default_detail = 'Ошибка поиска'
    default_code = 'search_error'


class ElasticsearchConnectionError(SearchException):
    status_code = 503
    default_detail = 'Сервис поиска временно недоступен'
    default_code = 'elasticsearch_connection_error'


class InvalidQueryError(SearchException):
    status_code = 400
    default_detail = 'Некорректный поисковый запрос'
    default_code = 'invalid_query'
