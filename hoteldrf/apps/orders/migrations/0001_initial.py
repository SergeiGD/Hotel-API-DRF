# Generated by Django 4.1.7 on 2023-02-26 05:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('rooms', '0011_roomcategory_tags'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField(blank=True, null=True, verbose_name='комментарий к заказу')),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name='Стоимость')),
                ('paid', models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name='Оплачено')),
                ('refunded', models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name='Возвращено')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='дата создания')),
                ('date_full_prepayment', models.DateTimeField(blank=True, null=True, verbose_name='дата полной предоплаты')),
                ('date_full_paid', models.DateTimeField(blank=True, null=True, verbose_name='дата полной оплаты')),
                ('date_finished', models.DateTimeField(blank=True, null=True, verbose_name='дата завершения')),
                ('date_canceled', models.DateTimeField(blank=True, null=True, verbose_name='дата отмены')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Клиент')),
            ],
        ),
        migrations.CreateModel(
            name='Purchase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=12)),
                ('prepayment', models.DecimalField(decimal_places=2, max_digits=12)),
                ('refund', models.DecimalField(decimal_places=2, max_digits=12)),
                ('is_paid', models.BooleanField(default=False, verbose_name='Оплачено')),
                ('is_prepayment_paid', models.BooleanField(default=False, verbose_name='Предоплата внесена')),
                ('is_refund_made', models.BooleanField(default=False, verbose_name='Средства возвращены')),
                ('is_canceled', models.BooleanField(default=False, verbose_name='Отменено')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='purchases', to='orders.order', verbose_name='заказ')),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='purchases', to='rooms.room', verbose_name='комната')),
            ],
        ),
    ]
