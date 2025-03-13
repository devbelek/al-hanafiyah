import requests
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from .models import Notification


def create_notification(user, title, message, notification_type, content_object=None, url=''):
    content_type = None
    object_id = None

    if content_object:
        content_type = ContentType.objects.get_for_model(content_object)
        object_id = content_object.id

    notification = Notification.objects.create(
        user=user,
        title=title,
        message=message,
        notification_type=notification_type,
        content_type=content_type,
        object_id=object_id,
        url=url
    )

    if user.profile.telegram:
        send_telegram_notification(
            telegram_username=user.profile.telegram,
            title=title,
            message=message,
            url=url
        )
        notification.sent_to_telegram = True
        notification.save()

    return notification


def send_admin_notification(title, message, notification_type, content_object=None, url=''):
    admins = User.objects.filter(is_staff=True)

    for admin in admins:
        create_notification(
            user=admin,
            title=title,
            message=message,
            notification_type=notification_type,
            content_object=content_object,
            url=url
        )


def send_telegram_notification(telegram_username, title, message, url=''):
    bot_token = settings.TELEGRAM_BOT_TOKEN

    if not bot_token or not telegram_username:
        return False

    telegram_username = telegram_username.lstrip('@')
    emoji = '🔔'
    if 'урок' in title.lower():
        emoji = '🎓'
    elif 'встреч' in title.lower():
        emoji = '📅'
    elif 'ответ' in title.lower() and 'вопрос' in title.lower():
        emoji = '❓'
    elif 'коммент' in title.lower():
        emoji = '💬'

    try:
        text = f"{emoji} <b>{title}</b>\n\n{message}"

        if url:
            text += f"\n\n<a href='https://al-hanafiyah.com{url}'>Посмотреть</a>"

        response = requests.post(
            f'https://api.telegram.org/bot{bot_token}/sendMessage',
            json={
                'chat_id': f'@{telegram_username}',
                'text': text,
                'parse_mode': 'HTML'
            }
        )

        return response.status_code == 200
    except Exception as e:
        print(f"Ошибка отправки в Telegram: {e}")
        return False