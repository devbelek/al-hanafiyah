from django.db import models
from ckeditor.fields import RichTextField
from django.utils.html import strip_tags
import html


class Question(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, verbose_name='Пользователь', null=True, blank=True)
    content = models.TextField('Вопрос')
    telegram = models.CharField('Telegram', max_length=100, blank=True)
    is_answered = models.BooleanField('Есть ответ', default=False)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    def clean_content(self):
        text = html.unescape(self.content)
        text = strip_tags(text)
        return text


    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        ordering = ['-created_at']

    def __str__(self):
        if self.user:
            return f'Вопрос от {self.user.username}'
        return f'Вопрос от {self.telegram}'


class Answer(models.Model):
    question = models.OneToOneField(Question, on_delete=models.CASCADE, verbose_name='Вопрос')
    content = RichTextField(
        'Ответ',
        config_name='default',
        extra_plugins=['font', 'justify', 'colorbutton', 'find', 'preview'],
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    converted_to_article = models.BooleanField('Конвертирован в статью', default=False)

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'
        ordering = ['-created_at']

    def __str__(self):
        return f'Ответ на вопрос от {self.question.telegram}'

    def save(self, *args, **kwargs):
        if not self.pk:
            self.question.is_answered = True
            self.question.save()
        super().save(*args, **kwargs)
