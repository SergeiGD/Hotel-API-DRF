from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Order, Purchase

from .serializers import CreateOrderSerializer, OrdersSerializer, \
                        PurchasesSerializer, EditOrderSerializer

from .mixins import PurchaseManageMixin, PurchaseCreateMixin


class OrdersListAPIView(APIView):
    """
    Вью для получения списка и создания заказов
    """

    def get(self, request):
        serializer = OrdersSerializer(Order.objects.all(), many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OrderManageAPIView(APIView):
    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        serializer = OrdersSerializer(order)
        return Response(serializer.data)

    def patch(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        serializer = EditOrderSerializer(instance=order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        # не удаляем, а отмечаем как отмененный
        order.mark_as_canceled()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PurchasesListAPIView(PurchaseCreateMixin, APIView):
    """
    Вью для получения списка и создания покупок заказа
    """
    def get_object(self):
        return get_object_or_404(Order, pk=self.kwargs['pk'])

    def get(self, request, pk):
        serializer = PurchasesSerializer(self.get_object().purchases.all(), many=True)
        return Response(serializer.data)


class PurchaseManageAPIView(PurchaseManageMixin, APIView):
    def get_object(self):
        return get_object_or_404(Purchase, pk=self.kwargs['purchase_id'], order_id=self.kwargs['pk'])



