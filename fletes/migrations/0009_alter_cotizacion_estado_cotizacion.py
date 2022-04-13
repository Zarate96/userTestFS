# Generated by Django 3.2 on 2022-03-31 21:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fletes', '0008_alter_domicilios_is_valid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cotizacion',
            name='estado_cotizacion',
            field=models.CharField(choices=[('Pendiente', 'Pendiente'), ('Aceptada', 'Aceptada'), ('Rechazada', 'Rechazada'), ('Confirmada', 'Confirmada'), ('Cancelada', 'Cancelada'), ('Solicitud cancelada', 'Solicitud cancelada'), ('Pagada', 'Pagada'), ('Pendiente de pago', 'Pendiente de pago')], default='Pendiente', max_length=40, verbose_name='Estado'),
        ),
    ]