from rest_framework import serializers

from .models import Room, RoomCategory, Photo
from ..tags.models import Tag


class RoomsCategoriesSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для оторабражения, создания, изменений категорий комнат
    """
    class Meta:
        model = RoomCategory
        fields = ['id', 'name', 'description', 'default_price',
                  'prepayment_percent', 'refund_percent',
                  'main_photo', 'floors', 'rooms_count', 'beds',
                  'square', 'is_hidden'
                  ]

    def __init__(self, *args, **kwargs):
        super(RoomsCategoriesSerializer, self).__init__(*args, **kwargs)

        # если фото и так загружено, то помечаем поле как необязательное
        if hasattr(self.instance, 'main_photo') and self.instance.main_photo is not None:
            self.fields['main_photo'].allow_empty_file = True
            self.fields['main_photo'].required = False

    def validate(self, data):
        if data['default_price'] <= 0:
            raise serializers.ValidationError({
                'price': 'Цена должна быть больше 0'
            })

        if data['prepayment_percent'] <= 0 or data['prepayment_percent'] > 100:
            raise serializers.ValidationError({
                'prepayment': 'Предоплата должна быть больше 0 и не больше 100'
            })

        if data['refund_percent'] <= 0 or data['refund_percent'] > 100:
            raise serializers.ValidationError({
                'refund': 'Возврат должен быть больше 0 и не больше 100"'
            })

        if data['rooms_count'] <= 0:
            raise serializers.ValidationError({
                'rooms_count': 'Кол-во комнат должно быть больше 0'
            })

        if data['floors'] <= 0:
            raise serializers.ValidationError({
                'floors': 'Кол-во этажей должно быть больше 0'
            })

        if data['beds'] <= 0:
            raise serializers.ValidationError({
                'beds': 'Кол-во спальных мест должно быть больше 0'
            })

        if data['square'] <= 0:
            raise serializers.ValidationError({
                'square': 'Площадь должна быть больше 0'
            })

        return super().validate(data)


class RoomsSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для оторабражения, создания, изменений номером
    """
    class Meta:
        model = Room
        fields = ['id', 'room_number', 'is_hidden']

    def validate(self, data):

        # получаем id комнаты
        if self.instance is not None:
            instance_id = self.instance.id
        else:
            instance_id = None

        # если есть не удаленная комната с таким же номером, то запрещаем создание
        if Room.objects.exclude(id=instance_id).filter(
                room_number=data['room_number'],
                date_deleted__isnull=True
        ).exists():
            raise serializers.ValidationError({
                'room_number': 'Уже существует комната с этим номером'
            })

        if data['room_number'] <= 0:
            raise serializers.ValidationError({
                'room_number': 'Номер комнаты должен быть больше 0'
            })

        return super().validate(data)


class CreatePhotoSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для создания доп. фотографий категорий номеров
    """
    class Meta:
        model = Photo
        fields = ['id', 'path']


class PhotosSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для отображения и измения номеров
    """

    # этот сериалайзер используется, для уже созданых объектов, поэтому фото уже есть и необязательно
    path = serializers.ImageField(allow_empty_file=True, required=False)

    class Meta:
        model = Photo
        fields = ['id', 'path', 'order']

    def validate(self, data):
        if data['order'] <= 0:
            raise serializers.ValidationError({
                'order': 'Порядковый номер должен быть больше 0'
            })

        # используется только при изменении, поменять местами может только с уже существуюшим фото
        if not self.instance.room_category.photos.filter(order=data['order']).exists():
            raise serializers.ValidationError({
                'order': 'Нет фото с таким порядковым номером'
            })

        return super().validate(data)


class CatTagsSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для добавления тегов к комнате
    """
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all())

    class Meta:
        model = RoomCategory
        fields = ['tags']

    def update(self, instance, validated_data):
        instance.tags.add(validated_data['tags'])
        return instance

