import graphene
from rest_framework.generics import get_object_or_404

from .types import PurchaseType, OrderType
from .models import Order, Purchase


class Query(graphene.ObjectType):
    """
    Квери для заказов клиентов и покупок
    """

    orders = graphene.List(OrderType)
    order = graphene.Field(OrderType, pk=graphene.Int())
    purchases = graphene.List(PurchaseType)
    purchase = graphene.Field(PurchaseType, pk=graphene.Int())

    def resolve_orders(self, info, **kwargs):
        return Order.objects.all()

    def resolve_order(self, info, **kwargs):
        pk = kwargs.get('pk')
        return get_object_or_404(Order, pk=pk)

    def resolve_purchases(self, info, **kwargs):
        return Purchase.objects.all()

    def resolve_purchase(self, info, **kwargs):
        pk = kwargs.get('pk')
        return get_object_or_404(Purchase, pk=pk)
