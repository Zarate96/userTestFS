# Generated by Django 3.2 on 2022-04-13 05:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fletes', '0009_alter_cotizacion_estado_cotizacion'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cotizacion',
            name='checkoutUrl',
        ),
        migrations.AlterField(
            model_name='seguro',
            name='cobertura',
            field=models.FloatField(verbose_name='Cobertura del seguro'),
        ),
        migrations.CreateModel(
            name='Orden',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('link_id', models.CharField(blank=True, max_length=200, null=True)),
                ('link_url', models.URLField(blank=True, null=True)),
                ('link_status', models.CharField(blank=True, max_length=200, null=True)),
                ('orden_id', models.CharField(blank=True, max_length=200, null=True)),
                ('orden_status', models.CharField(blank=True, max_length=200, null=True)),
                ('cotizacion_id', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='fletes.cotizacion')),
            ],
        ),
    ]