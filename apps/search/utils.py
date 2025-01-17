from elasticsearch_dsl import analyzer, token_filter, tokenizer


custom_analyzer = analyzer(
    'custom_analyzer',
    tokenizer=tokenizer('standard'),
    filter=[
        'lowercase',
        'stop',
        token_filter('russian_stemmer', type='stemmer', language='russian'),
        'word_delimiter'
    ]
)


def get_search_query_builder(query, fields, operator='or'):
    """
    Строит поисковый запрос с поддержкой нескольких языков
    """
    return {
        'query': {
            'multi_match': {
                'query': query,
                'fields': fields,
                'type': 'best_fields',
                'operator': operator,
                'fuzziness': 'AUTO'
            }
        }
    }


def format_highlight(highlight_field, default_text):
    """
    Форматирует подсвеченный текст
    """
    if highlight_field and len(highlight_field) > 0:
        return highlight_field[0]
    return default_text
