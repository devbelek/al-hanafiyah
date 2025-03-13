from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from ckeditor.fields import RichTextField


class UstazProfile(models.Model):
    name = models.CharField('Имя', max_length=100)
    biography = RichTextField('Биография', blank=True, null=True)
    achievements = models.TextField('Достижения')

    class Meta:
        verbose_name = 'Профиль устаза'
        verbose_name_plural = 'Профиль устаза'

    def __str__(self):
        return 'Профиль устаза'

    def save(self, *args, **kwargs):
        if not self.pk and UstazProfile.objects.exists():
            return
        super().save(*args, **kwargs)


class UstazGallery(models.Model):
    profile = models.ForeignKey(UstazProfile, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField('Фотография', upload_to='ustaz_gallery/')
    description = models.CharField('Описание', max_length=255, blank=True)

    class Meta:
        verbose_name = 'Фотография'
        verbose_name_plural = 'Фотографии'

    def __str__(self):
        return f'Фотография {self.id}'


class Category(models.Model):
    name = models.CharField('Название', max_length=200)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Topic(models.Model):
    name = models.CharField('Название', max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория')
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Тема'
        verbose_name_plural = 'Темы'

    def __str__(self):
        return f'{self.name} ({self.category.name})'


class Module(models.Model):
    name = models.CharField('Название', max_length=200)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, verbose_name='Тема')
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Модуль'
        verbose_name_plural = 'Модули'

    def __str__(self):
        return f'{self.name} - {self.topic.name}'

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            unique_slug = base_slug
            counter = 1

            while Module.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = unique_slug

        super().save(*args, **kwargs)


class Lesson(models.Model):
    MEDIA_TYPES = (
        ('video', 'Видео'),
        ('audio', 'Аудио'),
    )

    module = models.ForeignKey(Module, on_delete=models.CASCADE, verbose_name='Модуль')
    media_type = models.CharField('Тип медиа', max_length=5, choices=MEDIA_TYPES)
    media_file = models.FileField('Медиа файл', upload_to='lessons/%Y/%m/%d/')
    is_intro = models.BooleanField('Вводный урок', default=False)
    order = models.IntegerField('Порядок', default=0)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ['module', '-is_intro', 'order']
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'
        unique_together = [('module', 'order', 'is_intro')]

    def __str__(self):
        return f'Урок {self.order} ({self.get_media_type_display()})'

    def clean(self):
        if self.is_intro:
            if not self.pk and Lesson.objects.filter(module=self.module, is_intro=True).exists():
                raise ValidationError({'is_intro': 'В модуле уже есть вводный урок'})
            self.order = 0

    def save(self, *args, **kwargs):
        if not self.slug:
            if self.is_intro:
                self.slug = f"intro-{self.module.slug}"
            else:
                self.slug = f"lesson-{self.module.slug}-{self.order}"
            base_slug = self.slug
            counter = 1
            while Lesson.objects.filter(slug=self.slug).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1

        super().save(*args, **kwargs)


class LessonProgress(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progress')
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True, blank=True)
    device_hash = models.CharField('Хеш устройства', max_length=64, blank=True)
    timestamp = models.IntegerField('Время в секундах')
    last_viewed = models.DateTimeField('Последний просмотр', auto_now=True)

    class Meta:
        unique_together = [['lesson', 'user']]
        verbose_name = 'Прогресс урока'
        verbose_name_plural = 'Прогресс уроков'


class Comment(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, verbose_name='Урок', related_name='comments')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE,
                               verbose_name='Родительский комментарий', related_name='replies')
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, verbose_name='Пользователь', null=True, blank=True)
    content = models.TextField('Содержание')
    telegram = models.CharField('Telegram', max_length=100, blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    is_moderated = models.BooleanField('Модерировано', default=False)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-created_at']

    def __str__(self):
        username = self.user.username if self.user else self.telegram
        return f'Комментарий от {username} к {self.lesson}'


class CommentLike(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['comment', 'user']
        verbose_name = 'Лайк комментария'
        verbose_name_plural = 'Лайки комментариев'

