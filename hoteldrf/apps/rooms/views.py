import datetime

from django.db.models import Max, F
from rest_framework import generics, status, viewsets
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAdminUser, DjangoModelPermissions, IsAuthenticated, \
                                        DjangoModelPermissionsOrAnonReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import RoomCategory, Room, Photo
from ..tags.models import Tag
from ..tags.serializers import TagsSerializer
from ..core.permissions import FullModelPermissionsPermissions
from .serializers import RoomsCategoriesSerializer, RoomsSerializer, PhotosSerializer, \
                        CreatePhotoSerializer, CatTagsSerializer


# TODO: django_filter
class RoomsCategoriesViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для работы с категорями комнат
    """
    queryset = RoomCategory.objects.all()
    serializer_class = RoomsCategoriesSerializer
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)

    def get_queryset(self):
        if not self.request.user.is_staff:
            return RoomCategory.objects.filter(date_deleted=None, is_hidden=False)
        return RoomCategory.objects.filter(date_deleted=None)

    @action(methods=['GET'], detail=True, url_path='familiar')
    def familiar(self, request, **kwargs):
        """
        Дополнительный action для получения похожих комнат
        """
        familiar = self.get_object().get_familiar()
        serializer = self.get_serializer(familiar, many=True)
        return Response(serializer.data)

    @action(methods=['GET'], detail=True, url_path='busy_dates')
    def busy_dates(self, request, **kwargs):
        """
        Дополнительный action для получения занятых дат
        """
        # формуруем даты начала
        try:
            dates_start = datetime.datetime.strptime(
                request.query_params.get("dates_start"),
                '%Y-%m-%d'
            ).date()
            dates_end = datetime.datetime.strptime(
                request.query_params.get("dates_end"),
                '%Y-%m-%d'
            ).date()
        except Exception:
            return Response({
                'error': 'Параметр даты начала или даты конца имеет неверный формат'
            })
        # получаем список занятых дат
        busy_dates = self.get_object().get_busy_dates(dates_start, dates_end)
        return Response(busy_dates)

    @action(methods=['GET'], detail=True, url_path='find_rooms')
    def find_rooms(self, request, **kwargs):
        """
        Дополнительный action для подбора комнат и дат для брони
        """
        try:
            dates_start = datetime.datetime.strptime(
                request.query_params.get("dates_start"),
                '%Y-%m-%d'
            ).date()
            dates_end = datetime.datetime.strptime(
                request.query_params.get("dates_end"),
                '%Y-%m-%d'
            ).date()
        except Exception:
            return Response({
                'error': 'Параметр даты начала или даты конца имеет неверный формат'
            })
        rooms_dates = self.get_object().find_rooms(dates_start, dates_end)
        return Response(rooms_dates)

    def perform_destroy(self, instance):
        # переопределяем destroy, чтоб он просто почемал как удаленный, а не удалял реально
        instance.mark_as_deleted()


class RoomsListAPIView(generics.ListCreateAPIView):
    """
    Вью для получения списка и создания номеров категории
    """
    serializer_class = RoomsSerializer
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly, )

    def get_queryset(self):
        room_cat = get_object_or_404(RoomCategory, pk=self.kwargs.get('pk'))
        return room_cat.rooms.filter(date_deleted=None)

    def perform_create(self, serializer):
        # берем категорию из URL
        room_cat = get_object_or_404(RoomCategory, pk=self.kwargs.get('pk'))
        serializer.save(room_category=room_cat)


class RoomManageAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Вью для просмотра, изменения, удаления номера
    """
    serializer_class = RoomsSerializer
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)

    def get_object(self):
        room = get_object_or_404(Room, room_category__id=self.kwargs.get('pk'), pk=self.kwargs['room_id'])
        self.check_object_permissions(self.request, room)
        return room

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
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly, )

    def get_queryset(self):
        room_cat = get_object_or_404(RoomCategory, pk=self.kwargs['pk'])
        return room_cat.tags.all()

    def get(self, request, pk):
        serializer = TagsSerializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    def put(self, request, pk):
        room_cat = get_object_or_404(RoomCategory, pk=pk)
        serializer = CatTagsSerializer(data=request.data, instance=room_cat)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class CategoryTagDeleteAPIView(APIView):
    """
    Вью для удаления тега из категории
    """
    permission_classes = (IsAdminUser, FullModelPermissionsPermissions,)

    def get_queryset(self):
        room_cat = get_object_or_404(RoomCategory, pk=self.kwargs['pk'])
        return room_cat.tags.all()

    def delete(self, request, tag_id, pk):
        room_cat = get_object_or_404(RoomCategory, pk=pk)
        tag = get_object_or_404(Tag, pk=tag_id)
        room_cat.tags.remove(tag)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CategoryPhotosListAPIView(APIView):
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly, )

    def get_queryset(self):
        room_cat = get_object_or_404(RoomCategory, pk=self.kwargs['pk'])
        return room_cat.photos.all()

    def get(self, request, pk):
        serializer = PhotosSerializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    def post(self, request, pk):
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


class PhotoManageAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Вью для просмотра, изменения, удаления доп фотографий
    """
    serializer_class = PhotosSerializer
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)

    def get_object(self):
        photo = get_object_or_404(Photo, room_category__id=self.kwargs.get('pk'), pk=self.kwargs['photo_id'])
        self.check_object_permissions(self.request, photo)
        return photo

    def get_queryset(self):
        # Отображаем те, которые не удалены, категорию берем из url
        room_cat = get_object_or_404(RoomCategory, pk=self.kwargs.get('pk'))
        return room_cat.photos.all()

    def perform_destroy(self, instance):
        # переопределяем destroy, чтоб он сдиваг порядковый номер последующих фотографий
        next_photos = self.get_queryset().filter(
            order__gt=instance.order
        )
        next_photos.update(order=F('order') - 1)
        super().perform_destroy(instance)

