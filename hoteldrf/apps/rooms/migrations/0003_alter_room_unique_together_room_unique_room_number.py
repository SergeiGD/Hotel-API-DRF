# Generated by Django 4.1.7 on 2023-02-22 11:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0002_alter_room_options_alter_room_default_price_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='room',
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name='room',
            constraint=models.UniqueConstraint(fields=('room_number', 'date_deleted'), name='unique_room_number'),
        ),
    ]
