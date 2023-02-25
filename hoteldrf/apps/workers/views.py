from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response

from .models import Worker
from .serializers import WorkersSerializer


class WorkersListAPIView(generics.ListCreateAPIView):
    """
    Вью для просмотра и создания сотрудников
    """
    queryset = Worker.objects.all()
    serializer_class = WorkersSerializer

    def get_queryset(self):
        return Worker.objects.filter(date_deleted=None)


class WorkersManageAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Вью для просмотра, удаления и изменения сотрудника
    """
    queryset = Worker.objects.all()
    serializer_class = WorkersSerializer

    def get_queryset(self):
        return Worker.objects.filter(date_deleted=None)

    def perform_destroy(self, instance):
        # переопределяем destroy, чтоб он просто почемал как удаленный, а не удалял реально
        instance = self.get_object()
        instance.mark_as_deleted()
        return Response(status=status.HTTP_204_NO_CONTENT)