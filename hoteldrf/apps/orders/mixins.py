from rest_framework import status
from rest_framework.response import Response

from .serializers import EditPurchaseSerializer, PurchasesSerializer, CreatePurchaseSerializer


class PurchaseManageMixin:
    def get(self, request, **kwargs):
        serializer = PurchasesSerializer(self.get_object())
        return Response(serializer.data)

    def patch(self, request, **kwargs):
        serializer = EditPurchaseSerializer(instance=self.get_object(), data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, **kwargs):
        # не удаляем, а отмечаем как отмененный
        self.get_object().mark_as_canceled()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PurchaseCreateMixin:
    def post(self, request, **kwargs):
        serializer = CreatePurchaseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(order=self.get_order())
        return Response(serializer.data, status=status.HTTP_201_CREATED)
