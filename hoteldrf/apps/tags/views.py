from django.shortcuts import render
from rest_framework import generics

from .models import Tag
from .serializers import TagsSerializer


class TagsListAPIView(generics.ListAPIView):
    """
    Вью для получения списка тегов
    """
    queryset = Tag.objects.all()
    serializer_class = TagsSerializer
    

class TagsCreateAPIView(generics.CreateAPIView):
    """
    Вью для создания тегов
    """
    queryset = Tag.objects.all()
    serializer_class = TagsSerializer


class TagsManageAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Вью для просмотра, изменения, удаления тегов
    """
    queryset = Tag.objects.all()
    serializer_class = TagsSerializer

