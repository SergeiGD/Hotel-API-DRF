import datetime
from decimal import Decimal
import uuid

from django.db.models import Sum, Max, Q
from django.db.models.signals import pre_save, pre_delete, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.db import models

from .utils import PurchaseUtil


class BaseOrder(models.Model):
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Стоимость'
    )
    date_created = models.DateTimeField(
        verbose_name='дата создания',
        auto_now_add=True
    )

    @property
    def prepayment(self):
        """
        Свойство для получения предоплаты
        """
        # если заказ еще не сохранен в БД или нету активных покупок, то предоплата 0
        if not self.pk or not self.purchases.filter(is_canceled=False).exists():
            return 0
        return self.purchases.filter(is_canceled=False).aggregate(Sum('prepayment')).get('prepayment__sum', 0)


class Cart(BaseOrder):
    cart_uuid = models.UUIDField(
        null=True,
        blank=True,
        default=uuid.uuid4,
        editable=False
    )


class Order(BaseOrder):
    client = models.ForeignKey(
        'clients.Client',
        on_delete=models.PROTECT,
        related_name='orders',
        related_query_name='order',
        verbose_name='Клиент',
        null=True,
        blank=True
    )
    comment = models.TextField(
        verbose_name='комментарий к заказу',
        blank=True, 
        null=True
    )
    paid = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        default=0, 
        verbose_name='Оплачено'
    )
    refunded = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0, 
        verbose_name='Возвращено'
    )
    date_full_prepayment = models.DateTimeField(
        verbose_name='дата полной предоплаты',
        blank=True, 
        null=True
    )
    date_full_paid = models.DateTimeField(
        verbose_name='дата полной оплаты', 
        blank=True, 
        null=True
    )
    date_finished = models.DateTimeField(
        verbose_name='дата завершения', 
        blank=True, 
        null=True
    )
    date_canceled = models.DateTimeField(
        verbose_name='дата отмены',
        blank=True, 
        null=True
    )

    @property
    def left_to_pay(self):
        """
        Свойство для получения суммы, которую осталось заплатить
        """
        left_to_pay = self.price - self.paid
        if left_to_pay > 0:
            return left_to_pay
        return 0

    @property
    def required_to_be_refunded(self):
        """
        Свойство для получения значения, которре суммарно должно быть возвращено
        """
        required_to_be_refunded = self.paid - self.price
        if required_to_be_refunded > 0:
            return required_to_be_refunded
        return 0

    @property
    def left_to_refund(self):
        """
        Свойство для получения сумму, которую ОСТАЛОСЬ вернуть
        """
        left_to_refund = self.required_to_be_refunded - self.refunded
        if left_to_refund > 0:
            return left_to_refund
        return 0

    def save(self, *args, **kwargs):
        # переопределяем сохранение, чтоб дополнительно обновить автовычисляемые поля
        if self.pk:
            self.update_payment()
        super().save(*args, **kwargs)

    def update_payment(self):
        """
        Метод для обновления статуса оплаты заказы и покупок при сохранении заказа
        """
        prepayment = self.prepayment

        # если полностью оплатили, то то устанавливаем статус оплаты всем не отмененным покупкам
        # и выставляем дату полной оплаты заказа
        if self.paid >= self.price and self.paid > 0:
            self.purchases.filter(
                is_canceled=False,
                is_paid=False
            ).update(is_paid=True)
            if self.date_full_paid is None:
                self.date_full_paid = timezone.now()
            return

        # если оплатили предоплату, то устанавливаем статус оплаты всем не отмененным покупкам
        # и выставляем дату предоплату заказа
        if self.paid >= prepayment and self.paid > 0:
            self.purchases.filter(
                is_canceled=False,
                is_prepayment_paid=False
            ).update(is_prepayment_paid=True)
            if self.date_full_prepayment is None:
                self.date_full_prepayment = timezone.now()
            return

        # если предполата не внесена (обновилось внесенная сумма paid или изменился набор покупок),
        # то устанавливаем статус оплаты всем не отмененным покупкам и убераем дату предоплату и оплаты заказа
        if self.paid < prepayment:
            self.purchases.filter(
                is_canceled=False,
                is_prepayment_paid=True
            ).update(is_prepayment_paid=False, is_paid=False)
            if self.date_full_prepayment is not None:
                self.date_full_prepayment = None
            if self.date_full_paid is not None:
                self.date_full_paid = None
            return

        # если оплата не внесена (обновилось внесенная сумма paid или изменился набор покупок),
        # то устанавливаем статус оплаты всем не отмененным покупкам и убераем дату полной оплаты заказа
        if self.paid < self.price:
            self.purchases.filter(
                is_canceled=False,
                is_paid=True
            ).update(is_paid=False)
            if self.date_full_paid is not None:
                self.date_full_paid = None
            return

    def mark_as_prepayment_paid(self):
        """
        Отметить предоплату как уплаченную
        """
        self.paid = self.prepayment
        self.save()

    def mark_as_paid(self):
        """
        Отметить предоплату как уплаченную
        """
        self.paid = self.price
        self.save()

    def mark_as_finished(self):
        # устанавливаем дату завершения
        self.date_finished = timezone.now()
        # убираем дату отмены, если она вдруг стоит
        self.date_canceled = None
        self.save()
        # все не оплаченные покупки, которые еще не отменены, ставим как отмененные
        # не update т.к. нужен вызов pre save у puchase
        for purchase in self.purchases.filter(is_canceled=False, is_paid=False):
            purchase.mark_as_canceled()

    def mark_as_canceled(self):
        # устанавливаем дату отмены
        self.date_canceled = timezone.now()
        # убираем дату завершения, если она вдруг стоит
        self.date_finished = None
        self.save()
        # все не оплаченные покупки, которые еще не отменены, ставим как отмененные
        # не update т.к. нужен вызов pre save у puchase
        for purchase in self.purchases.filter(is_canceled=False, is_paid=False):
            purchase.mark_as_canceled()


