from django.db.models import Sum, Q
from django.utils import timezone

from ..orders.models import Order
from ..users.models import CustomUser


class Client(CustomUser):
    @property
    def orders_count(self):
        return Order.objects.filter(client=self, date_canceled=None).count()

    @property
    def money_spent(self):
        spent = Order.objects.filter(client=self, date_canceled=None).aggregate(Sum('paid'))['paid__sum']
        if spent:
            return spent
        return 0

    class Meta:
        proxy = True

    def mark_as_deleted(self):
        self.date_deleted = timezone.now()
        self.is_active = False
        self.save()

    # def get_cart(self):
    #     """
    #     Получение коризны клиента
    #     :return:
    #     """
    #     cart = Order.objects.filter(
    #         client=self,
    #         paid=0, refunded=0,
    #         date_canceled=None,
    #         date_finished=None
    #     ).first()
    #     if cart is not None:
    #         return cart
    #
    #     # если корзины нету, то создаем
    #     return Order.objects.create_cart()

    def get_orders(self):
        """
        Получение заказов клиента
        :return:
        """
        # если paid = 0 и refunded = 0, то это корзина
        return self.orders.filter(
            Q(paid__gt=0) | Q(refunded__gt=0)
        )


