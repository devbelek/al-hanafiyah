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
            highlight = None
            if hasattr(hit.meta, 'highlight') and hasattr(hit.meta.highlight, 'content'):
                highlight = hit.meta.highlight.content[0]
            else:
                highlight = hit.content if hasattr(hit, 'content') else ""

            results.append({
                'id': hit.id if hasattr(hit, 'id') else 0,
                'type': 'question',
                'content': hit.content if hasattr(hit, 'content') else "",
                'url': f'/questions/{hit.id}' if hasattr(hit, 'id') else "",
                'created_at': hit.created_at if hasattr(hit, 'created_at') else None,
                'highlight': highlight,
                'additional_info': {
                    'is_answered': hit.is_answered if hasattr(hit, 'is_answered') else False,
                    'telegram': hit.telegram if hasattr(hit, 'telegram') else ""
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

            title = hit.title if hasattr(hit, 'title') else "Без названия"

            results.append({
                'id': hit.id if hasattr(hit, 'id') else 0,
                'type': 'article',
                'title': title,
                'slug': hit.slug if hasattr(hit, 'slug') else "",
                'url': f'/articles/{hit.slug}' if hasattr(hit, 'slug') else "",
                'created_at': hit.created_at if hasattr(hit, 'created_at') else None,
                'highlight': highlight or title
            })
        return results

    @staticmethod
    def _format_lessons(lessons):
        results = []
        for hit in lessons:
            # Проверяем, что module существует
            if not hasattr(hit, 'module'):
                continue

            highlight = hit.module.name if hasattr(hit.module, 'name') else ""

            if hasattr(hit.meta, 'highlight'):
                if hasattr(hit.meta.highlight, 'module.name'):
                    highlight = hit.meta.highlight['module.name'][0]

            additional_info = {}
            if hasattr(hit.module, 'topic'):
                additional_info['topic'] = hit.module.topic.name if hasattr(hit.module.topic, 'name') else ""
                if hasattr(hit.module.topic, 'category') and hasattr(hit.module.topic.category, 'name'):
                    additional_info['category'] = hit.module.topic.category.name
                else:
                    additional_info['category'] = ""
            else:
                additional_info = {'topic': "", 'category': ""}

            results.append({
                'id': hit.id if hasattr(hit, 'id') else 0,
                'type': 'lesson',
                'title': hit.module.name if hasattr(hit.module, 'name') else "",
                'url': f'/lessons/{hit.slug}' if hasattr(hit, 'slug') else "",
                'created_at': hit.created_at if hasattr(hit, 'created_at') else None,
                'highlight': highlight,
                'additional_info': additional_info
            })
        return results

    @staticmethod
    def find_similar_questions(text, limit=3):
        if len(text) < 2:
            return []

        try:
            words = text.split()
            if words:
                search_text = words[0]
            else:
                search_text = text

            search = QuestionDocument.search().query(
                Q('multi_match',
                  query=search_text,
                  fields=['content^2'],
                  type='best_fields',
                  minimum_should_match='20%',
                  fuzziness='AUTO')
            )

            search = search.filter('term', is_answered=True)
            response = search[:limit].execute()

            results = []
            for hit in response:
                results.append({
                    'id': hit.id,
                    'content': hit.content,
                    'created_at': hit.created_at,
                    'is_answered': hit.is_answered,
                    'similarity_score': hit.meta.score
                })

            return results
        except Exception as e:
            print(f"Ошибка при поиске похожих вопросов: {e}")
            return []

    @staticmethod
    def _format_events(events):
        results = []
        for hit in events:
            title = hit.title if hasattr(hit, 'title') else "Без названия"

            highlight = title
            if hasattr(hit.meta, 'highlight'):
                if hasattr(hit.meta.highlight, 'title') and len(hit.meta.highlight.title) > 0:
                    highlight = hit.meta.highlight.title[0]
                elif hasattr(hit.meta.highlight, 'description') and len(hit.meta.highlight.description) > 0:
                    highlight = hit.meta.highlight.description[0]

            additional_info = {}
            if hasattr(hit, 'event_date'):
                additional_info['event_date'] = hit.event_date
            if hasattr(hit, 'location'):
                additional_info['location'] = hit.location

            results.append({
                'id': hit.id if hasattr(hit, 'id') else 0,
                'type': 'event',
                'title': title,
                'url': f'/events/{hit.id}' if hasattr(hit, 'id') else "",
                'created_at': hit.created_at if hasattr(hit, 'created_at') else None,
                'highlight': highlight,
                'additional_info': additional_info
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

        for doc_class in [ArticleDocument, LessonDocument, EventDocument]:
            try:
                search = doc_class.search().query(
                    Q('multi_match',
                      query=query,
                      fields=['title^3', 'content^2'] if doc_class != LessonDocument else ['module.name^2'],
                      type='best_fields',
                      minimum_should_match='70%',
                      fuzziness=1
                      )
                )
                response = search[:2].execute()

                for hit in response:
                    # Безопасное получение текста
                    if doc_class == ArticleDocument:
                        text = hit.title if hasattr(hit, 'title') else hit.content[:100] if hasattr(hit,
                                                                                                    'content') else "Без названия"
                    elif doc_class == LessonDocument:
                        text = hit.module.name if hasattr(hit, 'module') and hasattr(hit.module, 'name') else "Урок"
                    elif doc_class == EventDocument:
                        text = hit.title if hasattr(hit, 'title') else "Мероприятие"
                    else:
                        text = "Результат поиска"

                    suggestion = {
                        'text': text,
                        'type': doc_class._index._name,
                        'url': f"/{doc_class._index._name}/{hit.id}" if hasattr(hit, 'id') else "#",
                        'score': hit.meta.score if hasattr(hit.meta, 'score') else 0
                    }
                    suggestions.append(suggestion)
            except Exception as e:
                # Логирование ошибки, но продолжаем обработку
                print(f"Ошибка при поиске в {doc_class._index._name}: {e}")