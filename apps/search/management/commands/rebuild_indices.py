from django.core.management.base import BaseCommand
from django_elasticsearch_dsl.registries import registry
from elasticsearch.exceptions import NotFoundError
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Пересоздание индексов Elasticsearch'

    def handle(self, *args, **options):
        # Получаем все зарегистрированные документы
        for doc in registry.get_documents():
            index_name = doc._index._name
            self.stdout.write(f'Обработка индекса: {index_name}')

            # Пытаемся удалить индекс
            try:
                self.stdout.write(f'Удаление индекса {index_name}...')
                doc._index.delete(ignore=404)
                self.stdout.write(self.style.SUCCESS(f'Индекс {index_name} успешно удален'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Ошибка при удалении индекса {index_name}: {e}'))

            # Создаем индекс заново
            try:
                self.stdout.write(f'Создание индекса {index_name}...')
                doc._index.create()
                self.stdout.write(self.style.SUCCESS(f'Индекс {index_name} успешно создан'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Ошибка при создании индекса {index_name}: {e}'))
                continue

            # Индексируем данные
            try:
                self.stdout.write(f'Индексация данных для {index_name}...')
                qs = doc.get_queryset()
                doc().update(qs)
                self.stdout.write(self.style.SUCCESS(f'Данные для индекса {index_name} успешно проиндексированы'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Ошибка при индексации данных для {index_name}: {e}'))

        self.stdout.write(self.style.SUCCESS('Процесс пересоздания индексов завершен!'))