from django.db.models import Max
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Room, RoomCategory, Photo
from ..tags.models import Tag
from .serializers import RoomsCategoriesSerializer, RoomsSerializer, PhotosSerializer, CreatePhotoSerializer


class RoomsCategoriesListAPIView(generics.ListCreateAPIView):
    """
    Вью для получения списка и создания категорий номеров
    """
    queryset = RoomCategory.objects.all()
    serializer_class = RoomsCategoriesSerializer

    def get_queryset(self):
        # Отображаем те, которые не удалены
        return RoomCategory.objects.filter(date_deleted=None)


class RoomsListAPIView(generics.ListCreateAPIView):
    """
    Вью для получения списка и создания номеров категории
    """
    queryset = Room.objects.all()
    serializer_class = RoomsSerializer

    def get_queryset(self):
        # Отображаем те, которые не удалены, категорию берем из url
        return Room.objects.filter(date_deleted=None, room_category_id=self.kwargs.get('cat_id'))

    def perform_create(self, serializer):
        # берем категорию из URL
        room_cat = get_object_or_404(RoomCategory, pk=self.kwargs.get('cat_id'))
        serializer.save(room_category=room_cat)


@api_view(['GET', 'POST'])
def photos_list_api_view(request, cat_id):
    """
    Вью для получения списка фотографий категрии и добавления новых
    """
    if request.method == 'POST':
        serializer = CreatePhotoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        room_cat = get_object_or_404(RoomCategory, pk=cat_id)
        # при создании автоматически ставим порядковый номер на последний
        if room_cat.photos.exists():
            order = room_cat.photos.aggregate(Max('order'))['order__max'] + 1
        else:
            order = 1
        serializer.save(room_category=room_cat, order=order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    if request.method == 'GET':
        # категорию берем из url
        queryset = Photo.objects.filter(room_category_id=cat_id)
        serializer = PhotosSerializer(queryset, many=True)
        return Response(list(serializer.data))


class CategoryTagsListAPIView(APIView):
    """
    Вью для получения списка и добавления тегов категории номеров
    """
    def get(self, request, cat_id):
        tags = Tag.objects.filter(room__id=cat_id).values()
        return Response(list(tags))

    def post(self, request, cat_id):
        room_cat = get_object_or_404(RoomCategory, pk=cat_id)
        tag = get_object_or_404(Tag, pk=request.data['tag_id'])
        room_cat.tags.add(tag)
        return Response({
            'room_category_id': room_cat.pk,
            'tag_id': tag.pk,
        })


class RoomCategoryManageAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Вью для просмотра, изменения, удаления категории номеров
    """
    queryset = RoomCategory.objects.all()
    serializer_class = RoomsCategoriesSerializer

    def get_queryset(self):
        # Отображаем те, которые не удалены
        return RoomCategory.objects.filter(date_deleted=None)

    def perform_destroy(self, instance):
        # переопределяем destroy, чтоб он просто почемал как удаленный, а не удалял реально
        instance = self.get_object()
        instance.mark_as_deleted()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RoomManageAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Вью для просмотра, изменения, удаления номера
    """
    queryset = Room.objects.all()
    serializer_class = RoomsSerializer

    def get_queryset(self):
        # Отображаем те, которые не удалены, категорию берем из url
        return Room.objects.filter(date_deleted=None, room_category_id=self.kwargs.get('cat_id'))

    def perform_destroy(self, instance):
        # переопределяем destroy, чтоб он просто почемал как удаленный, а не удалял реально
        instance = self.get_object()
        instance.mark_as_deleted()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PhotoManageAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Вью для просмотра, изменения, удаления доп фотографий
    """
    queryset = Photo.objects.all()
    serializer_class = PhotosSerializer

    def get_queryset(self):
        # Категорию берем из url
        return Photo.objects.filter(room_category_id=self.kwargs.get('cat_id'))

    def perform_update(self, serializer):
        #  переопределяем обновление, чтоб поменять порядковые номера местами
        temp_order = self.get_object().order
        new_order = self.request.data['order']
        room_cat = get_object_or_404(RoomCategory, pk=self.kwargs.get('cat_id'))
        photo_to_change = room_cat.photos.get(order=new_order)
        photo_to_change.order = temp_order
        photo_to_change.save()
        serializer.save()

    def perform_destroy(self, instance):
        # переопределяем destroy, чтоб он сдиваг порядковый номер последующих фотографий
        instance = self.get_object()
        next_photos = Photo.objects.filter(
            room_category=instance.room_category,
            order__gt=instance.order
        )
        for photo in next_photos:
            photo.order -= 1
            photo.save()
        super().perform_destroy(instance)


class CategoryTagManageAPIView(APIView):
    """
    Вью для удаления тега из категории
    """

    def delete(self, request, cat_id, pk):
        room_cat = get_object_or_404(RoomCategory, pk=cat_id)
        tag = get_object_or_404(Tag, pk=pk)
        room_cat.tags.remove(tag)
        return Response(status=status.HTTP_204_NO_CONTENT)

