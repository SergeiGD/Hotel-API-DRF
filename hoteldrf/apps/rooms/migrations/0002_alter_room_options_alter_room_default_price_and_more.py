# Generated by Django 4.1.7 on 2023-02-22 11:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='room',
            options={'ordering': ['-date_created']},
        ),
        migrations.AlterField(
            model_name='room',
            name='default_price',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True, verbose_name='стандартная цена'),
        ),
        migrations.AlterField(
            model_name='room',
            name='main_room',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='child_rooms', related_query_name='child_room', to='rooms.room', verbose_name='родительский номер'),
        ),
        migrations.AlterField(
            model_name='room',
            name='name',
            field=models.CharField(max_length=255, null=True, verbose_name='наименование'),
        ),
        migrations.AlterField(
            model_name='room',
            name='prepayment_percent',
            field=models.FloatField(null=True, verbose_name='предоплата'),
        ),
        migrations.AlterField(
            model_name='room',
            name='refund_percent',
            field=models.FloatField(null=True, verbose_name='возврат'),
        ),
        migrations.AlterField(
            model_name='room',
            name='room_number',
            field=models.SmallIntegerField(null=True, verbose_name='номер комнаты'),
        ),
        migrations.AlterUniqueTogether(
            name='room',
            unique_together={('room_number', 'date_deleted')},
        ),
    ]
