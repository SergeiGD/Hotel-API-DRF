from django.db.models import Sum
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


