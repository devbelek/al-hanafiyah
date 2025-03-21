from rest_framework import serializers
from .models import Article
from apps.lessons.serializers import UstazProfileSerializer


class ArticleSerializer(serializers.ModelSerializer):
    similar_articles = serializers.SerializerMethodField()
    author_details = UstazProfileSerializer(source='author', read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'content', 'short_description', 'image', 'image_url', 'created_at',
            'updated_at', 'slug', 'similar_articles',
            'author', 'author_details', 'is_moderated'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_similar_articles(self, obj):
        similar = Article.objects.filter(
            is_moderated=True
        ).exclude(id=obj.id)[:3]
        return ArticleListSerializer(similar, many=True).data

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class ArticleListSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ['id', 'title', 'content', 'slug', 'created_at', 'author_name', 'image', 'image_url']

    def get_author_name(self, obj):
        if obj.author:
            return "Устаз"
        return ""

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

    def get_content(self, obj):
        return obj.content