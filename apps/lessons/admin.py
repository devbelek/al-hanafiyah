from django.contrib import admin
from django.utils.text import slugify
from .models import Category, Topic, Module, Lesson, Comment, UstazProfile, UstazGallery
from django.core.exceptions import ValidationError
from django.db import models


class UstazGalleryInline(admin.TabularInline):
    model = UstazGallery
    extra = 1


@admin.register(UstazProfile)
class UstazProfileAdmin(admin.ModelAdmin):
    inlines = [UstazGalleryInline]
    search_fields = ['name']

    def has_add_permission(self, request):
        if UstazProfile.objects.exists():
            return False
        return True


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    readonly_fields = ['slug']
    search_fields = ['name']

    def get_prepopulated_fields(self, request, obj=None):
        return {}

    def save_model(self, request, obj, form, change):
        if not obj.slug:
            obj.slug = slugify(obj.name)
        super().save_model(request, obj, form, change)


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']
    list_filter = ['category']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


class LessonInline(admin.TabularInline):
    model = Lesson
    fields = ['media_type', 'media_file', 'is_intro', 'order']
    extra = 1
    ordering = ['order']


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'topic']
    list_filter = ['topic']
    search_fields = ['name']
    readonly_fields = ['slug']

    def save_model(self, request, obj, form, change):
        if not obj.slug or obj.slug == '-1':
            from transliterate import slugify as tr_slugify
            base_slug = tr_slugify(obj.name, language_code='ru')
            if not base_slug:
                base_slug = slugify(obj.name)
            topic_slug = tr_slugify(obj.topic.name, language_code='ru')
            if topic_slug:
                base_slug = f"{topic_slug}-{base_slug}"
            unique_slug = base_slug
            counter = 1

            while Module.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1

            obj.slug = unique_slug

        if not obj.slug:
            raise ValidationError("Невозможно создать уникальный slug для этого модуля")

        super().save_model(request, obj, form, change)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'get_topic', 'get_media_type', 'is_intro', 'order', 'created_at']
    list_filter = ['media_type', 'is_intro', 'module__topic__category', 'module__topic', 'module']
    search_fields = ['module__name', 'module__topic__name']
    date_hierarchy = 'created_at'
    exclude = ['slug']
    fields = ['module', 'media_type', 'media_file', 'is_intro']

    def get_queryset(self, request):
        return super().get_queryset(request).order_by(
            'module',
            '-is_intro',
            'order'
        )

    def get_full_name(self, obj):
        if obj.is_intro:
            return f"📌 {obj.module.name} - Вводный урок"
        return f"⠀⠀⠀▫️ {obj.module.name} - Урок {obj.order}"

    get_full_name.short_description = 'Название'

    def get_topic(self, obj):
        return obj.module.topic.name

    get_topic.short_description = 'Тема'

    def get_media_type(self, obj):
        icons = {
            'video': '🎥',
            'audio': '🎧'
        }
        return f"{icons.get(obj.media_type, '')} {obj.get_media_type_display()}"

    get_media_type.short_description = 'Тип медиа'

    def save_model(self, request, obj, form, change):
        if not change:
            if obj.is_intro:
                obj.order = 0
            else:
                max_order = Lesson.objects.filter(
                    module=obj.module,
                    is_intro=False
                ).aggregate(models.Max('order'))['order__max'] or 0
                obj.order = max_order + 1
        super().save_model(request, obj, form, change)

    class Media:
        css = {
            'all': [
                'admin/css/custom_lesson_list.css',
            ]
        }


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['telegram', 'lesson', 'is_moderated', 'created_at']
    list_filter = ['is_moderated', 'created_at', 'lesson']
    search_fields = ['content', 'telegram']
    date_hierarchy = 'created_at'
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        queryset.update(is_moderated=True)

    approve_comments.short_description = "Одобрить выбранные комментарии"
