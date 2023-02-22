from django.shortcuts import render
from rest_framework import generics
from rest_framework.generics import get_object_or_404
from rest_framework import serializers

from .models import Room, RoomCategory
from .serializers import RoomsCategoriesSerializer, RoomsSerializer


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


