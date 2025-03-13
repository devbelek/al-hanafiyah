from django.apps import AppConfig

class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.notifications'

    # Комментируем или удаляем этот метод, так как теперь бот запускается в отдельном контейнере
    # def ready(self):
    #     import os
    #     if os.environ.get('RUN_MAIN', None) != 'true':
    #         try:
    #             from .bot import start_bot
    #             start_bot()
    #         except Exception as e:
    #             print(f"Ошибка запуска бота: {e}")