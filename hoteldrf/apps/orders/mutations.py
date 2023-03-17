import graphene

from .types import OrderType, PurchaseType
from .models import Order, Purchase
from ..clients.models import Client
from ..rooms.models import RoomCategory


class ClientInput(graphene.InputObjectType):
    id = graphene.ID()


class RoomCatInput(graphene.InputObjectType):
    id = graphene.ID()


class OrderInput(graphene.InputObjectType):
    id = graphene.ID()


class CreateOrderInput(graphene.InputObjectType):
    client = graphene.Field(ClientInput, required=True)


class EditPurchaseInput(graphene.InputObjectType):
    start = graphene.Date(required=False)
    end = graphene.Date(required=False)
    id = graphene.ID(required=True)


class CreatePurchaseInput(graphene.InputObjectType):
    start = graphene.Date(required=True)
    end = graphene.Date(required=True)
    room_cat = graphene.Field(RoomCatInput, required=True)
    order = graphene.Field(OrderInput, required=True)


class EditOrderInput(graphene.InputObjectType):
    id = graphene.ID()
    paid = graphene.Decimal(required=False)
    refunded = graphene.Decimal(required=False)
    comment = graphene.String(required=False)


class CreateOrderMutation(graphene.Mutation):
    """
    Мутация для создания заказа
    """
    class Arguments:
        input = CreateOrderInput(required=True)

    ok = graphene.Boolean()
    order = graphene.Field(OrderType)
    error = graphene.String(required=False)

    @staticmethod
    def mutate(root, info, input=None):
        if input.client is None:
            return CreateOrderMutation(ok=False, order=None, error='необходим client')

        client = Client.objects.filter(id=input.client.id).first()

        if client is None:
            return CreateOrderMutation(ok=False, order=None, error='клиент не найден')

        order_instance = Order(
            client=client,
        )
        order_instance.save()
        return CreateOrderMutation(ok=True, order=order_instance)


class EditOrderMutation(graphene.Mutation):
    """
    Мутация для изменения заказа
    """
    class Arguments:
        input = EditOrderInput(required=True)

    ok = graphene.Boolean()
    order = graphene.Field(OrderType)
    error = graphene.String(required=False)

    @staticmethod
    def mutate(root, info, input=None):
        # TODO: проверка прав

        order_instance = Order.objects.get(pk=input.id)

        if 'paid' in input:
            if input['paid'] < 0:
                return EditOrderMutation(ok=False, order=None, error='   paid должно быть >= 0')

            order_instance.paid = input.paid

        if 'refunded' in input:
            if input['refunded'] < 0:
                return EditOrderMutation(ok=False, order=None, error='refunded должно быть >= 0')

            if input['refunded'] > order_instance.left_to_refund:
                return EditOrderMutation(ok=False, order=None, error='refunded должно быть <= left_to_refund')

            order_instance.refunded = input.refunded

        if 'comment' in input:
            order_instance.comment = input.comment

        order_instance.save()
        return EditOrderMutation(ok=True, order=order_instance)


class CreatePurchaseMutation(graphene.Mutation):
    """
    Мутация для создания покупки
    """
    class Arguments:
        input = CreatePurchaseInput(required=True)

    ok = graphene.Boolean()
    purchase = graphene.Field(PurchaseType)
    error = graphene.String()

    @staticmethod
    def mutate(root, info, input=None):
        if input.order is None:
            return CreatePurchaseMutation(ok=False, purchase=None, error='необходим order')

        order = Order.objects.filter(id=input.order.id).first()

        if order is None:
            return CreatePurchaseMutation(ok=False, purchase=None, error='заказ не найден')

        if order.date_canceled is not None or order.date_finished is not None:
            return CreatePurchaseMutation(ok=False, purchase=None, error='заказ уже завершен')

        if input.start >= input.end:
            return CreatePurchaseMutation(ok=False, purchase=None, error='начало должно быть меньше конца')

        if input.room_cat is None:
            return CreatePurchaseMutation(ok=False, purchase=None, error='необходима room category')

        room_cat = RoomCategory.objects.filter(pk=input.room_cat.id).first()

        if room_cat is None:
            return CreatePurchaseMutation(ok=False, purchase=None, error='категория не найден')

        picked_room = room_cat.pick_room_for_purchase(input.start, input.end)

        if picked_room is None:
            return CreatePurchaseMutation(ok=False, purchase=None, error='нет свободных комнат на этим даты')

        #  подбор комнаты
        purchase_instance = Purchase(
            room_id=picked_room,
            start=input.start,
            end=input.end,
            order=order
        )

        purchase_instance.update_payment()
        return CreatePurchaseMutation(ok=True, purchase=purchase_instance)


class EditPurchaseMutation(graphene.Mutation):
    """
    Мутация для изменеия покупки
    """
    class Arguments:
        input = EditPurchaseInput(required=True)

    ok = graphene.Boolean()
    purchase = graphene.Field(PurchaseType)
    error = graphene.String()

    @staticmethod
    def mutate(root, info, input=None):
        purchase_instance = Purchase.objects.get(pk=input.id)

        if 'start' in input:
            start = input.start
        else:
            start = purchase_instance.start

        if 'end' in input:
            end = input.end
        else:
            end = purchase_instance.end

        if start >= end:
            return EditPurchaseMutation(ok=False, purchase=None, error='начало должно быть меньше конца')

        # подбираем комнаты
        picked_room = purchase_instance.room.room_category.pick_room_for_purchase(
            start,
            end,
            purchase_id=purchase_instance.id
        )

        if picked_room is None:
            return EditPurchaseMutation(
                ok=False,
                purchase=None,
                error='нет свободных комнат на этим даты'
            )

        purchase_instance.room_id = picked_room
        purchase_instance.start = start
        purchase_instance.end = end
        purchase_instance.update_payment()
        return EditPurchaseMutation(ok=True, purchase=purchase_instance)
