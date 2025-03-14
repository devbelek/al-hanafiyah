from drf_yasg import openapi

additional_info_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'is_answered': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Флаг наличия ответа (для вопросов)'),
        'telegram': openapi.Schema(type=openapi.TYPE_STRING, description='Telegram пользователя (для вопросов)'),
        'event_date': openapi.Schema(type=openapi.TYPE_STRING, format='date-time', description='Дата мероприятия (для событий)'),
        'location': openapi.Schema(type=openapi.TYPE_STRING, description='Место проведения (для событий)'),
        'topic': openapi.Schema(type=openapi.TYPE_STRING, description='Название темы (для уроков)'),
        'category': openapi.Schema(type=openapi.TYPE_STRING, description='Название категории (для уроков)')
    }
)

search_result_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID результата'),
        'type': openapi.Schema(
            type=openapi.TYPE_STRING,
            enum=['question', 'article', 'lesson', 'event'],
            description='Тип контента'
        ),
        'title': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='Заголовок (для статей, уроков, событий)'
        ),
        'content': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='Содержимое (для вопросов)'
        ),
        'url': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='URL для просмотра контента'
        ),
        'created_at': openapi.Schema(
            type=openapi.TYPE_STRING,
            format='date-time',
            description='Дата создания'
        ),
        'highlight': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='Подсвеченный фрагмент текста с найденным запросом'
        ),
        'additional_info': additional_info_schema
    },
    required=['id', 'type', 'url', 'created_at', 'highlight']
)

search_response = openapi.Response(
    description='Результаты поиска',
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'results': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=search_result_schema,
                description='Список найденных результатов'
            ),
            'total': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description='Общее количество найденных результатов'
            ),
            'page': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description='Текущая страница'
            ),
            'size': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description='Размер страницы'
            )
        },
        required=['results', 'total', 'page', 'size']
    )
)

search_suggestion_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'text': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='Текст подсказки'
        ),
        'type': openapi.Schema(
            type=openapi.TYPE_STRING,
            enum=['questions', 'articles', 'lessons', 'events'],
            description='Тип контента'
        ),
        'url': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='URL для перехода'
        )
    },
    required=['text', 'type', 'url']
)

suggestions_response = openapi.Response(
    description='Поисковые подсказки',
    schema=openapi.Schema(
        type=openapi.TYPE_ARRAY,
        items=search_suggestion_schema
    )
)


