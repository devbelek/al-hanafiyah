from django.core.management.base import BaseCommand
from apps.notifications.bot import run_bot

class Command(BaseCommand):
    help = 'Запуск Telegram-бота'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Запуск Telegram-бота...'))
        run_bot()