from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('comment_reply', 'Ответ на комментарий'),
        ('question_answer', 'Ответ на вопрос'),
        ('new_comment', 'Новый комментарий к уроку'),
        ('new_question', 'Новый вопрос'),
        ('new_lesson', 'Новый урок'),
        ('new_event', 'Новая оффлайн встреча'),
        ('system', 'Системное уведомление')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField('Заголовок', max_length=255)
    message = models.TextField('Сообщение')
    url = models.CharField('URL для перехода', max_length=255, blank=True)
    notification_type = models.CharField('Тип уведомления', max_length=20, choices=NOTIFICATION_TYPES)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    is_read = models.BooleanField('Прочитано', default=False)
    sent_to_browser = models.BooleanField('Отправлено в браузер', default=False)
    sent_to_telegram = models.BooleanField('Отправлено в Telegram', default=False)
    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'

    def __str__(self):
        return f'{self.get_notification_type_display()} для {self.user.username}'


class PushSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='push_subscriptions')
    subscription_info = models.JSONField('Информация о подписке')
    browser = models.CharField('Браузер', max_length=100, blank=True)
    device = models.CharField('Устройство', max_length=100, blank=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        verbose_name = 'Push-подписка'
        verbose_name_plural = 'Push-подписки'

    def __str__(self):
        return f'Push-подписка {self.user.username}'


class NotificationSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_settings')
    push_enabled = models.BooleanField('Push-уведомления', default=True)
    email_enabled = models.BooleanField('Email-уведомления', default=False)
    notification_types = models.JSONField('Типы уведомлений', default=dict)

    class Meta:
        verbose_name = 'Настройки уведомлений'
        verbose_name_plural = 'Настройки уведомлений'

    def __str__(self):
        return f'Настройки уведомлений пользователя {self.user.username}'

    def save(self, *args, **kwargs):
        if not self.notification_types:
            self.notification_types = {
                'question_answer': True,
                'comment_reply': True,
                'new_lesson': True,
                'new_event': True,
                'system': True
            }
        super().save(*args, **kwargs)