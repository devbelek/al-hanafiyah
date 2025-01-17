from rest_framework import serializers
from .models import Question, Answer


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'content', 'created_at']
        read_only_fields = ['created_at']


class QuestionListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка вопросов"""

    class Meta:
        model = Question
        fields = ['id', 'content', 'created_at', 'is_answered']


class QuestionDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для детального отображения вопроса"""
    answer = AnswerSerializer(read_only=True)

    class Meta:
        model = Question
        fields = [
            'id', 'content', 'telegram',
            'is_answered', 'created_at', 'answer'
        ]


class QuestionCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания вопроса"""

    class Meta:
        model = Question
        fields = ['content', 'telegram']