class Purchase(models.Model):
    order = models.ForeignKey(
        BaseOrder,
        on_delete=models.CASCADE, 
        related_name='purchases',
        verbose_name='заказ'
    )
    room = models.ForeignKey(
        'rooms.Room',
        on_delete=models.CASCADE,
        related_name='purchases',
        verbose_name='комната'
    )

    start = models.DateField()
    end = models.DateField()

    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    prepayment = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    refund = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    is_paid = models.BooleanField(
        default=False,
        verbose_name='Оплачено'
    )
    is_prepayment_paid = models.BooleanField(
        default=False,
        verbose_name='Предоплата внесена'
    )
    is_refund_made = models.BooleanField(
        default=False,
        verbose_name='Средства возвращены'
    )
    is_canceled = models.BooleanField(
        default=False,
        verbose_name='Отменено'
    )

    def get_payment_info(self):
        """
        Метод для получения актуальной (обновленной) цены, предоплаты, возврата
        """
        room_category = self.room.room_category

        delta_seconds = (self.end - self.start).total_seconds()
        seconds_in_day = 86400
        # окрулгям, т.к. часы заезда может не часам времени выезда
        days = round(Decimal(delta_seconds / seconds_in_day), 0)
        price = room_category.default_price * days
        # смотрим есть ли активные скидки
        sales = self.room.room_category.sales.filter(
            start_date__lte=datetime.datetime.today(),
            end_date__gt=datetime.datetime.today()
        )
        if sales:
            # если есть, то применяем максимальную из них
            biggest_sale = sales.aggregate(Max('discount')).get('discount__max', 0)
            sale__ratio = Decimal(biggest_sale) / 100
            if sale__ratio > 0:
                price = price - (price * sale__ratio)

        prepayment_ratio = Decimal(room_category.prepayment_percent) / 100
        prepayment = price * prepayment_ratio

        refund_ratio = Decimal(room_category.refund_percent) / 100
        refund = price * refund_ratio

        return {
            'price': price,
            'prepayment': prepayment,
            'refund': refund
        }

    def mark_as_canceled(self):
        if Cart.objects.filter(id=self.order.id).exists():
            # если корзина, то проста сразу удаляем
            self.delete()
            return

        if not self.order.purchases.exclude(pk=self.id).filter(
                is_canceled=False
        ).exists() and self.order.date_canceled is None:
            # если нету больше не отмененных покупок, то заказ помечаем как отмененный
            self.order.mark_as_canceled()
        if self.is_paid or self.is_prepayment_paid:
            # если была оплачена предоплата/полностью, то помечаем покупоку как отмененную
            self.is_canceled = True
            self.save()
        else:
            self.delete()


@receiver(pre_save, sender=Purchase, dispatch_uid='update_purchase')
def update_purchase(sender, instance, **kwargs):
    """
    Pre save сигнал для обновления цены заказа при изменении покупки
    """

    if instance.pk:
        # расчитываем цену, которая было до сохранения
        old_obj = Purchase.objects.get(pk=instance.pk)
        instance.order.price -= PurchaseUtil.calc_price_in_order(old_obj)

    # прибавляем текущую цену
    instance.order.price += PurchaseUtil.calc_price_in_order(instance)
    # сохраняем заказ, будет вызван метод update_payment заказа, для обновления статуса оплаты
    instance.order.save()


@receiver(post_delete, sender=Purchase, dispatch_uid='delete_purchase')
def delete_purchase(sender, instance, **kwargs):
    """
    Pre delete сигнал для обновления цены заказа при удалении покупки
    """
    # отнимаем цену покупки и сохраняем заказ, будет вызван метод update_payment заказа для обновления статуса оплаты
    instance.order.price -= PurchaseUtil.calc_price_in_order(instance)
    instance.order.save()


# class Cart(models.Model):
#     id = models.UUIDField(
#         primary_key=True,
#         default=uuid.uuid4,
#         editable=False
#     )
#     date_created = models.DateTimeField(
#         auto_now_add=True
#     )
#     purchases = GenericRelation(Purchase)
