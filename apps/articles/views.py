from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Article
from .serializers import ArticleSerializer, ArticleListSerializer


class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Article.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['title', 'content']
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'list':
            return ArticleListSerializer
        return ArticleSerializer

    @action(detail=True, methods=['get'])
    def similar(self, request, slug=None):
        article = self.get_object()
        similar_articles = Article.objects.exclude(id=article.id)[:5]
        serializer = ArticleListSerializer(similar_articles, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def latest(self, request):
        latest_articles = self.get_queryset().order_by('-created_at')[:5]
        serializer = ArticleListSerializer(latest_articles, many=True)
        return Response(serializer.data)