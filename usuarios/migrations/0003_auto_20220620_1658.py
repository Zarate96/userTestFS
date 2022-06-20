# Generated by Django 3.2 on 2022-06-20 21:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0002_auto_20220620_1656'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transportista',
            name='fecha_vencimiento_licencia',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Fecha de vencimiento de la licencia de manejo'),
        ),
        migrations.AlterField(
            model_name='transportista',
            name='licencia_conducir',
            field=models.CharField(default='', max_length=50, null=True, verbose_name='Número de licencia de conducir'),
        ),
        migrations.AlterField(
            model_name='transportista',
            name='licencia_conducir_foto',
            field=models.ImageField(blank=True, null=True, upload_to='licencias_transportistas', verbose_name='Foto de licencia de conducir'),
        ),
        migrations.AlterField(
            model_name='transportista',
            name='licencia_conducir_mp_foto',
            field=models.ImageField(blank=True, null=True, upload_to='licencias_transportistas', verbose_name='Foto de licencia de conducir material peligroso'),
        ),
    ]
