# Generated by Django 4.1.7 on 2023-02-24 14:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workers', '0002_worker_salary'),
    ]

    operations = [
        migrations.AlterField(
            model_name='worker',
            name='salary',
            field=models.DecimalField(decimal_places=2, max_digits=10, verbose_name='зарплата'),
        ),
    ]