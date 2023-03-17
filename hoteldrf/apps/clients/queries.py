import graphene
from rest_framework.generics import get_object_or_404

from .types import ClientType
from .models import Client


class Query(graphene.ObjectType):
    """
    Квери для клиентов
    """

    clients = graphene.List(ClientType)
    client = graphene.Field(ClientType, pk=graphene.Int())

    def resolve_clients(self, info, **kwargs):
        return Client.objects.all()

    def resolve_client(self, info, **kwargs):
        pk = kwargs.get('pk')
        return get_object_or_404(Client, pk=pk)


