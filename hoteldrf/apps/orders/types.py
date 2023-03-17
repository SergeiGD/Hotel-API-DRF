import graphene
from graphene_django.types import DjangoObjectType

from .models import Order, Purchase, BaseOrder


class OrderType(DjangoObjectType):
    """
    Тип для заказов клиентов (сформированных, не корзины)
    """
    # привязываем purchases вручную, т.к. по какой-то причине сам он его не видит
    # (мб потому что purchases привязано к BaseOrder, а не Order (наследнику BaseOrder))
    purchases = graphene.List('apps.orders.types.PurchaseType')

    class Meta:
        model = Order

    def resolve_purchases(self, info):
        return self.purchases.all()


class BaseOrderType(DjangoObjectType):
    """
    Тип для базовых заказов (и корзины, и заказы)
    """

    class Meta:
        model = BaseOrder


class PurchaseType(DjangoObjectType):
    """
    Тип для покупок
    """

    class Meta:
        model = Purchase



