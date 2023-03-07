from datetime import datetime, timedelta
from django.utils.timezone import make_aware

from ..orders.models import Order, Purchase, Cart
from .models import IdempotencyKey


def clean_carts_job():
    Cart.objects.filter(
        date_create__lt=make_aware(datetime.now() - timedelta(hours=12))
    ).delete()


def finish_orders_job():
    finished_orders = Order.objects.filter(
        date_finished=None,
        date_canceled=None,
    ).exclude(
        purchases__in=Purchase.objects.filter(
            end__gte=make_aware(datetime.now())
        )
    )

    for order in finished_orders:
        order.mark_as_finished()


def clean_idempotency_keys():
    IdempotencyKey.objects.filter(
        date_created__lt=make_aware(datetime.now() - timedelta(hours=24))
    ).delete()
