from django.db import models
from django.core.exceptions import ValidationError
from ckeditor.fields import RichTextField
from django.utils.text import slugify
from django.utils.crypto import get_random_string
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
import os


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
    thumbnail = models.ImageField('Миниатюра', upload_to='ustaz_gallery/thumbnails/', blank=True, null=True)
    description = models.CharField('Описание', max_length=255, blank=True)

    class Meta:
        verbose_name = 'Фотография'
        verbose_name_plural = 'Фотографии'

    def __str__(self):
        return f'Фотография {self.id}'

    def create_thumbnail(self):
        if not self.image:
            return
        img = Image.open(self.image)
        width = 300
        ratio = width / float(img.width)
        height = int(float(img.height) * ratio)
        img = img.resize((width, height), Image.LANCZOS)
        thumb_io = BytesIO()
        img_format = 'JPEG' if self.image.name.lower().endswith('.jpg') or self.image.name.lower().endswith(
            '.jpeg') else 'PNG'
        img.save(thumb_io, format=img_format, quality=85)
        filename = os.path.basename(self.image.name)
        name, ext = os.path.splitext(filename)
        thumb_filename = f"{name}_thumb{ext}"
        self.thumbnail.save(thumb_filename, ContentFile(thumb_io.getvalue()), save=False)

    def save(self, *args, **kwargs):
        if not self.thumbnail:
            self.create_thumbnail()
        super().save(*args, **kwargs)


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

    def create_thumbnail(self):
        if self.media_type != 'video' or not self.media_file:
            return

        try:
            import subprocess
            import tempfile
            import os
            from django.core.files import File

            temp_thumb = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
            temp_thumb.close()

            media_path = self.media_file.path

            command = [
                'ffmpeg', '-i', media_path,
                '-ss', '00:00:05',
                '-vframes', '1',
                '-vf', 'scale=480:-1',
                '-q:v', '3',
                temp_thumb.name
            ]

            subprocess.call(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            with open(temp_thumb.name, 'rb') as f:
                filename = os.path.basename(self.media_file.name)
                name, _ = os.path.splitext(filename)
                thumb_filename = f"{name}_thumb.jpg"

                self.thumbnail.save(thumb_filename, File(f), save=False)

            os.unlink(temp_thumb.name)

        except Exception as e:
            print(f"Ошибка при создании миниатюры: {e}")

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

        if not self.thumbnail and self.media_type == 'video':
            if not self.pk:
                super().save(*args, **kwargs)
                self.create_thumbnail()
                super().save(*args, **kwargs)
                return
            else:
                self.create_thumbnail()

        super().save(*args, **kwargs)