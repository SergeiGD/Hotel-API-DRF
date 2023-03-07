from rest_framework import viewsets, generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import Group

from .models import Worker, WorkerTimetable
from .serializers import WorkersSerializer, WorkerTimetableSerializer, WorkerGroupsSerializer
from ..users.serializers import GroupsSerializer
from ..core.permissions import FullModelPermissionsPermissions
from .permissions import IsWorkerTimetable


class WorkersViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для работы с сотрудниками
    """
    queryset = Worker.objects.all()
    serializer_class = WorkersSerializer
    permission_classes = (IsAdminUser, FullModelPermissionsPermissions)

    def get_queryset(self):
        return Worker.objects.all()

    def perform_destroy(self, instance):
        # переопределяем destroy, чтоб он просто почемал как удаленный, а не удалял реально
        instance = self.get_object()
        instance.mark_as_deleted()


class WorkerTimetablesListAPIView(generics.ListCreateAPIView):
    """
    Вьюсет для работы со списком расписаний сотрудника
    """
    serializer_class = WorkerTimetableSerializer
    permission_classes = (IsAdminUser, IsWorkerTimetable)

    def get_worker(self):
        return get_object_or_404(Worker, pk=self.kwargs['pk'])

    def get_queryset(self):
        return self.get_worker().timetables.all()

    def perform_create(self, serializer):
        serializer.save(worker=self.get_worker())


class WorkerTimetableManageAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Вьюсет для работы со расписанием сотрудника
    """
    serializer_class = WorkerTimetableSerializer
    permission_classes = (IsAdminUser, FullModelPermissionsPermissions, )

    def get_worker(self):
        return get_object_or_404(Worker, pk=self.kwargs['pk'])

    def get_queryset(self):
        return self.get_worker().timetables.all()

    def get_object(self):
        timetable = get_object_or_404(
            WorkerTimetable,
            worker=self.get_worker(),
            pk=self.kwargs['timetable_id']
        )
        self.check_object_permissions(self.request, timetable)
        return timetable


class WorkerGroupsListAPIView(APIView):
    """
    Вью для получения списка групп сотрудника
    """
    permission_classes = (IsAdminUser, FullModelPermissionsPermissions,)

    def get_queryset(self):
        worker = get_object_or_404(Worker, pk=self.kwargs['pk'])
        return worker.groups.all()

    def get(self, request, pk):
        serializer = GroupsSerializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    def put(self, request, pk):
        worker = get_object_or_404(Worker, pk=pk)
        serializer = WorkerGroupsSerializer(data=request.data, instance=worker)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class WorkerGroupDeleteAPIView(APIView):
    """
    Вью для удаление сотрудника из группы
    """
    permission_classes = (IsAdminUser, FullModelPermissionsPermissions,)

    def get_queryset(self):
        worker = get_object_or_404(Worker, pk=self.kwargs['pk'])
        return worker.groups.all()

    def delete(self, request, group_id, pk):
        worker = get_object_or_404(Worker, pk=pk)
        group = get_object_or_404(Group, pk=group_id)
        worker.groups.remove(group)
        return Response(status=status.HTTP_204_NO_CONTENT)
