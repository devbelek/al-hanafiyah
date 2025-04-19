from django.db import models
from django.core.exceptions import ValidationError
from ckeditor.fields import RichTextField
from django.utils.text import slugify
from django.utils.crypto import get_random_string
import os
import subprocess
import tempfile
from django.core.files import File
import logging

logger = logging.getLogger(__name__)

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
            base_slug = slugify(self.name)
            if not base_slug:
                try:
                    from transliterate import slugify as tr_slugify
                    base_slug = tr_slugify(self.name, language_code='ru')
                except ImportError:
                    base_slug = 'category'
            if not base_slug:
                base_slug = f"category-{str(self.id or '')}"
            slug = base_slug
            counter = 1

            while Category.objects.filter(slug=slug).exists():
                random_suffix = get_random_string(4).lower()
                slug = f"{base_slug}-{counter}-{random_suffix}"
                counter += 1

            self.slug = slug

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
    image = models.ImageField('Изображение', upload_to='topics/', blank=True, null=True)

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
    thumbnail = models.ImageField('Превью', upload_to='lessons/thumbnails/%Y/%m/', blank=True, null=True)
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

    @property
    def duration(self):
        if not self.media_file:
            return "0:00"

        import subprocess
        import json
        import os

        if not os.path.exists(self.media_file.path):
            return "0:00"

        try:
            result = subprocess.run([
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'json',
                self.media_file.path
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            if result.returncode != 0:
                return "0:00"

            output = json.loads(result.stdout)
            duration = float(output['format']['duration'])

            minutes = int(duration // 60)
            seconds = int(duration % 60)

            return f"{minutes}:{seconds:02d}"
        except Exception as e:
            print(f"Ошибка при получении длительности: {e}")
            return "0:00"

    def generate_thumbnail(self):
        if self.media_type != 'video' or not self.media_file:
            return False

        try:
            # Получаем год и месяц из пути к файлу
            file_path_parts = self.media_file.name.split('/')
            year_month = '/'.join(file_path_parts[1:3])  # получаем '2025/04'

            # Создаем директорию для миниатюр
            from django.conf import settings
            thumbnail_dir = os.path.join(settings.MEDIA_ROOT, 'lessons/thumbnails', year_month)
            os.makedirs(thumbnail_dir, exist_ok=True)

            # Получаем имя файла
            filename_base = os.path.basename(self.media_file.name)
            thumbnail_filename = f"thumb_{filename_base}.jpg"
            thumbnail_path = os.path.join(thumbnail_dir, thumbnail_filename)

            # Извлекаем кадр из видео
            command = [
                'ffmpeg', '-i', self.media_file.path,
                '-ss', '00:00:03',  # 3-я секунда видео
                '-vframes', '1',  # извлекаем один кадр
                '-vf', 'scale=640:-1',  # размер 640px по ширине
                '-q:v', '2',  # качество JPEG
                '-y',  # перезаписать файл
                thumbnail_path
            ]

            result = subprocess.call(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Проверяем результат
            if result == 0 and os.path.exists(thumbnail_path) and os.path.getsize(thumbnail_path) > 0:
                # Путь для сохранения в базе данных (относительно MEDIA_ROOT)
                rel_path = f"lessons/thumbnails/{year_month}/{thumbnail_filename}"
                self.thumbnail = rel_path
                print(f"✅ Превью успешно создано: {rel_path}")
                return True

            print(f"❌ Не удалось создать превью для {self.id}")
            return False
        except Exception as e:
            print(f"Ошибка при создании превью: {e}")
            return False

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

        # Сохраняем объект
        is_new = self.pk is None
        super().save(*args, **kwargs)

        # Генерируем миниатюру для видео, если еще не создана или не существует
        if self.media_type == 'video' and (not self.thumbnail or
                                           (self.thumbnail and not os.path.exists(
                                               os.path.join(settings.MEDIA_ROOT, str(self.thumbnail))))):
            success = self.generate_thumbnail()
            if success:
                # Если миниатюра была создана, сохраняем объект еще раз
                super().save(update_fields=['thumbnail'])


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

