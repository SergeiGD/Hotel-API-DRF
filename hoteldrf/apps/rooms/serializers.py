from rest_framework import serializers

from .models import Room, RoomCategory


class RoomsCategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomCategory
        fields = ['id', 'name', 'description', 'default_price',
                  'prepayment_percent', 'refund_percent',
                  'main_photo', 'floors', 'rooms_count', 'beds',
                  'square', 'is_hidden',
                  ]

    def validate(self, data):
        if data['default_price'] <= 0:
            raise serializers.ValidationError("Цена должна быть больше 0")
        if data['prepayment_percent'] <= 0 or data['prepayment_percent'] > 100:
            raise serializers.ValidationError("Предоплата должна быть больше 0 и не больше 100")
        if data['refund_percent'] <= 0 or data['refund_percent'] > 100:
            raise serializers.ValidationError("Возврат должен быть больше 0 и не больше 100")
        if data['rooms_count'] <= 0:
            raise serializers.ValidationError("Кол-во комнат должно быть больше 0")
        if data['floors'] <= 0:
            raise serializers.ValidationError("Кол-во этажей должно быть больше 0")
        if data['beds'] <= 0:
            raise serializers.ValidationError("Кол-во спальных мест должно быть больше 0")
        if data['square'] <= 0:
            raise serializers.ValidationError("Площадь должна быть больше 0")

        return data


class RoomsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['room_number', 'is_hidden']

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
            raise serializers.ValidationError("Уже существует комната с этим номером")
        return data

