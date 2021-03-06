# Generated by Django 3.2 on 2022-07-25 19:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0003_encierro_verificador_direccion'),
    ]

    operations = [
        migrations.AddField(
            model_name='verifaciones_encierros',
            name='notas_verificador',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Notas sobre la verificación del verifiador'),
        ),
        migrations.AlterField(
            model_name='verifaciones',
            name='estado_verificacion',
            field=models.CharField(choices=[('Asignada', 'Asignada'), ('Disputa', 'Disputa'), ('Invalida', 'Invalida'), ('Realizada', 'Realizada'), ('Pendiente', 'Pendiente')], max_length=40, verbose_name='Estado'),
        ),
        migrations.AlterField(
            model_name='verifaciones_encierros',
            name='estado_verificacion',
            field=models.CharField(choices=[('Asignada', 'Asignada'), ('Disputa', 'Disputa'), ('Invalida', 'Invalida'), ('Realizada', 'Realizada'), ('Pendiente', 'Pendiente')], max_length=40, verbose_name='Estado'),
        ),
    ]
