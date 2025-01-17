from django.core.management.base import BaseCommand
from django_elasticsearch_dsl.registries import registry


class Command(BaseCommand):
    help = 'Пересоздание поисковых индексов'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Принудительное пересоздание индексов'
        )

    def handle(self, *args, **options):
        for doc in registry.get_documents():
            self.stdout.write(f'Обработка индекса {doc._index._name}...')
            if options['force']:
                self.stdout.write('Удаление старого индекса...')
                doc._index.delete(ignore=404)

            self.stdout.write('Создание индекса...')
            doc._index.create()

            self.stdout.write('Индексация документов...')
            doc().update(scan=True)

        self.stdout.write(self.style.SUCCESS('Индексы успешно обновлены!'))