from django.db import models
from django.utils import timezone

from ..core.utils import build_photo_path
from ..rooms.models import RoomCategory


class Sale(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name='наименование'
    )
    description = models.TextField(
        verbose_name='описание',
        null=True,
        blank=True
    )
    discount = models.FloatField(
        verbose_name='скидка'
    )
    image = models.ImageField(
        upload_to=build_photo_path
    )
    start_date = models.DateField(
        verbose_name='дата начала'
    )
    end_date = models.DateField(
        verbose_name='дата завершения'
    )
    date_created = models.DateTimeField(
        verbose_name='дата создания',
        auto_now_add=True
    )
    date_deleted = models.DateTimeField(
        verbose_name='дата удаления',
        blank=True,
        null=True
    )
    applies_to = models.ManyToManyField(
        RoomCategory,
        related_name='sales',
        related_query_name='sale',
        verbose_name='действует на',
        blank=True
    )

    class Meta:
        ordering = ['-name']

    def mark_as_deleted(self):
        self.date_deleted = timezone.now()
        self.save()
