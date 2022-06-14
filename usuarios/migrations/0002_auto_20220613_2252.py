# Generated by Django 3.2 on 2022-06-14 03:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='transportista',
            old_name='fecha_vencimiento',
            new_name='fecha_vencimiento_licencia',
        ),
        migrations.AddField(
            model_name='transportista',
            name='licencia_conducir_mp_foto',
            field=models.ImageField(blank=True, null=True, upload_to='licencias_transportistas', verbose_name='Foto de licencia de conducir material peligroso'),
        ),
    ]