from django.core.cache import cache
from functools import wraps


def cache_search_results(timeout=300):
    """
    Декоратор для кэширования результатов поиска
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"search:{kwargs.get('query')}:{kwargs.get('doc_type')}:{kwargs.get('page')}:{kwargs.get('size')}"
            result = cache.get(cache_key)

            if result is None:
                result = func(*args, **kwargs)
                cache.set(cache_key, result, timeout)

            return result

        return wrapper

    return decorator
