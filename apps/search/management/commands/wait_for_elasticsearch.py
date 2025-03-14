from django.core.management.base import BaseCommand
import time
import urllib3
from elasticsearch import Elasticsearch
from django.conf import settings


class Command(BaseCommand):
    help = 'Wait for Elasticsearch to become available'

    def handle(self, *args, **options):
        self.stdout.write('Waiting for Elasticsearch...')
        es = Elasticsearch(hosts=[settings.ELASTICSEARCH_DSL['default']['hosts']])

        while True:
            try:
                if es.ping():
                    self.stdout.write(self.style.SUCCESS('Elasticsearch is available!'))
                    break
            except Exception as e:
                self.stdout.write(f'Elasticsearch is not available yet: {str(e)}')
                time.sleep(1)