from rest_framework import viewsets

from .models import Tag
from .serializers import TagsSerializer


class TagsViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagsSerializer
