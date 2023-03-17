from rest_framework import serializers
from django.utils import timezone
import datetime

from rest_framework.utils.serializer_helpers import ReturnDict

from .models import Order, Purchase
from .utils import PurchaseSerializerMixin
from ..rooms.models import RoomCategory
from ..clients.models import Client
from ..rooms.serializers import RoomsSerializer
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


class CreatePurchaseSerializer(PurchaseSerializerMixin, serializers.ModelSerializer):
    room_cat = serializers.PrimaryKeyRelatedField(
        queryset=RoomCategory.objects.filter(date_deleted=None),
        write_only=True
    )  # кидаем только нужную категорию, саму комнату подбираем автоматически
    start = serializers.DateField()
    end = serializers.DateField()
    room = RoomsSerializer(read_only=True)
    id = serializers.ReadOnlyField()

    class Meta:
        model = Purchase
        fields = ['start', 'end', 'room', 'id', 'room_cat']

    def validate(self, data):
        return {
            **self.validate_dates(data),
            'room_cat': data['room_cat']
        }

    def create(self, validated_data):
        """
        Подбор комнат и создание из них покупок для заказа
        """
        if validated_data['order'].date_canceled is not None or validated_data['order'].date_finished is not None:
            raise serializers.ValidationError({
                'order': 'Нельзя добавить покупку и завершенному заказу'
            })

        room_cat = validated_data['room_cat']
        picked_room = room_cat.pick_room_for_purchase(validated_data['start'], validated_data['end'])
        if picked_room is None:
            raise serializers.ValidationError({
                "start": "На данный промежуток времени нету свободных комнат этой категории"
            })

        return self.create_purchase(
            picked_room,
            validated_data['start'],
            validated_data['end'],
            validated_data['order']
        )


class EditPurchaseSerializer(PurchaseSerializerMixin, serializers.ModelSerializer):
    room = RoomsSerializer(read_only=True)
    start = serializers.DateField(required=False)
    end = serializers.DateField(required=False)

    class Meta:
        model = Purchase
        fields = ['start', 'end', 'room', 'id']

    def validate(self, data):
        if self.instance.is_canceled:
            raise serializers.ValidationError({
                'is_canceled': 'Нельзя изменять отмененную покупку'
            })

        data_to_validate = data
        if self.partial:
            # если не передали начало/конец, то берем текущие данные модели
            if 'start' not in data:
                data_to_validate['start'] = self.instance.start
            if 'end' not in data:
                data_to_validate['end'] = self.instance.end
        return self.validate_dates(data_to_validate)

    def update(self, instance, validated_data):
        """
        Подбор комнат и создание из них покупок для заказа
        """
        purchase = instance
        room_cat = purchase.room.room_category
        # ищем свободную комнату на выбранные даты
        picked_room = room_cat.pick_room_for_purchase(
            validated_data['start'],
            validated_data['end'],
            purchase_id=purchase.id
        )
        if picked_room is None:
            raise serializers.ValidationError({
                "start": "На данный промежуток времени нету свободных комнат этой категории"
            })

        purchase.start = validated_data['start']
        purchase.end = validated_data['end']
        purchase.room_id = picked_room
        #  устанавливаем цены и сохраняем
        purchase.update_payment()

        return purchase
