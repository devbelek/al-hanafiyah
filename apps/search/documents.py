from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from django.utils.html import strip_tags
from ckeditor.fields import RichTextField
from apps.questions.models import Question, Answer
from apps.articles.models import Article
from apps.events.models import OfflineEvent
from apps.lessons.models import Lesson, Module, Topic, Category


class BaseDocument(Document):
    @classmethod
    def to_field(cls, field_name, django_field):
        if isinstance(django_field, RichTextField):
            return fields.TextField()
        return super().to_field(field_name, django_field)


@registry.register_document
class QuestionDocument(BaseDocument):
    answer = fields.NestedField(properties={
        'content': fields.TextField(),
        'created_at': fields.DateField(),
    })

    class Index:
        name = 'questions'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }

    class Django:
        model = Question
        fields = [
            'id',
            'content',
            'telegram',
            'is_answered',
            'created_at',
        ]
        related_models = [Answer]

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, Answer):
            return related_instance.question


@registry.register_document
class ArticleDocument(BaseDocument):
    class Index:
        name = 'articles'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }

    class Django:
        model = Article
        fields = [
            'id',
            'title',
            'content',
            'created_at',
            'updated_at',
            'slug',
        ]


@registry.register_document
class LessonDocument(BaseDocument):
    module = fields.ObjectField(properties={
        'name': fields.TextField(),
        'topic': fields.ObjectField(properties={
            'name': fields.TextField(),
            'category': fields.ObjectField(properties={
                'name': fields.TextField(),
            })
        })
    })

    class Index:
        name = 'lessons'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }

    class Django:
        model = Lesson
        fields = [
            'id',
            'media_type',
            'is_intro',
            'order',
            'created_at',
            'slug',
        ]


@registry.register_document
class EventDocument(BaseDocument):
    class Index:
        name = 'events'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }

    class Django:
        model = OfflineEvent
        fields = [
            'id',
            'title',
            'description',
            'event_date',
            'location',
            'created_at',
        ]