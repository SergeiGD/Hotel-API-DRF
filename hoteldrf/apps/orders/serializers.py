from rest_framework import serializers
from django.utils import timezone
import datetime

from .models import Order, Purchase
from .utils import PurchaseSerializerMixin
from django.conf import settings


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
        fields = '__all__'


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


class CreatePurchaseSerializer(PurchaseSerializerMixin, serializers.ModelSerializer):
    price = serializers.DecimalField(read_only=True, max_digits=12, decimal_places=2)

    class Meta:
        model = Purchase
        fields = ['room', 'start', 'end', 'price']

    def validate(self, data):
        return {
            **self.validate_dates(data),
            'room': data['room']
        }

    def create(self, validated_data):
        """
        Кастомное сохранение для установки автовычисляемых полей
        """
        purchase = Purchase(**validated_data)
        payment_info = purchase.get_payment_info()
        # получаем расчитанные цены
        purchase.price = payment_info['price']
        purchase.prepayment = payment_info['prepayment']
        purchase.refund = payment_info['refund']
        # сохраняем объект, будет вызван сигнал presave (см в модели)
        purchase.save()
        return purchase


class PurchasesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Purchase
        fields = '__all__'


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
                # т.к. приходит время без часового пояса, сравнивать мы должно тоже без него
                data_to_validate['start'] = timezone.make_naive(self.instance.start)
            if 'end' not in data:
                data_to_validate['end'] = timezone.make_naive(self.instance.end)
        return self.validate_dates(data_to_validate)

    def update(self, instance, validated_data):
        """
        Кастомное сохранение для установки автовычисляемых полей
        """
        # устанавливаем прочие атрибуты (даты)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        payment_info = instance.get_payment_info()
        # получаем расчитанные цены
        instance.price = payment_info['price']
        instance.prepayment = payment_info['prepayment']
        instance.refund = payment_info['refund']
        # сохраняем объект, будет вызван сигнал presave (см в модели)
        instance.save()
        return instance
