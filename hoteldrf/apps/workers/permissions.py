from rest_framework import permissions
from django.contrib.auth.models import Permission

from ..users.models import CustomUser


class IsWorkerTimetable(permissions.BasePermission):
    """
    Разрешения на работы со списком расписаний
    """
    def has_permission(self, request, view):
        if request.method == 'POST':
            # если POST, то проверяем может ли добавлять
            return request.user.has_perm(Permission.objects.get(codename="add_workertimetable"))
        if request.method == 'GET':
            # если GET, то проверяем может ли читать или свое собственное ли расписание
            if request.user.has_perm(Permission.objects.get(codename="view_workertimetable")):
                return True
            worker_id = view.kwargs['pk']
            worker = CustomUser.objects.get(pk=worker_id)
            return worker == request.user

