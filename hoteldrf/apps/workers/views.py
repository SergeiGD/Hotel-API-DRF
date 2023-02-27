from rest_framework import viewsets

from .models import Worker
from .serializers import WorkersSerializer


class WorkersViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для работы с сотрудниками
    """
    queryset = Worker.objects.all()
    serializer_class = WorkersSerializer

    def get_queryset(self):
        return Worker.objects.filter(date_deleted=None)

    def perform_destroy(self, instance):
        # переопределяем destroy, чтоб он просто почемал как удаленный, а не удалял реально
        instance = self.get_object()
        instance.mark_as_deleted()
