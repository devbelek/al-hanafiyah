from django.core.management.base import BaseCommand
from elasticsearch_dsl import connections
from apps.search.documents import QuestionDocument
from apps.questions.models import Question, Answer


class Command(BaseCommand):
    help = 'Test elasticsearch search functionality'

    def handle(self, *args, **options):
        # Правильное подключение к Elasticsearch с полным URL
        connections.create_connection(
            hosts=['http://elasticsearch:9200']  # Добавили 'http://'
        )
        self.stdout.write(self.style.SUCCESS('Connected to Elasticsearch'))

        # Тестовые запросы
        test_queries = [
            "намаз",
            "намас",
            "беш убак",
            "дарат",
            "даарат алуу",
            "орозо",
            "ураза",
            "жума",
            "нике кыюу",
            "курман",
            "садага",
            "ажыга баруу"
        ]

        # Создаем индекс заново
        QuestionDocument._index.delete(ignore=404)
        QuestionDocument.init()

        # Создаем тестовые данные
        self.stdout.write('Creating test data...')
        test_questions = [
            "Намаз кандай окулат?",
            "Беш убак намазды кантип окуйбуз?",
            "Дааратты кантип алабыз?",
            "Орозо кармоонун эрежелери кандай?",
            "Жума намазы кандайча окулат?",
            "Нике кыйууда эмнелер керек?",
            "Курман айт намазы кантип окулат?",
            "Садака берүүнүн сообу канча?",
            "Ажылыкка кантип барса болот?",
        ]

        for content in test_questions:
            question = Question.objects.create(
                content=content,
                telegram="@test_user",
                is_answered=True
            )
            Answer.objects.create(
                question=question,
                content=f"Ответ на вопрос: {content}"
            )

        # Обновляем индекс
        for question in Question.objects.all():
            QuestionDocument().update(question)

        self.stdout.write('Testing search queries...')
        # Проверяем каждый запрос
        for query in test_queries:
            self.stdout.write(f"\nSearching for: '{query}'")
            self.stdout.write("-" * 50)

            search = QuestionDocument.search().query(
                'multi_match',
                query=query,
                fields=['content^2', 'answer.content'],
                fuzziness='AUTO'
            )

            response = search.execute()

            if not response.hits:
                self.stdout.write("No results found")
                continue

            self.stdout.write(f"Found {response.hits.total.value} results\n")

            for hit in response:
                self.stdout.write(f"ID: {hit.meta.id}")
                self.stdout.write(f"Score: {hit.meta.score}")
                self.stdout.write(f"Content: {hit.content}")
                self.stdout.write("-" * 50)