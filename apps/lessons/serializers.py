from rest_framework import serializers
from .models import Category, Topic, Module, Lesson, Comment, UstazProfile, UstazGallery


class UstazGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = UstazGallery
        fields = ['id', 'image', 'description']


class UstazProfileSerializer(serializers.ModelSerializer):
    photos = UstazGallerySerializer(many=True, read_only=True)

    class Meta:
        model = UstazProfile
        fields = ['biography', 'achievements', 'photos']


class CommentSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    has_user_liked = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()
    user_id = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'content', 'username', 'avatar', 'like_count',
                  'has_user_liked', 'created_at', 'replies', 'parent', 'user_id']
        read_only_fields = ['like_count', 'username', 'avatar', 'has_user_liked', 'replies', 'user_id']

    def get_user_id(self, obj):
        if obj.user:
            return obj.user.id
        return None

    def get_username(self, obj):
        if obj.user:
            return obj.user.username
        return obj.telegram

    def get_avatar(self, obj):
        if obj.user and obj.user.profile.avatar:
            return obj.user.profile.avatar.url
        return None

    def get_like_count(self, obj):
        return obj.likes.count()

    def get_has_user_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False

    def get_replies(self, obj):
        replies = obj.replies.all()
        if hasattr(obj, 'order_by_likes') and obj.order_by_likes:
            from django.db.models import Count
            replies = replies.annotate(likes_count=Count('likes')).order_by('-likes_count', '-created_at')
        else:
            replies = replies.order_by('-created_at')
        return CommentSerializer(replies, many=True, context=self.context).data


class LessonSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = [
            'id', 'module', 'media_type',
            'media_file', 'thumbnail_url', 'is_intro', 'order', 'created_at',
            'updated_at', 'slug', 'comments'
        ]
        read_only_fields = ['created_at', 'updated_at', 'thumbnail_url']

    def get_thumbnail_url(self, obj):
        if obj.thumbnail:
            return obj.thumbnail.url
        return None

    def get_comments(self, obj):
        comments = obj.comments.filter(parent=None)
        sort_by = self.context.get('sort_comments_by', 'newest')

        if sort_by == 'popular':
            from django.db.models import Count
            comments = comments.annotate(likes_count=Count('likes')).order_by('-likes_count', '-created_at')
            for comment in comments:
                comment.order_by_likes = True
        else:
            comments = comments.order_by('-created_at')

        serializer = CommentSerializer(comments, many=True, context=self.context)
        return serializer.data


class ModuleSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = ['id', 'name', 'topic', 'slug', 'lessons']


class TopicSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, read_only=True)

    class Meta:
        model = Topic
        fields = ['id', 'name', 'category', 'slug', 'modules']


class CategorySerializer(serializers.ModelSerializer):
    topics = TopicSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'topics']