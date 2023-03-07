from django.utils import timezone
from django.db import models

from ..users.models import CustomUser, CustomUserManager


class WorkersManager(CustomUserManager):
    def get_queryset(self):
        return super(WorkersManager, self).get_queryset().filter(is_staff=True)


class Worker(CustomUser):
    salary = models.DecimalField(
        verbose_name='зарплата',
        max_digits=10,
        decimal_places=2
    )

    objects = WorkersManager()

    def mark_as_deleted(self):
        self.is_staff = False
        self.is_active = False
        self.save()


class WorkerTimetable(models.Model):
    worker = models.ForeignKey(
        Worker,
        on_delete=models.CASCADE,
        verbose_name='сотрудник',
        related_name='timetables',
        related_query_name='timetable'
    )
    start = models.DateTimeField(
        verbose_name='начало'
    )
    end = models.DateTimeField(
        verbose_name='конец'
    )

    class Meta:
        ordering = ['-start']

