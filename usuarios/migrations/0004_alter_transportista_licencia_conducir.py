# Generated by Django 3.2 on 2022-06-21 03:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0003_auto_20220620_1658'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transportista',
            name='licencia_conducir',
            field=models.CharField(blank=True, default='', max_length=50, null=True, verbose_name='Número de licencia de conducir'),
        ),
    ]
