from rest_framework import serializers

from .models import Sale
from ..rooms.models import RoomCategory


class SalesSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для CRUD операция над скидками
    """
    class Meta:
        model = Sale
        exclude = ['date_created', 'date_deleted', 'applies_to']

    def __init__(self, *args, **kwargs):
        super(SalesSerializer, self).__init__(*args, **kwargs)

        # если фото и так загружено, то помечаем поле как необязательное
        if hasattr(self.instance, 'image') and self.instance.image is not None:
            self.fields['image'].allow_empty_file = True
            self.fields['image'].required = False


class AppliesToSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для добавления элемента к скидке
    """
    applies_to = serializers.PrimaryKeyRelatedField(queryset=RoomCategory.objects.filter(date_deleted=None))

    class Meta:
        model = Sale
        fields = ['applies_to']

    def update(self, instance, validated_data):
        instance.applies_to.add(validated_data['applies_to'])
        return instance





