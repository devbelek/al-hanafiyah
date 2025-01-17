from rest_framework import serializers
from .models import Article


class ArticleSerializer(serializers.ModelSerializer):
    similar_articles = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'content', 'created_at',
            'updated_at', 'slug', 'similar_articles'
        ]
        read_only_fields = ['author', 'created_at', 'updated_at']

    def get_similar_articles(self, obj):
        similar = Article.objects.filter(
            is_moderated=True
        ).exclude(id=obj.id)[:3]
        return ArticleListSerializer(similar, many=True).data


class ArticleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'title', 'slug', 'created_at']
