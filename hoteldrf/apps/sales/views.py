from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Sale
from .serializers import SalesSerializer, AppliesToSerializer
from ..rooms.serializers import RoomsCategoriesSerializer
from ..rooms.models import RoomCategory


class SalesViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для работы со скидками
    """
    queryset = Sale.objects.all()
    serializer_class = SalesSerializer

    def get_queryset(self):
        return Sale.objects.filter(date_deleted=None)

    def perform_destroy(self, instance):
        # переопределяем destroy, чтоб он просто помечал как удаленный, а не удалял реально
        instance.mark_as_deleted()

    # def get_serializer_class(self):
    #     """
    #     Переопределенный метод получения класса сериалайзера в зависимости от action
    #     """
    #     if self.action == 'applies_to_add':
    #         return AppliesToSerializer
    #     if self.action == 'applies_to':
    #         return RoomsCategoriesSerializer
    #     return SalesSerializer
    #
    # @action(methods=['GET'], detail=True, url_path='applies_to')
    # def applies_to(self, request, **kwargs):
    #     """
    #     Дополнительный action для получения элементов, на которые распросраняется скидка
    #     """
    #     if request.method == 'GET':
    #         sale = self.get_object()
    #         serializer = self.get_serializer(sale.applies_to.filter(date_deleted=None), many=True)
    #         return Response(serializer.data)
    #
    # @applies_to.mapping.put
    # def applies_to_add(self, request, **kwargs):
    #     """
    #     Дополнительный action для добавления элементов, на которые распросраняется скидка
    #     """
    #     if request.method == 'PUT':
    #         serializer = self.get_serializer(data=request.data, instance=self.get_object())
    #         serializer.is_valid(raise_exception=True)
    #         serializer.save()
    #         data = RoomsCategoriesSerializer(serializer.validated_data['applies_to'], many=True)
    #         return Response(serializer.data)


class SaleAppliesToListAPIView(APIView):
    """
    Вью для получения списка и добавления элементов, на которые распостраняется скидка
    """
    def get(self, request, pk):
        sale = get_object_or_404(Sale, pk=pk)
        applies_to = sale.applies_to.filter(date_deleted=None)
        serializer = RoomsCategoriesSerializer(applies_to, many=True)
        return Response(serializer.data)

    def put(self, request, pk):
        sale = get_object_or_404(Sale, pk=pk)
        serializer = AppliesToSerializer(data=request.data, instance=sale)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # т.к. applies_to вернет объекты RoomCategory, преобразуем их в json
        serialized_data = RoomsCategoriesSerializer(serializer.validated_data['applies_to'])
        return Response(serialized_data.data)


class SaleAppliesToManageAPIView(APIView):
    """
    Вью для отвязки элмента из списка элементов, на которые распостраняется скидка
    """

    def delete(self, request, cat_id, pk):
        sale = get_object_or_404(Sale, pk=pk)
        room_cat = get_object_or_404(RoomCategory, pk=cat_id)
        sale.applies_to.remove(room_cat)
        return Response(status=status.HTTP_204_NO_CONTENT)

