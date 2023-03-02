# Generated by Django 4.1.7 on 2023-03-02 09:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0001_initial'),
        ('orders', '0006_alter_order_client'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='cart_uuid',
            field=models.UUIDField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='client',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='orders', related_query_name='order', to='clients.client', verbose_name='Клиент'),
        ),
    ]
