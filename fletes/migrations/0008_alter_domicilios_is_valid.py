# Generated by Django 3.2 on 2022-03-31 04:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fletes', '0007_cotizacion_aceptar_tyc'),
    ]

    operations = [
        migrations.AlterField(
            model_name='domicilios',
            name='is_valid',
            field=models.BooleanField(default=False, verbose_name='Es válido'),
        ),
    ]