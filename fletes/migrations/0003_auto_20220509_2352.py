# Generated by Django 3.2 on 2022-05-10 04:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fletes', '0002_auto_20220509_2304'),
    ]

    operations = [
        migrations.AddField(
            model_name='viaje',
            name='factura_pdf',
            field=models.FileField(blank=True, null=True, upload_to='uploads/%Y/%m/%d/', verbose_name='Factura pdf'),
        ),
        migrations.AddField(
            model_name='viaje',
            name='factura_xml',
            field=models.FileField(blank=True, null=True, upload_to='uploads/%Y/%m/%d/', verbose_name='Factura xml'),
        ),
    ]