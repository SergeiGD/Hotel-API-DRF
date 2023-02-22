from django.db import models
from django.db.models import UniqueConstraint
from rest_framework.exceptions import ValidationError

from .utils import build_photo_path


class RoomCategory(models.Model):
    name = models.CharField(
        verbose_name='наименование',
        max_length=255
    )
    description = models.TextField(
        verbose_name='описание'
    )
    default_price = models.DecimalField(
        verbose_name='стандартная цена',
        max_digits=10,
        decimal_places=2
    )
    prepayment_percent = models.FloatField(
        verbose_name='предоплата'
    )
    refund_percent = models.FloatField(
        verbose_name='возврат'
    )
    main_photo = models.ImageField(
        upload_to=build_photo_path
    )
    rooms_count = models.SmallIntegerField(
        verbose_name='кол-во комнат'
    )
    floors = models.SmallIntegerField(
        verbose_name='этажей'
    )
    beds = models.SmallIntegerField(
        verbose_name='спальных мест'
    )
    square = models.FloatField(
        verbose_name='площадь'
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
    is_hidden = models.BooleanField(
        verbose_name='скрыто',
        default=False
    )

    class Meta:
        ordering = ['-date_created']


class Room(models.Model):
    is_hidden = models.BooleanField(
        verbose_name='скрыто',
        default=False
    )
    room_number = models.SmallIntegerField(
        verbose_name='номер комнаты'
    )
    room_category = models.ForeignKey(
        RoomCategory,
        on_delete=models.PROTECT,
        related_name='rooms',
        related_query_name='room'
    )
    date_deleted = models.DateTimeField(
        verbose_name='дата удаления',
        blank=True,
        null=True
    )

    class Meta:
        ordering = ['-id']
