from django.db.models import Sum, Q

from ..orders.models import Order
from ..users.models import CustomUser, CustomUserManager


class ClientsManager(CustomUserManager):
    def get_queryset(self):
        return super(ClientsManager, self).get_queryset().filter(is_staff=False)


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

    objects = ClientsManager()

    def mark_as_deleted(self):
        self.is_active = False
        self.save()

    def get_orders(self):
        """
        Получение заказов клиента
        :return:
        """
        # если paid = 0 и refunded = 0, то это корзина
        return self.orders.all()


