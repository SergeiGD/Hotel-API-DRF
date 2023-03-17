import graphene

from ..orders.queries import Query as OrdersQuery
from ..rooms.queries import Query as RoomsQuery
from ..clients.queries import Query as ClientsQuery
from ..orders.mutations import CreateOrderMutation, EditOrderMutation, CreatePurchaseMutation, EditPurchaseMutation


class Query(OrdersQuery, RoomsQuery, ClientsQuery, graphene.ObjectType):
    pass


class Mutation(graphene.ObjectType):
    create_order = CreateOrderMutation.Field()
    update_order = EditOrderMutation.Field()
    create_purchase = CreatePurchaseMutation.Field()
    update_purchase = EditPurchaseMutation.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
