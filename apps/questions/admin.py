from django.contrib import admin
from django.utils.html import format_html
from .models import Question, Answer


class AnswerInline(admin.StackedInline):
    model = Answer
    can_delete = False
    extra = 1
    max_num = 1
    fields = ['content']
    verbose_name = 'Ответ'
    verbose_name_plural = 'Ответ'


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = [
        'status_display',
        'question_link',
        'content_display',
        'telegram_display',
        'created_at_display',
    ]
    list_filter = [
        ('is_answered', admin.BooleanFieldListFilter),
        ('created_at', admin.DateFieldListFilter),
    ]
    search_fields = ['content', 'telegram']
    readonly_fields = ['created_at', 'telegram', 'content']
    fields = [('telegram', 'created_at'), 'content']
    inlines = [AnswerInline]
    list_per_page = 20

    def question_content(self, obj):
        return format_html(
            '<div class="question-content-box">{}</div>',
            obj.content
        )
    question_content.short_description = 'Вопрос'

    def question_link(self, obj):
        return f'№{obj.id}'
    question_link.short_description = 'ID'

    def content_display(self, obj):
        return obj.clean_content()[:100] + '...' if len(obj.clean_content()) > 100 else obj.clean_content()
    content_display.short_description = 'Вопрос'

    def telegram_display(self, obj):
        if obj.telegram:
            return format_html(
                '<div class="telegram-cell">'
                '<span>{}</span>'
                '<a href="https://t.me/{}" class="telegram-link" target="_blank">'
                '<span class="telegram-icon">📱</span>'
                '</a>'
                '</div>',
                obj.telegram,
                obj.telegram.strip('@')
            )
        return '-'
    telegram_display.short_description = 'Telegram'

    def created_at_display(self, obj):
        return obj.created_at.strftime('%d.%m.%Y %H:%M')
    created_at_display.short_description = 'Дата'

    def status_display(self, obj):
        status_class = 'answered' if obj.is_answered else 'pending'
        status_text = 'Отвечено' if obj.is_answered else 'Ожидает'
        return format_html(
            '<div class="status-container">'
            '<span class="status {}">{}</span>'
            '</div>',
            status_class, status_text
        )
    status_display.short_description = 'Статус'

    def get_list_display_links(self, request, list_display):
        return ['question_link', 'content_display']

    class Media:
        css = {
            'all': ('admin/css/questions.css',)
        }