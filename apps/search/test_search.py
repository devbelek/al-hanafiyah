import os
import sys
import django
from pathlib import Path
from elasticsearch_dsl import connections, Q
from apps.search.documents import QuestionDocument
from apps.questions.models import Question, Answer

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Подключение к Elasticsearch
connections.create_connection(hosts=['http://elasticsearch:9200'])


def test_search(query):
    """
    Тестирование поиска с выводом результатов
    """
    print(f"\nПоиск для запроса: '{query}'")
    print("-" * 50)

    # Улучшенный поисковый запрос
    search = QuestionDocument.search().query(
        Q('bool',
          should=[
              # Точное совпадение
              Q('match_phrase', content={
                  'query': query,
                  'boost': 3
              }),
              # Синонимы и похожие слова
              Q('multi_match', {
                  'query': query,
                  'fields': ['content^2', 'answer.content'],
                  'type': 'best_fields',
                  'fuzziness': 'AUTO',
                  'minimum_should_match': '70%'
              }),
              # Поиск по частям слова
              Q('match', content={
                  'query': query,
                  'operator': 'and',
                  'minimum_should_match': '60%'
              })
          ]
          )
    ).source(['id', 'content'])

    # Убираем дубликаты
    search = search.collapse('content')

    # Добавляем подсветку совпадений
    search = search.highlight(
        'content',
        'answer.content',
        pre_tags=['<em>'],
        post_tags=['</em>']
    )

    # Получаем результаты
    response = search.execute()

    if not response.hits:
        print("Результатов не найдено")
        return

    print(f"Найдено результатов: {response.hits.total.value}\n")

    # Выводим результаты
    for hit in response:
        print(f"ID: {hit.meta.id}")
        print(f"Score: {hit.meta.score}")
        print(f"Контент: {hit.content}")

        # Выводим подсветку если есть
        if hasattr(hit.meta, 'highlight'):
            if hasattr(hit.meta.highlight, 'content'):
                print("Совпадение: ", hit.meta.highlight.content[0])
        print("-" * 50)


def create_test_data():
    """
    Создание тестовых данных
    """
    # Удаляем старые данные
    Question.objects.all().delete()

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

    print("Создание тестовых вопросов...")
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
    print("Тестовые данные созданы")


def run_tests():
    """
    Запуск всех тестов
    """
    # Создаем индекс заново
    QuestionDocument._index.delete(ignore=404)
    QuestionDocument.init()

    # Создаем тестовые данные
    create_test_data()

    # Обновляем индекс
    for question in Question.objects.all():
        QuestionDocument().update(question)

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
        "ажыга баруу",
        # Дополнительные тесты для проверки синонимов
        "молитва",
        "пост",
        "омовение",
        "никах"
    ]

    # Проверяем каждый запрос
    for query in test_queries:
        test_search(query)


if __name__ == "__main__":
    run_tests()