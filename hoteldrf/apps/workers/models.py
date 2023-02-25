from django.utils import timezone
from django.db import models

from ..users.models import CustomUser


class Worker(CustomUser):
    salary = models.DecimalField(
        verbose_name='зарплата',
        max_digits=10,
        decimal_places=2
    )

    def mark_as_deleted(self):
        self.date_deleted = timezone.now()
        self.save()

