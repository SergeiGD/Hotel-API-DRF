import graphene
from rest_framework.generics import get_object_or_404

from .types import RoomCategoryType, RoomType
from .models import Room, RoomCategory


class Query(graphene.ObjectType):
    """
    Квери для категорий номеров и номеров
    """

    categories = graphene.List(RoomCategoryType)
    category = graphene.Field(RoomCategoryType, pk=graphene.Int())
    rooms = graphene.List(RoomType)
    room = graphene.Field(RoomType, pk=graphene.Int())

    def resolve_categories(self, info, **kwargs):
        return RoomCategory.objects.all()

    def resolve_category(self, info, **kwargs):
        pk = kwargs.get('pk')
        return get_object_or_404(RoomCategory, pk=pk)

    def resolve_rooms(self, info, **kwargs):
        return Room.objects.all()

    def resolve_room(self, info, **kwargs):
        pk = kwargs.get('pk')
        return get_object_or_404(Room, pk=pk)
