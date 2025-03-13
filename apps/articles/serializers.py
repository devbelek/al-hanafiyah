from rest_framework import serializers
from .models import Article
from apps.lessons.serializers import UstazProfileSerializer


class ArticleSerializer(serializers.ModelSerializer):
    similar_articles = serializers.SerializerMethodField()
    author_details = UstazProfileSerializer(source='author', read_only=True)

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'content', 'created_at',
            'updated_at', 'slug', 'similar_articles',
            'author', 'author_details', 'is_moderated'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_similar_articles(self, obj):
        similar = Article.objects.filter(
            is_moderated=True
        ).exclude(id=obj.id)[:3]
        return ArticleListSerializer(similar, many=True).data


class ArticleListSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ['id', 'title', 'slug', 'created_at', 'author_name']

    def get_author_name(self, obj):
        if obj.author:
            return "Устаз"
        return ""