from django.db import models
from django.utils.text import slugify
from django.utils.html import strip_tags
from ckeditor.fields import RichTextField
from apps.lessons.models import UstazProfile


class Article(models.Model):
    title = models.CharField('Заголовок', max_length=200)
    content = RichTextField('Содержание')
    short_description = models.TextField('Краткое описание', blank=True)
    image = models.ImageField('Изображение', upload_to='articles/', null=True, blank=True)
    author = models.ForeignKey(UstazProfile, on_delete=models.SET_NULL,
                               null=True, blank=True,
                               verbose_name='Автор',
                               related_name='articles')
    is_moderated = models.BooleanField('Опубликовано', default=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    slug = models.SlugField('URL', unique=True, help_text="URL статьи будет сгенерирован автоматически")

    class Meta:
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def clean_content(self):
        return strip_tags(self.content)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        if not self.short_description and self.content:
            clean_text = strip_tags(self.content)
            self.short_description = clean_text[:250] + '...' if len(clean_text) > 250 else clean_text

        super().save(*args, **kwargs)