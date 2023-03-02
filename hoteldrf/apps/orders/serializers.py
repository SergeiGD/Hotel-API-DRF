from rest_framework import serializers
from django.utils import timezone
import datetime

from rest_framework.utils.serializer_helpers import ReturnDict

from .models import Order, Purchase
from .utils import PurchaseSerializerMixin
from ..rooms.models import RoomCategory
from django.conf import settings
from django.apps import apps


class CreateOrderSerializer(serializers.ModelSerializer):
    date_created = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Order
        fields = ['client', 'comment', 'date_created']


class OrdersSerializer(serializers.ModelSerializer):
    left_to_pay = serializers.ReadOnlyField()
    left_to_refund = serializers.ReadOnlyField()
    prepayment = serializers.ReadOnlyField()
    required_to_be_refunded = serializers.ReadOnlyField()

    class Meta:
        model = Order
        # не fields = '__all__' чтоб было удобнее переопределить в ClientOrdersSerializer
        exclude = []


class EditOrderSerializer(serializers.ModelSerializer):
    left_to_pay = serializers.ReadOnlyField()
    left_to_refund = serializers.ReadOnlyField()

    class Meta:
        model = Order
        fields = ['comment', 'paid', 'refunded', 'left_to_pay', 'left_to_refund']

    def validate(self, data):
        if self.partial and 'refunded' in data:
            if 'refunded' in data and data['refunded'] > self.instance.required_to_be_refunded:
                raise serializers.ValidationError({
                    'refunded': 'Сумма возврата не должна быть больше значения возврата средств'
                })
            if 'refunded' in data and data['refunded'] < 0:
                raise serializers.ValidationError({
                    'refunded': 'Сумма возврата не должна быть меньше 0'
                })
            if 'paid' in data and data['paid'] < 0:
                raise serializers.ValidationError({
                    'refunded': 'Сумма оплаты не должна быть меньше 0'
                })

        return data


class PurchasesSerializer(serializers.ModelSerializer):
    room_category = serializers.SerializerMethodField()

    def get_room_category(self, instance):
        return instance.room.room_category.id

    class Meta:
        model = Purchase
        exclude = ['order', ]


class CreatePurchaseSerializer(PurchaseSerializerMixin, serializers.Serializer):
    room_cat = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=RoomCategory.objects.filter(date_deleted=None),
    )
    start = serializers.DateField(write_only=True)
    end = serializers.DateField(write_only=True)

    def validate(self, data):
        return {
            **self.validate_dates(data),
            'room_cat': data['room_cat']
        }

    def create(self, validated_data):
        """
        Подбор комнат и создание из них покупок для заказа
        """
        room_cat = validated_data['room_cat']
        picked_rooms = room_cat.pick_rooms_for_purchase(validated_data['start'], validated_data['end'])

        return self.create_purchases(picked_rooms, validated_data['order'])

    @property
    def data(self):
        """
        Переопределенная data, т.к. сериалайзер у нас инциализируется Many=False, а после создания
        возвращается коллекция объектом
        """
        serializer = PurchasesSerializer(self.instance, many=True)
        return serializer.data


class EditPurchaseSerializer(PurchaseSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Purchase
        fields = ['start', 'end']

    def validate(self, data):
        if self.instance.is_canceled:
            raise serializers.ValidationError({
                'is_canceled': 'Нельзя изменять отмененную покупку'
            })

        data_to_validate = data
        if self.partial:
            # если не передали начало/конец, то берем текущие данные модели
            if 'start' not in data:
                # data_to_validate['start'] = timezone.make_naive(self.instance.start)
                data_to_validate['start'] = self.instance.start
            if 'end' not in data:
                # data_to_validate['end'] = timezone.make_naive(self.instance.end)
                data_to_validate['end'] = self.instance.end
        return self.validate_dates(data_to_validate)

    def update(self, instance, validated_data):
        """
        Подбор комнат и создание из них покупок для заказа
        """
        purchase = instance
        room_cat = purchase.room.room_category
        order = purchase.order
        picked_rooms = room_cat.pick_rooms_for_purchase(
            validated_data['start'],
            validated_data['end'],
            purchase.id
        )
        if picked_rooms:
            purchase.delete()

        return self.create_purchases(picked_rooms, order)

    @property
    def data(self):
        """
        Переопределенная data, т.к. сериалайзер у нас инциализируется Many=False, а после создания
        возвращается коллекция объектом
        """
        serializer = PurchasesSerializer(self.instance, many=True)
        return serializer.data
