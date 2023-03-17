import graphene
from graphene_django.types import DjangoObjectType
from .models import Client


class ClientType(DjangoObjectType):
    """
    Тип для клиентов
    """
    class Meta:
        model = Client




