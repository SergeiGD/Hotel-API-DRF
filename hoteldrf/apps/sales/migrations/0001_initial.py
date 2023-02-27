# Generated by Django 4.1.7 on 2023-02-27 04:45

import apps.core.utils
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('rooms', '0011_roomcategory_tags'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sale',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='наименование')),
                ('description', models.TextField(blank=True, null=True, verbose_name='описание')),
                ('discount', models.FloatField(verbose_name='скидка')),
                ('image', models.ImageField(upload_to=apps.core.utils.build_photo_path)),
                ('start_date', models.DateField(verbose_name='дата начала')),
                ('end_date', models.DateField(verbose_name='дата завершения')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='дата создания')),
                ('date_deleted', models.DateTimeField(blank=True, null=True, verbose_name='дата удаления')),
                ('applies_to', models.ManyToManyField(blank=True, related_name='sales', related_query_name='sale', to='rooms.roomcategory', verbose_name='действует на')),
            ],
            options={
                'ordering': ['-name'],
            },
        ),
    ]