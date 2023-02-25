from rest_framework import serializers

from .models import Tag


class TagsSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для оторабражения, создания, изменений тегов
    """
    class Meta:
        model = Tag
        fields = ['id', 'name']