'''
1. Глобальный поиск
`GET /api/search/`

Параметры запроса:
- `q` (обязательный) - поисковый запрос
- `type` (опциональный) - тип контента: 
  - `all` (по умолчанию) - все типы
  - `questions` - только вопросы
  - `articles` - только статьи
  - `lessons` - только уроки
  - `events` - только мероприятия
- `page` (опциональный) - номер страницы (по умолчанию: 1)
- `size` (опциональный) - количество результатов на страницу (по умолчанию: 10)

Пример ответа:
{
    "results": [
        {
            "id": 1,
            "type": "article",
            "title": "Как правильно совершать намаз",
            "url": "/articles/kak-pravilno-sovershat-namaz",
            "created_at": "2025-01-18T12:00:00Z",
            "highlight": "Как правильно совершать <em>намаз</em>",
            "additional_info": null
        },
        {
            "id": 2,
            "type": "question",
            "content": "Вопрос про намаз",
            "url": "/questions/2",
            "created_at": "2025-01-18T13:00:00Z",
            "highlight": "Вопрос про <em>намаз</em>",
            "additional_info": {
                "is_answered": true,
                "telegram": "@user123"
            }
        }
    ],
    "total": 2,
    "page": 1,
    "size": 10
}

Поисковые подсказки
GET /api/search/suggestions/
Параметры запроса:

q (обязательный) - текст для подсказок

Пример ответа:
[
    {
        "text": "намаз",
        "type": "article",
        "url": "/articles/1"
    },
    {
        "text": "намаз утренний",
        "type": "question",
        "url": "/questions/2"
    }
]


Примеры использования (React + TypeScript)


typescriptCopy// types/search.ts
interface SearchResult {
    id: number;
    type: 'article' | 'question' | 'lesson' | 'event';
    title?: string;
    content?: string;
    url: string;
    created_at: string;
    highlight: string;
    additional_info?: {
        is_answered?: boolean;
        telegram?: string;
        event_date?: string;
        location?: string;
        topic?: string;
        category?: string;
    };
}

interface SearchResponse {
    results: SearchResult[];
    total: number;
    page: number;
    size: number;
}

interface SearchSuggestion {
    text: string;
    type: string;
    url: string;
}

// api/search.ts
const SEARCH_API = {
    search: async (
        query: string,
        type: string = 'all',
        page: number = 1,
        size: number = 10
    ): Promise<SearchResponse> => {
        const params = new URLSearchParams({
            q: query,
            type,
            page: String(page),
            size: String(size)
        });

        const response = await fetch(`/api/search/?${params}`);
        if (!response.ok) {
            throw new Error('Search failed');
        }
        return response.json();
    },

    getSuggestions: async (query: string): Promise<SearchSuggestion[]> => {
        const response = await fetch(`/api/search/suggestions/?q=${query}`);
        if (!response.ok) {
            throw new Error('Failed to get suggestions');
        }
        return response.json();
    }
};

// components/Search/SearchInput.tsx
import React, { useState, useEffect } from 'react';
import { debounce } from 'lodash';

export const SearchInput: React.FC = () => {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState<SearchResult[]>([]);
    const [loading, setLoading] = useState(false);
    const [suggestions, setSuggestions] = useState<SearchSuggestion[]>([]);

    // Отложенный поиск
    const debouncedSearch = useMemo(
        () => debounce(async (searchQuery: string) => {
            if (searchQuery.length < 2) return;
            
            setLoading(true);
            try {
                const data = await SEARCH_API.search(searchQuery);
                setResults(data.results);
            } catch (error) {
                console.error('Search error:', error);
            } finally {
                setLoading(false);
            }
        }, 300),
        []
    );

    // Получение подсказок
    const debouncedSuggestions = useMemo(
        () => debounce(async (searchQuery: string) => {
            if (searchQuery.length < 2) return;
            
            try {
                const data = await SEARCH_API.getSuggestions(searchQuery);
                setSuggestions(data);
            } catch (error) {
                console.error('Suggestions error:', error);
            }
        }, 150),
        []
    );

    useEffect(() => {
        if (query) {
            debouncedSearch(query);
            debouncedSuggestions(query);
        }
        return () => {
            debouncedSearch.cancel();
            debouncedSuggestions.cancel();
        };
    }, [query]);

    return (
        <div className="search-container">
            <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Поиск..."
                className="search-input"
            />

            {/* Подсказки */}
            {suggestions.length > 0 && (
                <ul className="suggestions-list">
                    {suggestions.map((suggestion, index) => (
                        <li
                            key={index}
                            className="suggestion-item"
                            onClick={() => {
                                setQuery(suggestion.text);
                                window.location.href = suggestion.url;
                            }}
                        >
                            {suggestion.text}
                        </li>
                    ))}
                </ul>
            )}

            {/* Результаты */}
            {loading ? (
                <div className="search-loading">Поиск...</div>
            ) : (
                <div className="search-results">
                    {results.map((result) => (
                        <div key={result.id} className="search-result-item">
                            <a href={result.url} className="result-title">
                                {result.title || result.content}
                            </a>
                            <div
                                className="result-highlight"
                                dangerouslySetInnerHTML={{
                                    __html: result.highlight
                                }}
                            />
                            <div className="result-meta">
                                <span className="result-type">{result.type}</span>
                                <span className="result-date">
                                    {new Date(result.created_at).toLocaleDateString()}
                                </span>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};
'''