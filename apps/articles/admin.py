from django.contrib import admin
from django.utils.html import format_html
from django.utils.text import slugify
from django.db import IntegrityError
from django.utils.crypto import get_random_string
from apps.lessons.models import UstazProfile  # Импортируем модель UstazProfile

from .models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title_display', 'thumbnail_display', 'author_display', 'date_display', 'edit_button']
    list_filter = ['created_at', 'author', 'is_moderated']
    search_fields = ['title', 'content']
    fields = ['title', 'content', 'short_description', 'image', 'author', 'is_moderated']
    ordering = ['-created_at']
    list_per_page = 20
    autocomplete_fields = ['author']

    def thumbnail_display(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover;" />',
                obj.image.url
            )
        return '-'

    thumbnail_display.short_description = 'Изображение'

    def title_display(self, obj):
        # Ограничиваем длину заголовка для компактности
        title = obj.title if len(obj.title) <= 50 else obj.title[:47] + '...'
        return format_html(
            '<div class="article-title-container">'
            '<div class="article-title">{}</div>'
            '</div>',
            title
        )

    title_display.short_description = 'Статья'

    def author_display(self, obj):
        if obj.author:
            return "Устаз"  # Можно изменить на какое-то конкретное имя, если нужно
        return "-"

    author_display.short_description = 'Автор'

    def date_display(self, obj):
        return format_html(
            '<div class="article-date">'
            '<span class="date-time">{}</span>'
            '</div>',
            obj.created_at.strftime('%d.%m.%Y %H:%M')
        )

    date_display.short_description = 'Дата'

    def edit_button(self, obj):
        return format_html(
            '<div class="action-buttons">'
            '<a href="/admin/articles/article/{}/change/" class="edit-btn">'
            '<span>✏️</span>'
            '<span class="btn-text">Изменить</span>'
            '</a>'
            '</div>',
            obj.id
        )

    edit_button.short_description = 'Действия'

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def save_model(self, request, obj, form, change):
        # Если пользователь является устазом, устанавливаем его как автора
        if request.user.profile.is_ustaz and not obj.author:
            try:
                ustaz_profile = UstazProfile.objects.get(user=request.user)
                obj.author = ustaz_profile
            except UstazProfile.DoesNotExist:
                pass

        if not change:  # Если это новая статья
            base_slug = slugify(obj.title)
            slug = base_slug
            counter = 1

            # Пытаемся найти уникальный slug
            while True:
                try:
                    # Проверяем существует ли статья с таким slug
                    if not Article.objects.filter(slug=slug).exists():
                        obj.slug = slug
                        super().save_model(request, obj, form, change)
                        break
                    else:
                        # Если slug занят, добавляем число к базовому slug
                        slug = f"{base_slug}-{counter}"
                        counter += 1
                except IntegrityError:
                    # Если произошла ошибка уникальности, генерируем случайный суффикс
                    slug = f"{base_slug}-{get_random_string(4)}"
                    continue
        else:
            # Если это существующая статья, просто сохраняем
            super().save_model(request, obj, form, change)

    class Media:
        css = {
            'all': ('admin/css/articles.css',)
        }