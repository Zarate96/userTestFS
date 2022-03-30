# Generated by Django 3.2 on 2022-03-24 21:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fletes', '0004_cotizacion_total'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cotizacion',
            name='checkoutUrl',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='cotizacion',
            name='motivo_cancelacion',
            field=models.TextField(blank=True, null=True, verbose_name='Motivo de cancelación'),
        ),
        migrations.AlterField(
            model_name='seguro',
            name='cobertura',
            field=models.FloatField(verbose_name='Costo del seguro'),
        ),
    ]
