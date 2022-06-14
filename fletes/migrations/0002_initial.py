# Generated by Django 3.2 on 2022-06-14 04:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('fletes', '0001_initial'),
        ('usuarios', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='solicitud',
            name='cliente_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='usuarios.cliente'),
        ),
        migrations.AddField(
            model_name='solicitud',
            name='domicilio_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='fletes.domicilios', verbose_name='Origen'),
        ),
        migrations.AddField(
            model_name='orden',
            name='cotizacion_id',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='fletes.cotizacion'),
        ),
        migrations.AddField(
            model_name='domicilios',
            name='cliente_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='usuarios.cliente'),
        ),
        migrations.AddField(
            model_name='destino',
            name='domicilio_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='fletes.domicilios'),
        ),
        migrations.AddField(
            model_name='destino',
            name='solicitud_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fletes.solicitud'),
        ),
        migrations.AddField(
            model_name='cotizacion',
            name='nivel_seguro',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='fletes.seguro', verbose_name='Nivel de Seguro'),
        ),
        migrations.AddField(
            model_name='cotizacion',
            name='solicitud_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fletes.solicitud', verbose_name='Solicitud'),
        ),
        migrations.AddField(
            model_name='cotizacion',
            name='transportista_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='usuarios.transportista', verbose_name='Transportista'),
        ),
        migrations.AddField(
            model_name='cotizacion',
            name='unidad_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='usuarios.unidades', verbose_name='Unidad'),
        ),
    ]
