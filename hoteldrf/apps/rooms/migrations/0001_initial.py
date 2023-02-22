# Generated by Django 4.1.7 on 2023-02-21 09:33

import apps.rooms.utils
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='наименование')),
                ('description', models.TextField(null=True, verbose_name='описание')),
                ('default_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='стандартная цена')),
                ('prepayment_percent', models.FloatField(verbose_name='предоплата')),
                ('refund_percent', models.FloatField(verbose_name='возврат')),
                ('main_photo', models.ImageField(null=True, upload_to=apps.rooms.utils.build_photo_path)),
                ('rooms', models.SmallIntegerField(null=True, verbose_name='кол-во комнат')),
                ('floors', models.SmallIntegerField(null=True, verbose_name='этажей')),
                ('beds', models.SmallIntegerField(null=True, verbose_name='спальных мест')),
                ('square', models.FloatField(null=True, verbose_name='площадь')),
                ('room_number', models.SmallIntegerField(null=True, unique=True, verbose_name='номер комнаты')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='дата создания')),
                ('date_deleted', models.DateTimeField(blank=True, null=True, verbose_name='дата удаления')),
                ('is_hidden', models.BooleanField(default=False, verbose_name='скрыто')),
                ('main_room', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='child_rooms', related_query_name='child_room', to='rooms.room', verbose_name='номер представитель')),
            ],
        ),
    ]
