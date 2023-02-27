from django.db.models import Max, F
from rest_framework import generics, status, viewsets
from rest_framework.decorators import api_view, action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import RoomCategory
from ..tags.models import Tag
from ..tags.serializers import TagsSerializer
from .serializers import RoomsCategoriesSerializer, RoomsSerializer, PhotosSerializer, \
                        CreatePhotoSerializer, CatTagsSerializer


class RoomsCategoriesViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для работы со скидками
    """
    queryset = RoomCategory.objects.all()
    serializer_class = RoomsCategoriesSerializer

    def get_queryset(self):
        return RoomCategory.objects.filter(date_deleted=None)

    @action(methods=['GET'], detail=True, url_path='familiar')
    def familiar(self, request, **kwargs):
        """
        Дополнительный action для получения похожих комнат
        """
        familiar = self.get_object().get_familiar()
        serializer = self.get_serializer(familiar, many=True)
        return Response(serializer.data)

    def perform_destroy(self, instance):
        # переопределяем destroy, чтоб он просто почемал как удаленный, а не удалял реально
        instance.mark_as_deleted()


class RoomsListAPIView(generics.ListCreateAPIView):
    """
    Вью для получения списка и создания номеров категории
    """
    serializer_class = RoomsSerializer

    def get_queryset(self):
        # Отображаем те, которые не удалены, категорию берем из url
        room_cat = get_object_or_404(RoomCategory, pk=self.kwargs.get('pk'))
        return room_cat.rooms.filter(date_deleted=None)
        # return Room.objects.filter(date_deleted=None, room_category_id=self.kwargs.get('cat_id'))

    def perform_create(self, serializer):
        # берем категорию из URL
        room_cat = get_object_or_404(RoomCategory, pk=self.kwargs.get('pk'))
        serializer.save(room_category=room_cat)


class RoomManageAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Вью для просмотра, изменения, удаления номера
    """
    serializer_class = RoomsSerializer

    def get_object(self):
        return self.get_queryset().get(pk=self.kwargs.get('room_id'))

    def get_queryset(self):
        # Отображаем те, которые не удалены, категорию берем из url
        room_cat = get_object_or_404(RoomCategory, pk=self.kwargs.get('pk'))
        return room_cat.rooms.filter(date_deleted=None)

    def perform_destroy(self, instance):
        # переопределяем destroy, чтоб он просто почемал как удаленный, а не удалял реально
        instance.mark_as_deleted()


class CategoryTagsListAPIView(APIView):
    """
    Вью для получения списка и добавления тегов категории номеров
    """
    def get(self, request, pk):
        room_cat = get_object_or_404(RoomCategory, pk=pk)
        serializer = TagsSerializer(room_cat.tags.all(), many=True)
        return Response(serializer.data)

    def put(self, request, pk):
        room_cat = get_object_or_404(RoomCategory, pk=pk)

        serializer = CatTagsSerializer(data=request.data, instance=room_cat)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # т.к. applies_to вернет объекты RoomCategory, преобразуем их в json
        serialized_data = TagsSerializer(serializer.validated_data['tags'])
        return Response(serialized_data.data)


class CategoryTagManageAPIView(APIView):
    """
    Вью для удаления тега из категории
    """

    def delete(self, request, cat_id, pk):
        room_cat = get_object_or_404(RoomCategory, pk=cat_id)
        tag = get_object_or_404(Tag, pk=pk)
        room_cat.tags.remove(tag)
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def photos_list_api_view(request, pk):
    """
    Вью для получения списка фотографий категрии и добавления новых
    """
    if request.method == 'POST':
        serializer = CreatePhotoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        room_cat = get_object_or_404(RoomCategory, pk=pk)
        # при создании автоматически ставим порядковый номер на последний
        if room_cat.photos.exists():
            order = room_cat.photos.aggregate(Max('order'))['order__max'] + 1
        else:
            order = 1
        serializer.save(room_category=room_cat, order=order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    if request.method == 'GET':
        # категорию берем из url
        room_cat = get_object_or_404(RoomCategory, pk=pk)
        serializer = PhotosSerializer(room_cat.photos, many=True)
        return Response(serializer.data)


class PhotoManageAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Вью для просмотра, изменения, удаления доп фотографий
    """
    serializer_class = PhotosSerializer

    def get_object(self):
        return self.get_queryset().get(pk=self.kwargs.get('photo_id'))

    def get_queryset(self):
        # Отображаем те, которые не удалены, категорию берем из url
        room_cat = get_object_or_404(RoomCategory, pk=self.kwargs.get('pk'))
        return room_cat.photos.all()

    def perform_update(self, serializer):
        # переопределяем обновление, чтоб поменять порядковые номера местами
        # берем старое и новое значение изменяемого объекта
        temp_order = self.get_object().order
        new_order = self.request.data['order']
        room_cat = get_object_or_404(RoomCategory, pk=self.kwargs.get('pk'))
        # берем объект, на место которого встанет изменяемый
        photo_to_change = room_cat.photos.get(order=new_order)
        photo_to_change.order = temp_order
        # сохраняем объект, на место которого встанет изменяемый
        photo_to_change.save()
        # сохраняем изменяемый объект
        serializer.save()

    def perform_destroy(self, instance):
        # переопределяем destroy, чтоб он сдиваг порядковый номер последующих фотографий
        next_photos = self.get_queryset().filter(
            order__gt=instance.order
        )
        next_photos.update(order=F('order') - 1)
        super().perform_destroy(instance)

