from django.db.models import Max
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.generics import get_object_or_404
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Room, RoomCategory, Photo
from ..tags.models import Tag
from ..tags.serializers import TagsSerializer
from .serializers import RoomsCategoriesSerializer, RoomsSerializer, PhotosSerializer, CreatePhotoSerializer


class RoomsCategoriesListAPIView(generics.ListAPIView):
    """
    Вью для получения списка категорий номеров
    """
    queryset = RoomCategory.objects.all()
    serializer_class = RoomsCategoriesSerializer

    def get_queryset(self):
        # Отображаем те, которые не удалены
        return RoomCategory.objects.filter(date_deleted=None)


class RoomsListAPIView(generics.ListAPIView):
    """
    Вью для получения списка номеров категории
    """
    queryset = Room.objects.all()
    serializer_class = RoomsSerializer

    def get_queryset(self):
        # Отображаем те, которые не удалены, категорию берем из url
        return Room.objects.filter(date_deleted=None, room_category_id=self.kwargs.get('cat_id'))


class PhotosListAPIView(generics.ListAPIView):
    """
    Вью для получения списка доп. фотографий категории номеров
    """
    queryset = Photo.objects.all()
    serializer_class = PhotosSerializer

    def get_queryset(self):
        # Отображаем те, которые не удалены, категорию берем из url
        return Photo.objects.filter(room_category_id=self.kwargs.get('cat_id'))


class CategoryTagsAPIView(APIView):
    """
    Вью для получения, добавления, удаления тегов категории номеров
    """
    def get(self, request, cat_id):
        tags = Tag.objects.filter(room__id=cat_id).values()
        return Response(list(tags))

    def delete(self, request, cat_id):
        room_cat = get_object_or_404(RoomCategory, pk=cat_id)
        tag = get_object_or_404(Tag, pk=request.data['tag_id'])
        room_cat.tags.remove(tag)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def post(self, request, cat_id):
        room_cat = get_object_or_404(RoomCategory, pk=cat_id)
        tag = get_object_or_404(Tag, pk=request.data['tag_id'])
        room_cat.tags.add(tag)
        return Response({
            'room_category_id': room_cat.pk,
            'tag_id': tag.pk,
        })


class RoomCategoryCreateAPIView(generics.CreateAPIView):
    """
    Вью для создания категорий номеров
    """
    queryset = RoomCategory.objects.all()
    serializer_class = RoomsCategoriesSerializer


class RoomCreateAPIView(generics.CreateAPIView):
    """
    Вью для создания номеров
    """
    queryset = Room.objects.all()
    serializer_class = RoomsSerializer

    def perform_create(self, serializer):
        room_cat = get_object_or_404(RoomCategory, pk=self.kwargs.get('cat_id'))
        serializer.save(room_category=room_cat)


class PhotoCreateAPIView(generics.CreateAPIView):
    """
    Вью для создания доп. фотографий
    """
    queryset = Photo.objects.all()
    serializer_class = CreatePhotoSerializer

    def perform_create(self, serializer):
        # при создании автоматически ставим порядковый номер на последний
        room_cat = get_object_or_404(RoomCategory, pk=self.kwargs.get('cat_id'))
        if room_cat.photos.exists():
            order = room_cat.photos.aggregate(Max('order'))['order__max'] + 1
        else:
            order = 1
        serializer.save(room_category=room_cat, order=order)


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

