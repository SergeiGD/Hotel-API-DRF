from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Order, Purchase
# from .serializers import CreateOrderSerializer, CreatePurchaseSerializer, OrdersSerializer, \
#                         PurchasesSerializer, EditOrderSerializer, EditPurchaseSerializer, CreatePurchaseSerializer2

from .serializers import CreateOrderSerializer, OrdersSerializer, EditPurchaseSerializer, \
                        PurchasesSerializer, EditOrderSerializer, CreatePurchaseSerializer


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


class PurchasesListAPIView(APIView):
    """
    Вью для получения списка и создания покупок заказа
    """
    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        serializer = PurchasesSerializer(order.purchases.all(), many=True)
        return Response(serializer.data)

    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        serializer = CreatePurchaseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(order=order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PurchaseManageAPIView(APIView):
    def get(self, request, purchase_id, pk):
        purchase = get_object_or_404(Purchase, pk=purchase_id, order_id=pk)
        serializer = PurchasesSerializer(purchase)
        return Response(serializer.data)

    def patch(self, request, purchase_id, pk):
        purchase = get_object_or_404(Purchase, pk=purchase_id, order_id=pk)
        serializer = EditPurchaseSerializer(instance=purchase, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, purchase_id, pk):
        purchase = get_object_or_404(Purchase, pk=purchase_id, order_id=pk)
        # не удаляем, а отмечаем как отмененный
        purchase.mark_as_canceled()
        return Response(status=status.HTTP_204_NO_CONTENT)


