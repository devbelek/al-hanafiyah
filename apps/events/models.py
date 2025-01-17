from django.db import models
from ckeditor.fields import RichTextField


class OfflineEvent(models.Model):
    title = models.CharField('Название', max_length=200)
    description = RichTextField('Описание')
    event_date = models.DateTimeField('Дата и время проведения', blank=True, null=True)
    location = models.CharField('Место проведения', max_length=255)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Офлайн встреча'
        verbose_name_plural = 'Офлайн встречи'
        ordering = ['event_date']

    def __str__(self):
        return self.title
