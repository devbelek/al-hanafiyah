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


COMMON_ANALYZER_SETTINGS = {
    'analysis': {
        'analyzer': {
            'custom_analyzer': {
                'type': 'custom',
                'tokenizer': 'standard',
                'char_filter': ['html_strip'],
                'filter': [
                    'lowercase',
                    'word_delimiter',
                    'kyrgyz_stop',
                    'synonym_filter',
                    'kyrgyz_ngram'
                ]
            }
        },
        'filter': {
            'kyrgyz_stop': {
                'type': 'stop',
                'stopwords': [
                    # Базовые стоп-слова
                    'жана', 'менен', 'да', 'дагы', 'деле', 'эмне', 'кандай',
                    'кайсы', 'кайда', 'качан', 'бул', 'ал', 'ошол', 'эмес',
                    'керек', 'болуш', 'үчүн', 'гана', 'дейт', 'деген', 'болот',
                    'болду', 'болгон', 'эле', 'эми', 'ошондой', 'андай',
                    # Дополнительные стоп-слова
                    'кантип', 'кандайча', 'канча', 'кайсыл',
                    'болобу', 'болоор', 'болсо', 'болуп',
                    'керекпи', 'керектүү', 'зарыл',
                    'кылуу', 'кылса', 'кылган',
                    'үчүн', 'сыяктуу', 'окшош'
                ]
            },
            'kyrgyz_ngram': {
                'type': 'ngram',
                'min_gram': 3,
                'max_gram': 4
            },
            'synonym_filter': {
                'type': 'synonym',
                'lenient': True,
                'synonyms': [
                    # Базовые синонимы намаза
                    'намаз, намас, окуу, беш убак, окуйбуз, окулат',
                    # Действия с намазом
                    'окуу => намаз окуу, намаз кылуу',
                    'окулат => намаз окулат',
                    'окуйбуз => намаз окуйбуз',
                    'беш убак => беш убак намаз',
                    'жума => жума намаз',
                    'айт => айт намаз, курман айт намаз, орозо айт намаз',

                    # Даарат
                    'даарат, дарат, вуду, тазалануу',
                    'даарат алуу, дарат алуу, тазалануу',
                    'жуунуу => даарат алуу, гусл алуу',
                    'гусул => гусл, гусул, гусл алуу, толук жуунуу, толук даарат',
                    'таяммум => таяммум, таямум, топурак даарат',

                    # Орозо
                    'орозо, ураза, карыз, роза',
                    'кармоо => орозо кармоо',
                    'тутуу => орозо тутуу',
                    'оозачуу => ифтар',
                    'саарлык => оозбүтүрүү',

                    # Нике
                    'нике, никах, нека, үйлөнүү',
                    'кыюу => нике кыюу',
                    'окуу => нике окуу',

                    # Ажылык
                    'ажылык, хадж, ажыга баруу, зыярат',
                    'барса болот => кандай барса болот, кантип барса болот',

                    # Садака
                    'садака, садага, кайыр, жардам',
                    'берүү => садака берүү, кайыр берүү',
                    'сооп => садаканын сообу, жардамдын сообу',

                    # Места и люди
                    'мечит, мечить, мечет, намазкана, жайнамаз',
                    'имам, молдо, олуя, дин башчы',
                    'медресе, медреса, диний мектеп, куран мектеби',
                    'устаз, устат, молдоке, дин кызматкери, аалым',

                    # Религиозные понятия
                    'сүннөт, суннат, пайгамбардын жолу, сүннөткө жатат',
                    'парз, фарз, парыз, милдет, милдеттүү',
                    'важип, ваажип, зарыл, керектүү',
                    'макрух, макыруу, жаман, жакшы эмес',
                    'харам, арам, тыюу салынган',
                    'адал, халал, уруксат берилген',

                    # Праздники и обряды
                    'айт, майрам, курман айт, орозо айт',
                    'жума, жума намаз, жума күн',
                    'садака, садага, кайыр, жардам',
                    'зекет, зекат, малдын зекети',

                    # Одежда
                    'хиджаб, жоолук, жаулук, баш кийим',
                    'намазкап, жайнамаз, намаз төшөк',

                    # Шариат
                    'шариат, шарият, ислам мыйзамы',
                    'куран, куран окуу, китеп',
                    'азан, эзен, намазга чакыруу',
                    'такбир, текбир, алла акбар',

                    # Духовные понятия
                    'тообо, тоба, истигфар, кечирим суроо',
                    'барака, береке, ырыскы',
                    'ыйман, иман, ишеним',
                    'шүгүр, шүкүр, ыраазычылык',

                    # Рамадан
                    'рамазан, рамадан, орозо айы',
                    'ифтар, оозачуу, орозо ачуу',
                    'саарлык, саары, оозбүтүрүү',

                    # Коран
                    'тажвид, тажуид, куран окуу эрежеси',
                    'хафиз, хафыз, куран жаттаган',

                    # Похороны
                    'жаназа, жаназа намаз, акыркы коштошуу',
                    'мүрзө, көр, кабыр, бейит'
                ]
            }
        }
    }
}


@registry.register_document
class QuestionDocument(BaseDocument):
    answer = fields.NestedField(properties={
        'content': fields.TextField(
            analyzer='custom_analyzer',
            search_analyzer='custom_analyzer',
            term_vector='with_positions_offsets'
        ),
        'created_at': fields.DateField(),
    })

    content = fields.TextField(
        analyzer='custom_analyzer',
        search_analyzer='custom_analyzer',
        term_vector='with_positions_offsets'
    )

    class Index:
        name = 'questions'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
            'max_ngram_diff': 3,
            **COMMON_ANALYZER_SETTINGS
        }

    class Django:
        model = Question
        fields = [
            'id',
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
    title = fields.TextField(analyzer='custom_analyzer')
    content = fields.TextField(analyzer='custom_analyzer')

    class Index:
        name = 'articles'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
            'max_ngram_diff': 3,
            **COMMON_ANALYZER_SETTINGS
        }

    class Django:
        model = Article
        fields = [
            'id',
            'created_at',
            'updated_at',
            'slug',
        ]


@registry.register_document
class LessonDocument(BaseDocument):
    module = fields.ObjectField(properties={
        'name': fields.TextField(analyzer='custom_analyzer'),
        'topic': fields.ObjectField(properties={
            'name': fields.TextField(analyzer='custom_analyzer'),
            'category': fields.ObjectField(properties={
                'name': fields.TextField(analyzer='custom_analyzer'),
            })
        })
    })

    class Index:
        name = 'lessons'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
            'max_ngram_diff': 3,
            **COMMON_ANALYZER_SETTINGS
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
    title = fields.TextField(analyzer='custom_analyzer')
    description = fields.TextField(analyzer='custom_analyzer')
    location = fields.TextField(analyzer='custom_analyzer')

    class Index:
        name = 'events'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
            'max_ngram_diff': 3,
            **COMMON_ANALYZER_SETTINGS
        }

    class Django:
        model = OfflineEvent
        fields = [
            'id',
            'event_date',
            'created_at',
        ]