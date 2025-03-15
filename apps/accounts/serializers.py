from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile
from google.oauth2 import id_token
from google.auth.transport import requests
from django.conf import settings


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['avatar', 'telegram', 'is_ustaz']


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']
        read_only_fields = ['id']

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if profile_data:
            profile = instance.profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

        instance.save()
        return instance


class UserPublicSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()
    telegram = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'date_joined', 'avatar', 'telegram']

    def get_avatar(self, obj):
        if hasattr(obj, 'profile') and obj.profile.avatar:
            return obj.profile.avatar.url
        return None

    def get_telegram(self, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.telegram
        return None


class GoogleAuthSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)

    def validate_token(self, value):
        try:
            idinfo = id_token.verify_oauth2_token(
                value,
                requests.Request(),
                settings.GOOGLE_OAUTH2_CLIENT_ID
            )

            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise serializers.ValidationError("Wrong issuer")

            return idinfo
        except ValueError:
            raise serializers.ValidationError("Invalid token")

    def validate(self, attrs):
        idinfo = attrs['token']

        user_data = {
            'email': idinfo.get('email'),
            'first_name': idinfo.get('given_name', ''),
            'last_name': idinfo.get('family_name', ''),
            'username': idinfo.get('email').split('@')[0],
            'picture': idinfo.get('picture', '')
        }

        attrs['user_data'] = user_data
        return attrs