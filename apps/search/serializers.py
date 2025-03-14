from rest_framework import serializers


class SearchResultSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    type = serializers.CharField()
    title = serializers.CharField(required=False)
    content = serializers.CharField(required=False)
    url = serializers.CharField()
    created_at = serializers.DateTimeField()
    highlight = serializers.CharField(required=False)
    additional_info = serializers.DictField(required=False)


class SearchSuggestionSerializer(serializers.Serializer):
    text = serializers.CharField()
    type = serializers.CharField()
    url = serializers.CharField()