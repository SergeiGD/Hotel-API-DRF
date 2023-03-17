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

    def create_purchase(self, picked_room, start, end, order):
        purchase = apps.get_model('orders.Purchase')(
            room_id=picked_room,
            start=start,
            end=end,
            order=order
        )
        #  устанавливаем цены и сохраняем
        purchase.update_payment()
        return purchase


