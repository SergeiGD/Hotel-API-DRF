# Generated by Django 4.1.7 on 2023-03-06 05:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('workers', '0003_alter_worker_salary'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkerTimetable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.DateTimeField(verbose_name='начало')),
                ('end', models.DateTimeField(verbose_name='конец')),
                ('worker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='timetables', related_query_name='timetable', to='workers.worker', verbose_name='сотрудник')),
            ],
        ),
    ]