import graphene
from graphene_django.types import DjangoObjectType
from .models import RoomCategory, Room


class RoomCategoryType(DjangoObjectType):
    """
    Тип для категорий номеров
    """
    class Meta:
        model = RoomCategory


class RoomType(DjangoObjectType):
    """
    Тип для номеров
    """
    class Meta:
        model = Room



