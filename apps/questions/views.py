from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Question
from .serializers import (
    QuestionListSerializer,
    QuestionDetailSerializer,
    QuestionCreateSerializer
)
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import permissions


class QuestionViewSet(viewsets.ModelViewSet):
    """
    API для работы с вопросами и ответами.
    """
    queryset = Question.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_answered']
    search_fields = ['content']
    http_method_names = ['get', 'post']

    def get_serializer_class(self):
        if self.action == 'create':
            return QuestionCreateSerializer
        if self.action == 'retrieve':
            return QuestionDetailSerializer
        return QuestionListSerializer

    @swagger_auto_schema(
        operation_description="Получение списка всех вопросов",
        manual_parameters=[
            openapi.Parameter(
                'is_answered',
                openapi.IN_QUERY,
                description="Фильтр по наличию ответа (true, false)",
                type=openapi.TYPE_BOOLEAN
            ),
            openapi.Parameter(
                'search',
                openapi.IN_QUERY,
                description="Поиск по содержанию вопроса",
                type=openapi.TYPE_STRING
            )
        ],
        responses={
            200: openapi.Response(
                description="Список вопросов",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'content': openapi.Schema(type=openapi.TYPE_STRING),
                            'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                            'is_answered': openapi.Schema(type=openapi.TYPE_BOOLEAN)
                        }
                    )
                )
            )
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Получение подробной информации о вопросе",
        responses={
            200: openapi.Response(
                description="Детальная информация о вопросе",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'content': openapi.Schema(type=openapi.TYPE_STRING),
                        'telegram': openapi.Schema(type=openapi.TYPE_STRING),
                        'is_answered': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                        'answer': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'content': openapi.Schema(type=openapi.TYPE_STRING),
                                'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME)
                            }
                        )
                    }
                )
            ),
            404: "Вопрос не найден"
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Создание нового вопроса",
        request_body=QuestionCreateSerializer,
        responses={
            201: openapi.Response(
                description="Созданный вопрос",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'content': openapi.Schema(type=openapi.TYPE_STRING),
                        'telegram': openapi.Schema(type=openapi.TYPE_STRING),
                        'is_answered': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME)
                    }
                )
            ),
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'similar_questions': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'content': openapi.Schema(type=openapi.TYPE_STRING),
                                'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                                'is_answered': openapi.Schema(type=openapi.TYPE_BOOLEAN)
                            }
                        )
                    )
                },
                description="Возвращается, если найдены похожие вопросы"
            ),
            400: "Некорректные данные",
            401: "Необходима авторизация"
        }
    )
    def create(self, request, *args, **kwargs):
        """
        Создание нового вопроса.
        Если найдены похожие вопросы, они будут возвращены вместо создания нового.
        """
        serializer = self.get_serializer(data=request.data)

        if not request.user.is_authenticated:
            return Response(
                {'error': 'Авторизуйтесь для отправки вопроса'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not request.user.profile.telegram:
            return Response(
                {'error': 'Заполните Telegram в профиле для получения ответа'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if serializer.is_valid():
            similar_questions = Question.objects.filter(
                content__icontains=request.data.get('content'),
                is_answered=True
            )[:3]

            if similar_questions.exists():
                return Response({
                    'similar_questions': QuestionListSerializer(
                        similar_questions, many=True
                    ).data
                })

            question = serializer.save(
                user=request.user,
                telegram=request.user.profile.telegram
            )

            from apps.notifications.services import send_admin_notification
            send_admin_notification(
                title='Новый вопрос',
                message=question.content[:100],
                notification_type='new_question',
                content_object=question,
                url=f'/admin/questions/question/{question.id}/change/'
            )

            return Response(
                QuestionDetailSerializer(question).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=400)

    @swagger_auto_schema(
        operation_description="Получение списка отвеченных вопросов",
        responses={
            200: openapi.Response(
                description="Список отвеченных вопросов",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'content': openapi.Schema(type=openapi.TYPE_STRING),
                            'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                            'is_answered': openapi.Schema(type=openapi.TYPE_BOOLEAN)
                        }
                    )
                )
            )
        }
    )
    @action(detail=False)
    def answered(self, request):
        """
        Получение списка отвеченных вопросов
        """
        questions = self.get_queryset().filter(is_answered=True)
        page = self.paginate_queryset(questions)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        operation_description="Получение списка вопросов текущего пользователя",
        manual_parameters=[
            openapi.Parameter(
                'is_answered',
                openapi.IN_QUERY,
                description="Фильтр по наличию ответа (true, false)",
                type=openapi.TYPE_BOOLEAN
            )
        ],
        responses={
            200: openapi.Response(
                description="Список вопросов пользователя",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'content': openapi.Schema(type=openapi.TYPE_STRING),
                            'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                            'is_answered': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            'answer': openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'content': openapi.Schema(type=openapi.TYPE_STRING),
                                    'created_at': openapi.Schema(type=openapi.TYPE_STRING,
                                                                 format=openapi.FORMAT_DATETIME)
                                }
                            )
                        }
                    )
                )
            ),
            401: "Необходима авторизация"
        }
    )
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_questions(self, request):
        """
        Получение списка вопросов текущего пользователя
        """
        user = request.user
        questions = self.get_queryset().filter(user=user)

        is_answered = request.query_params.get('is_answered')
        if is_answered is not None:
            is_answered = is_answered.lower() == 'true'
            questions = questions.filter(is_answered=is_answered)

        questions = questions.order_by('-created_at')

        page = self.paginate_queryset(questions)
        serializer = QuestionDetailSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        operation_description="Получение похожих вопросов",
        responses={
            200: openapi.Response(
                description="Список похожих вопросов",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'content': openapi.Schema(type=openapi.TYPE_STRING),
                            'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                            'is_answered': openapi.Schema(type=openapi.TYPE_BOOLEAN)
                        }
                    )
                )
            ),
            404: "Вопрос не найден"
        }
    )
    @action(detail=True)
    def similar(self, request, pk=None):
        """
        Получение похожих вопросов для указанного вопроса
        """
        question = self.get_object()
        similar = Question.objects.filter(
            content__icontains=question.content,
            is_answered=True
        ).exclude(id=question.id)[:3]

        serializer = QuestionListSerializer(similar, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Предварительная проверка на похожие вопросы",
        manual_parameters=[
            openapi.Parameter(
                'text',
                openapi.IN_QUERY,
                description="Текст вопроса для проверки",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'similar_questions': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'content': openapi.Schema(type=openapi.TYPE_STRING),
                                'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                                'is_answered': openapi.Schema(type=openapi.TYPE_BOOLEAN)
                            }
                        )
                    )
                }
            )
        }
    )
    @action(detail=False, methods=['get'])
    def similar_check(self, request):
        """
        Предварительная проверка текста вопроса на наличие похожих вопросов
        """
        text = request.query_params.get('text', '')
        if len(text) < 10:
            return Response({'similar_questions': []})

        similar_questions = Question.objects.filter(
            content__icontains=text,
            is_answered=True
        )[:5]

        serializer = QuestionListSerializer(similar_questions, many=True)
        return Response({'similar_questions': serializer.data})