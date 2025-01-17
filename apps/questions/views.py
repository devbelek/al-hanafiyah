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


class QuestionViewSet(viewsets.ModelViewSet):
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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Поиск похожих вопросов
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

            question = serializer.save()
            return Response(
                QuestionDetailSerializer(question).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=400)

    @action(detail=False)
    def answered(self, request):
        """Получение отвеченных вопросов"""
        questions = self.get_queryset().filter(is_answered=True)
        page = self.paginate_queryset(questions)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True)
    def similar(self, request, pk=None):
        """Получение похожих вопросов"""
        question = self.get_object()
        similar = Question.objects.filter(
            content__icontains=question.content,
            is_answered=True
        ).exclude(id=question.id)[:3]

        serializer = QuestionListSerializer(similar, many=True)
        return Response(serializer.data)