from datetime import datetime, timedelta
from django.utils.timezone import make_aware

from ..orders.models import Order, Purchase
from .models import IdempotencyKey


def clean_carts_job():
    Order.objects.filter(
        paid=0,
        refunded=0,
        client__isnull=True,
        cart_uuid__isnull=False,
        date_create__lt=make_aware(datetime.now() - timedelta(hours=12))
    ).delete()


def finish_orders_job():
    finished_orders = Order.objects.filter(
        date_finished=None,
        date_canceled=None,
        client__isnull=False,
        cart_uuid__isnull=True
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
