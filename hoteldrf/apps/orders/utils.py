from rest_framework import serializers

from django.apps import apps


class PurchaseUtil:
    @staticmethod
    def calc_price_in_order(purchase):
        """
        Метод для получения цены в заказе
        (нужен, потому что эта цена может отличается от цены экземпляра purchase, если он отменен)
        """
        price = 0
        # если отменен и оплачен, то цена = цена - возврат средств
        if purchase.is_canceled and purchase.is_paid:
            price = purchase.price - purchase.refund
        # если отменен и не оплачен, то цена = предоплате
        elif purchase.is_canceled and not purchase.is_paid:
            price = purchase.prepayment
        # если не отменен, то цена = цене
        elif not purchase.is_canceled:
            price = purchase.price
        return price


class PurchaseSerializerMixin:
    def validate_dates(self, data):
        start = data['start']
        end = data['end']

        if start >= end:
            raise serializers.ValidationError({
                'start': 'Дата конца должно больше даты начала минимум на один день'
            })

        return data

    def create_purchases(self, picked_rooms, order):
        if not picked_rooms:
            raise serializers.ValidationError({
                "start": "На данный промежуток времени нету свободных комнат этой категории"
            })

        purchases = []
        for room in picked_rooms:
            # создаем покупку
            purchase = apps.get_model('orders.Purchase')(
                room_id=room['room'],
                start=room['start'],
                end=room['end'],
                order=order
            )
            # получаем расчитанные цены
            payment_info = purchase.get_payment_info()
            purchase.price = payment_info['price']
            purchase.prepayment = payment_info['prepayment']
            purchase.refund = payment_info['refund']
            # сохраняем объект, будет вызван сигнал presave (см в модели)
            purchase.save()
            # добавляем к списку созданных
            purchases.append(purchase)
        return purchases
