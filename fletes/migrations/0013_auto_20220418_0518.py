# Generated by Django 3.2 on 2022-04-18 05:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fletes', '0012_alter_orden_orden_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='viaje',
            name='nip',
        ),
        migrations.AddField(
            model_name='viaje',
            name='nip_checkin',
            field=models.IntegerField(blank=True, null=True, verbose_name='NIP de seguridad checkin'),
        ),
        migrations.AddField(
            model_name='viaje',
            name='nip_checkout',
            field=models.IntegerField(blank=True, null=True, verbose_name='NIP de seguridad checkout'),
        ),
    ]