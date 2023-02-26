from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Order, Purchase
from .serializers import CreateOrderSerializer, CreatePurchaseSerializer, OrdersSerializer, \
                        PurchasesSerializer, EditOrderSerializer, EditPurchaseSerializer


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


class PurchasesListAPIView(APIView):
    """
    Вью для получения списка и создания покупок заказа
    """
    def get(self, request, order_id):
        order = get_object_or_404(Order, pk=order_id)
        serializer = PurchasesSerializer(Purchase.objects.filter(order=order), many=True)
        return Response(serializer.data)

    def post(self, request, order_id):
        order = get_object_or_404(Order, pk=order_id)
        serializer = CreatePurchaseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(order=order)
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


class PurchaseManageAPIView(APIView):
    def get(self, request, order_id, pk):
        purchase = get_object_or_404(Purchase, pk=pk, order_id=order_id)
        serializer = PurchasesSerializer(purchase)
        return Response(serializer.data)

    def patch(self, request, order_id, pk):
        purchase = get_object_or_404(Purchase, pk=pk, order_id=order_id)
        serializer = EditPurchaseSerializer(instance=purchase, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, order_id, pk):
        purchase = get_object_or_404(Purchase, pk=pk, order_id=order_id)
        purchase.mark_as_canceled()
        return Response(status=status.HTTP_204_NO_CONTENT)


