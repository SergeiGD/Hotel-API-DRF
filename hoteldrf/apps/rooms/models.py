import datetime

from django.db import models
from django.db.models import Count, Q
from django.utils import timezone

from ..core.utils import build_photo_path
from ..tags.models import Tag
from ..orders.models import Purchase
from django.conf import settings


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
    tags = models.ManyToManyField(
        Tag,
        related_name='rooms',
        related_query_name='room',
        verbose_name='теги',
        blank=True
    )

    def mark_as_deleted(self):
        """
        Отметить категорию комнат как удаленную
        """
        self.date_deleted = timezone.now()
        # все комнаты категории тоже отмечаем как удаленные
        self.get_rooms().update(date_deleted=timezone.now())
        self.save()

    def get_rooms(self):
        """
        Получение не удаленных комнат категории
        """
        return self.rooms.filter(room_category_id=self.id, date_deleted=None)

    def get_familiar(self):
        """
        Получение похожих категорий комнат
        """
        # получение категорий комнат с такими же тегами
        have_same_tags = RoomCategory.objects.filter(
            date_deleted=None, is_hidden=False, tags__in=self.tags.all()
        ).exclude(pk=self.pk).distinct()
        # подсчет и сортировка по количеству совпадений
        familiar = have_same_tags.annotate(
            count_familiar=Count('tags', filter=Q(tags__in=self.tags.all()))
        ).order_by('-count_familiar')
        # если меньше трех, то возвращаем все что есть
        if len(familiar) < 3:
            return familiar.all()
        # иначе возвращаем три наиболее похожие
        return familiar[0:3]

    def is_day_busy(self, day, purchase_id=None):
        """
        Проверка заняты ли все комнаты этой категории в этот день
        """
        rooms = self.get_rooms()
        # день окончания не включаем, т.к. выселение раньше заселения и номер уже освободится
        busy_rooms_count = Purchase.objects.filter(
            Q(start__lte=day) & Q(end__gt=day),
            room__in=rooms,
            is_canceled=False,
        ).exclude(pk=purchase_id).count()
        # если кол-во занятых комнат равняется количеству комнат категории, то все занято
        if busy_rooms_count >= rooms.count():
            return True
        return False

    def get_busy_dates(self, dates_start, dates_end):
        """
        Метод для получения занятых дат в диапозоне
        """
        current_day = dates_start
        busy_dates = set()
        while current_day <= dates_end:
            if self.is_day_busy(current_day):
                busy_dates.add(current_day)
            current_day += datetime.timedelta(days=1)
        return busy_dates

    def pick_rooms_for_purchase(self, start, end, purchase_id=None):
        """
        :param start: начало брони
        :param end: конец брони
        :param purchase_id: id покупки (если обновляем уже созданную)
        :return: список, состоящий из словарей с комнатами и подобранными свободными датами
        """
        result = []
        # текущая граница проверенных дат
        current_border = start
        rooms = self.get_rooms().values_list('id', flat=True)
        while current_border <= end:

            # день, который будет проверяться
            day_to_check = current_border
            # список свободных комнат на текущую итерацию
            free_rooms = set(rooms)
            # последняя комната и дата, которая была отмечена как свободная
            last_available_room = None
            last_available_date = None
            while free_rooms and day_to_check <= end:
                # ищем комнаты, который заняты на текущий проверяемый день
                busy_rooms = Purchase.objects.filter(
                    Q(start__lt=day_to_check) & Q(end__gt=day_to_check),
                    room__in=free_rooms,
                    is_canceled=False,
                ).exclude(pk=purchase_id).values_list('room_id', flat=True)

                # убираем из свободных комнат занятые
                free_rooms -= set(busy_rooms)

                if free_rooms:
                    # фиксируем доступную комнату
                    last_available_room = list(free_rooms)[0]
                    # фиксируем доступный день
                    last_available_date = day_to_check

                day_to_check += datetime.timedelta(days=1)

            # если на проверенные даты не было свободной комнаты, то возвращаем путой список
            if last_available_room is None or last_available_date is None:
                return []

            result.append({
                'room': last_available_room,
                'start': current_border,
                'end': last_available_date
            })

            current_border = last_available_date + datetime.timedelta(days=1)

        return result

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

