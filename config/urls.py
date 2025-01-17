from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from apps.search.views import GlobalSearchView

schema_view = get_schema_view(
    openapi.Info(
        title="Hanafi API",
        default_version='v1',
        description="""
        API для образовательной платформы исламских учителей (устазов).

        ## Основные возможности:

        ### Уроки
        - Получение списка категорий, тем и модулей
        - Доступ к видео и аудио урокам
        - Комментирование уроков
        - Отметка полезных комментариев

        ### Вопрос-ответ
        - Задать вопрос устазу
        - Поиск похожих вопросов
        - Получение ответов
        - Уведомления через Telegram

        ### Статьи
        - Просмотр статей
        - Поиск по статьям
        - Получение похожих статей

        ### Оффлайн встречи
        - Просмотр предстоящих встреч
        - Детали мероприятий

        ### Устазы
        - Информация об устазах
        - Список публикаций и уроков
        """,
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('api/search/', include('apps.search.urls')),  # Добавляем урлы поиска
                  path('api/', include('apps.lessons.urls')),
                  path('api/', include('apps.questions.urls')),
                  path('api/', include('apps.articles.urls')),
                  path('api/', include('apps.events.urls')),
                  re_path(r'^swagger(?P<format>\.json|\.yaml)$',
                          schema_view.without_ui(cache_timeout=0),
                          name='schema-json'),
                  path('swagger/',
                       schema_view.with_ui('swagger', cache_timeout=0),
                       name='schema-swagger-ui'),
                  path('redoc/',
                       schema_view.with_ui('redoc', cache_timeout=0),
                       name='schema-redoc'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
