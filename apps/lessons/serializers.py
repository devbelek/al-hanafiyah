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
    class Meta:
        model = Comment
        fields = ['id', 'content', 'telegram', 'helpful_count', 'created_at']
        read_only_fields = ['helpful_count']


class LessonSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Lesson
        fields = [
            'id', 'module', 'media_type',
            'media_file', 'is_intro', 'order','created_at',
            'updated_at', 'slug', 'comments'
        ]
        read_only_fields = ['created_at', 'updated_at']


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
