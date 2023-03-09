from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from ..core.permissions import FullModelPermissionsPermissions

from .models import Tag
from .serializers import TagsSerializer


class TagsViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagsSerializer
    permission_classes = (IsAdminUser, FullModelPermissionsPermissions)


