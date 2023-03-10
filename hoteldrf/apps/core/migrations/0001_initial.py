# Generated by Django 4.1.7 on 2023-03-03 06:07

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='IdempotencyKey',
            fields=[
                ('id', models.UUIDField(editable=False, primary_key=True, serialize=False)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddIndex(
            model_name='idempotencykey',
            index=models.Index(fields=['date_created'], name='core_idempo_date_cr_33c8e4_idx'),
        ),
    ]
