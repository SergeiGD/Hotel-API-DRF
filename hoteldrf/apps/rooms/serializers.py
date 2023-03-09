from django.db.models import Max
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from .models import Room, RoomCategory, Photo
from ..tags.models import Tag
from ..tags.serializers import TagsSerializer


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
        if 'default_price' in data and data['default_price'] <= 0:
            raise serializers.ValidationError({
                'price': 'Цена должна быть больше 0'
            })

        if 'prepayment_percent' in data and (data['prepayment_percent'] <= 0 or data['prepayment_percent'] > 100):
            raise serializers.ValidationError({
                'prepayment': 'Предоплата должна быть больше 0 и не больше 100'
            })

        if 'refund_percent' in data and (data['refund_percent'] <= 0 or data['refund_percent'] > 100):
            raise serializers.ValidationError({
                'refund': 'Возврат должен быть больше 0 и не больше 100'
            })

        if 'rooms_count' in data and data['rooms_count'] <= 0:
            raise serializers.ValidationError({
                'rooms_count': 'Кол-во комнат должно быть больше 0'
            })

        if 'floors' in data and data['floors'] <= 0:
            raise serializers.ValidationError({
                'floors': 'Кол-во этажей должно быть больше 0'
            })

        if 'beds' in data and data['beds'] <= 0:
            raise serializers.ValidationError({
                'beds': 'Кол-во спальных мест должно быть больше 0'
            })

        if 'square' in data and data['square'] <= 0:
            raise serializers.ValidationError({
                'square': 'Площадь должна быть больше 0'
            })

        return super().validate(data)


class RoomsSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для оторабражения, создания, изменений номером
    """
    room_number = serializers.IntegerField(required=False)

    class Meta:
        model = Room
        fields = ['id', 'room_number']

    def validate(self, data):

        # получаем id комнаты
        if self.instance is not None:
            instance_id = self.instance.id
        else:
            instance_id = None

        # если есть не удаленная комната с таким же номером, то запрещаем создание
        if 'room_number' in data and Room.objects.exclude(id=instance_id).filter(
                room_number=data['room_number'],
                date_deleted__isnull=True
        ).exists():
            raise serializers.ValidationError({
                'room_number': 'Уже существует комната с этим номером'
            })

        if 'room_number' in data and data['room_number'] <= 0:
            raise serializers.ValidationError({
                'room_number': 'Номер комнаты должен быть больше 0'
            })

        return super().validate(data)

    def create(self, validated_data):
        """
        Переопределенный create для установки room_number
        """
        room_number = validated_data.get('room_number', None)
        if room_number is None:
            # если не установили вручную, то берем крайний + 1
            room_number = Room.objects.filter(
                date_deleted=None
            ).aggregate(Max('room_number')).get('room_number__max', 0) + 1
        return Room.objects.create(room_number=room_number, room_category=validated_data['room_category'])


class CreatePhotoSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для создания доп. фотографий категорий номеров
    """
    order = serializers.ReadOnlyField()

    class Meta:
        model = Photo
        fields = ['id', 'path', 'order']


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
        if 'order' in data and data['order'] <= 0:
            raise serializers.ValidationError({
                'order': 'Порядковый номер должен быть больше 0'
            })

        # используется только при изменении, поменять местами может только с уже существуюшим фото
        if 'order' in data and not self.instance.room_category.photos.filter(order=data['order']).exists():
            raise serializers.ValidationError({
                'order': 'Нет фото с таким порядковым номером'
            })

        return super().validate(data)

    def update(self, instance, validated_data):
        if 'order' in validated_data:
            # переопределяем обновление, чтоб поменять порядковые номера местами
            # берем старое и новое значение изменяемого объекта
            temp_order = instance.order
            new_order = self.validated_data['order']
            room_cat = instance.room_category
            # берем объект, на место которого встанет изменяемый
            photo_to_change = room_cat.photos.get(order=new_order)
            photo_to_change.order = temp_order
            # сохраняем объект, на место которого встанет изменяемый
            photo_to_change.save()
        return super().update(instance, validated_data)


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

    @property
    def data(self):
        """
        Переопределенное св-во дата для сериализации tags
        :return:
        """
        return TagsSerializer(self.validated_data['tags']).data


