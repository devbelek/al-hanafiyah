from django.core.management.base import BaseCommand
from django_elasticsearch_dsl.registries import registry
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Пересоздание индексов Elasticsearch'

    def handle(self, *args, **options):
        self.stdout.write('Удаление старых индексов...')
        try:
            registry.delete_all_indices()
            self.stdout.write(self.style.SUCCESS('Старые индексы успешно удалены'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Ошибка при удалении индексов: {e}'))

        self.stdout.write('Создание новых индексов...')
        try:
            registry.create_all_indices()
            self.stdout.write(self.style.SUCCESS('Новые индексы успешно созданы'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка при создании индексов: {e}'))
            return

        self.stdout.write('Обновление данных в индексах...')
        for index in registry.get_indices():
            self.stdout.write(f'Обновление индекса: {index._name}')
            try:
                qs = index.get_queryset()
                index.update(qs)
                self.stdout.write(self.style.SUCCESS(f'Индекс {index._name} успешно обновлен'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Ошибка при обновлении индекса {index._name}: {e}'))

        self.stdout.write(self.style.SUCCESS('Индексы успешно пересозданы!'))