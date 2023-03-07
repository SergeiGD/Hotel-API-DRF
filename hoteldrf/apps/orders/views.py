from rest_framework import generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Order, Purchase
from ..core.permissions import FullModelPermissionsPermissions
from .serializers import CreateOrderSerializer, OrdersSerializer, \
                        PurchasesSerializer, EditOrderSerializer

from .mixins import PurchaseManageMixin, PurchaseCreateMixin


class OrdersListAPIView(APIView):
    """
    Вью для получения списка и создания заказов
    """
    permission_classes = (IsAdminUser, FullModelPermissionsPermissions,)

    def get_queryset(self):
        return Order.objects.all()

    def get(self, request):
        serializer = OrdersSerializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OrderManageAPIView(APIView):
    permission_classes = (IsAdminUser, FullModelPermissionsPermissions,)

    def get_queryset(self):
        return Order.objects.all()

    def get_object(self):
        order = get_object_or_404(Order, pk=self.kwargs['pk'])
        self.check_object_permissions(self.request, order)
        return order

    def get(self, request, pk):
        serializer = OrdersSerializer(self.get_object())
        return Response(serializer.data)

    def patch(self, request, pk):
        serializer = EditOrderSerializer(instance=self.get_object(), data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        order = self.get_object()
        # не удаляем, а отмечаем как отмененный
        order.mark_as_canceled()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PurchasesListAPIView(PurchaseCreateMixin, APIView):
    """
    Вью для получения списка и создания покупок заказа
    """

    permission_classes = (IsAdminUser, FullModelPermissionsPermissions,)

    def get_queryset(self):
        order = get_object_or_404(Order, pk=self.kwargs['pk'])
        return order.purchases.all()

    def get_order(self):
        return get_object_or_404(Order, pk=self.kwargs['pk'])

    def get(self, request, pk):
        serializer = PurchasesSerializer(self.get_queryset(), many=True)
        return Response(serializer.data)


class PurchaseManageAPIView(PurchaseManageMixin, APIView):
    permission_classes = (IsAdminUser, FullModelPermissionsPermissions, )

    def get_object(self):
        purchase = get_object_or_404(Purchase, pk=self.kwargs['purchase_id'], order_id=self.kwargs['pk'])
        self.check_object_permissions(self.request, purchase)
        return purchase



