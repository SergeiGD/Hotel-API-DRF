from rest_framework import serializers
from django.utils import timezone
import datetime

from django.conf import settings


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
        start = data['start'].date()
        end = data['end'].date()

        if start >= end:
            raise serializers.ValidationError({
                'start': 'Дата конца должно больше даты начала минимум на один день'
            })

        # устанавливаем часы заезда и выезда
        start = datetime.datetime.combine(start, settings.CHECK_IN_TIME)
        end = datetime.datetime.combine(end, settings.CHECK_OUT_TIME)

        # устанавливаем часовой пояс
        start = timezone.make_aware(start)
        end = timezone.make_aware(end)

        return {
            'start': start,
            'end': end
        }
