from elasticsearch_dsl import Q
from django.core.cache import cache
from .documents import (
    QuestionDocument, ArticleDocument,
    LessonDocument, EventDocument
)


class SearchService:
    @staticmethod
    def get_search_results(query, doc_type='all', page=1, size=10):
        start = (page - 1) * size
        results = []

        def search_documents(document_class, fields, highlight_fields=None):
            search = document_class.search().query(
                Q('multi_match',
                  query=query,
                  fields=fields,
                  fuzziness='AUTO')
            )

            if highlight_fields:
                search = search.highlight(
                    *highlight_fields,
                    pre_tags=['<em>'],
                    post_tags=['</em>']
                )

            return search[start:start + size].execute()

        if doc_type in ['all', 'questions']:
            questions = search_documents(
                QuestionDocument,
                ['content^2', 'answer.content'],
                ['content', 'answer.content']
            )
            results.extend(SearchService._format_questions(questions))

        if doc_type in ['all', 'articles']:
            articles = search_documents(
                ArticleDocument,
                ['title^3', 'content'],
                ['title', 'content']
            )
            results.extend(SearchService._format_articles(articles))

        if doc_type in ['all', 'lessons']:
            lessons = search_documents(
                LessonDocument,
                ['module.name^2', 'module.topic.name', 'module.topic.category.name'],
                ['module.name']
            )
            results.extend(SearchService._format_lessons(lessons))

        if doc_type in ['all', 'events']:
            events = search_documents(
                EventDocument,
                ['title^2', 'description', 'location'],
                ['title', 'description']
            )
            results.extend(SearchService._format_events(events))

        return results

    @staticmethod
    def _format_questions(questions):
        results = []
        for hit in questions:
            highlight = (
                hit.meta.highlight.content[0]
                if hasattr(hit.meta, 'highlight')
                else hit.content
            )
            results.append({
                'id': hit.id,
                'type': 'question',
                'content': hit.content,
                'url': f'/questions/{hit.id}',
                'created_at': hit.created_at,
                'highlight': highlight,
                'additional_info': {
                    'is_answered': hit.is_answered,
                    'telegram': hit.telegram
                }
            })
        return results

    @staticmethod
    def _format_articles(articles):
        results = []
        for hit in articles:
            highlight = None
            if hasattr(hit.meta, 'highlight'):
                if hasattr(hit.meta.highlight, 'title'):
                    highlight = hit.meta.highlight.title[0]
                elif hasattr(hit.meta.highlight, 'content'):
                    highlight = hit.meta.highlight.content[0]

            if not highlight:
                highlight = hit.title

            results.append({
                'id': hit.id,
                'type': 'article',
                'title': hit.title,
                'slug': hit.slug,
                'url': f'/articles/{hit.slug}',
                'created_at': hit.created_at,
                'highlight': highlight
            })
        return results

    @staticmethod
    def _format_lessons(lessons):
        results = []
        for hit in lessons:
            highlight = (
                hit.meta.highlight.get('module.name', [hit.module.name])[0]
                if hasattr(hit.meta, 'highlight')
                else hit.module.name
            )
            results.append({
                'id': hit.id,
                'type': 'lesson',
                'title': hit.module.name,
                'url': f'/lessons/{hit.slug}',
                'created_at': hit.created_at,
                'highlight': highlight,
                'additional_info': {
                    'topic': hit.module.topic.name,
                    'category': hit.module.topic.category.name
                }
            })
        return results

    @staticmethod
    def _format_events(events):
        results = []
        for hit in events:
            highlight = (
                hit.meta.highlight.title[0]
                if hasattr(hit.meta, 'highlight')
                else hit.title
            )
            results.append({
                'id': hit.id,
                'type': 'event',
                'title': hit.title,
                'url': f'/events/{hit.id}',
                'created_at': hit.created_at,
                'highlight': highlight,
                'additional_info': {
                    'event_date': hit.event_date,
                    'location': hit.location
                }
            })
        return results

    @staticmethod
    def get_suggestions(query):
        suggestions = []
        if len(query) < 2:
            return suggestions

        # В первую очередь ищем точные совпадения в вопросах
        search = QuestionDocument.search().query(
            Q('bool',
              should=[
                  # Точное совпадение фразы
                  Q('match_phrase', content={
                      'query': query,
                      'boost': 3,
                      'slop': 2
                  }),
                  # Семантически похожие вопросы
                  Q('multi_match', {
                      'query': query,
                      'fields': ['content^2', 'answer.content'],
                      'type': 'best_fields',
                      'minimum_should_match': '70%',
                      'fuzziness': 'AUTO'
                  }),
                  # Поиск по частям предложения
                  Q('match', content={
                      'query': query,
                      'operator': 'and',
                      'minimum_should_match': '60%'
                  })
              ]
              )
        )

        # Добавляем фильтр для отвеченных вопросов
        search = search.filter('term', is_answered=True)

        # Добавляем подсветку совпадений
        search = search.highlight(
            'content',
            'answer.content',
            pre_tags=['<em>'],
            post_tags=['</em>'],
            fragment_size=150,
            number_of_fragments=1
        )

        response = search[:5].execute()

        for hit in response:
            highlight = None
            if hasattr(hit.meta, 'highlight'):
                if hasattr(hit.meta.highlight, 'content'):
                    highlight = hit.meta.highlight.content[0]
                elif hasattr(hit.meta.highlight, 'answer.content'):
                    highlight = hit.meta.highlight['answer.content'][0]

            suggestion = {
                'text': highlight if highlight else hit.content[:100],
                'type': 'question',
                'url': f"/questions/{hit.id}",
                'is_answered': hit.is_answered,
                'score': hit.meta.score
            }
            suggestions.append(suggestion)

        # После этого добавляем результаты из других типов документов
        for doc_class in [ArticleDocument, LessonDocument, EventDocument]:
            search = doc_class.search().query(
                Q('multi_match',
                  query=query,
                  fields=['title^3', 'content^2'],
                  type='best_fields',
                  minimum_should_match='70%',
                  fuzziness=1
                  )
            )
            response = search[:2].execute()

            for hit in response:
                suggestion = {
                    'text': hit.title if hasattr(hit, 'title') else hit.content[:100],
                    'type': doc_class._index._name,
                    'url': f"/{doc_class._index._name}/{hit.id}",
                    'score': hit.meta.score
                }
                suggestions.append(suggestion)

        # Сортируем все результаты по релевантности
        suggestions.sort(key=lambda x: x.get('score', 0), reverse=True)
        return suggestions[:5]