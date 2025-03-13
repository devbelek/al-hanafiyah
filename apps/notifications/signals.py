from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.lessons.models import Lesson
from apps.events.models import OfflineEvent
from django.contrib.auth.models import User
from .services import create_notification

@receiver(post_save, sender=Lesson)
def notify_on_new_lesson(sender, instance, created, **kwargs):
    if created:
        for user in User.objects.filter(is_active=True):
            create_notification(
                user=user,
                title='Новый урок доступен',
                message=f'В модуле "{instance.module.name}" появился новый урок',
                notification_type='new_lesson',
                content_object=instance,
                url=f'/lessons/{instance.slug}'
            )

@receiver(post_save, sender=OfflineEvent)
def notify_on_new_event(sender, instance, created, **kwargs):
    if created:
        for user in User.objects.filter(is_active=True):
            create_notification(
                user=user,
                title='Новая оффлайн встреча',
                message=f'Новая встреча: {instance.title} - {instance.location}',
                notification_type='new_event',
                content_object=instance,
                url=f'/events/{instance.id}'
            )