from django.db import models
from django.utils import timezone

from ..core.utils import build_photo_path


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

    def mark_as_deleted(self):
        self.date_deleted = timezone.now()
        self.get_rooms().update(date_deleted=timezone.now())
        self.save()

    def get_rooms(self):
        return Room.objects.filter(room_category_id=self.id, date_deleted=None)

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

    def mark_as_deleted(self):
        self.date_deleted = timezone.now()
        self.save()

    class Meta:
        ordering = ['-id']


class Photo(models.Model):
    room_category = models.ForeignKey(
        RoomCategory,
        on_delete=models.CASCADE,
        related_name='photos',
        related_query_name='photo'
    )
    order = models.SmallIntegerField(
        verbose_name='порядковый номер'
    )
    path = models.ImageField(
        upload_to=build_photo_path,
        verbose_name='фото'
    )

    class Meta:
        ordering = ['order']
