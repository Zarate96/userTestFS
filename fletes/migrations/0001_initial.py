# Generated by Django 3.2 on 2021-12-15 05:40

from django.db import migrations, models
import fletes.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cotizacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creado', models.DateTimeField(editable=False)),
                ('modificado', models.DateTimeField()),
                ('monto', models.FloatField(verbose_name='Monto')),
                ('folio', models.CharField(editable=False, max_length=20, unique=True, verbose_name='Folio')),
                ('estado_cotizacion', models.CharField(choices=[('Pendiente', 'Pendiente'), ('Aceptada', 'Aceptada'), ('Rechazada', 'Rechazada'), ('Confirmada', 'Confirmada'), ('Cancelada', 'Cancelada'), ('Solicitud cancelada', 'Solicitud cancelada')], default='Pendiente', max_length=40, verbose_name='Estado')),
                ('motivo_cancelacion', models.TextField(verbose_name='Motivo de cancelación')),
                ('slug', models.SlugField(blank=True, null=True)),
                ('activo', models.BooleanField(default=True, verbose_name='Activo')),
            ],
        ),
        migrations.CreateModel(
            name='Destino',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tiempo_descarga', models.IntegerField(verbose_name='Tiempo máximo para la descarga(min)')),
                ('unidades_entregar', models.IntegerField(verbose_name='Unidades a entregar en este destino')),
            ],
        ),
        migrations.CreateModel(
            name='Domicilios',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creado', models.DateTimeField(editable=False)),
                ('modificado', models.DateTimeField()),
                ('nombre', models.CharField(max_length=100, verbose_name='Nombre para identificar domicilio')),
                ('calle', models.CharField(max_length=100, verbose_name='Calle')),
                ('num_ext', models.CharField(max_length=100, verbose_name='Numero exterior')),
                ('num_int', models.CharField(blank=True, default='', max_length=100, verbose_name='Numero interior')),
                ('colonia', models.CharField(max_length=100, verbose_name='Colonia')),
                ('municipio', models.CharField(max_length=100, verbose_name='Municipio o alcadía')),
                ('cp', models.CharField(max_length=100, verbose_name='Código postal')),
                ('estado', models.CharField(choices=[('Aguascalientes', 'Aguascalientes'), ('Baja California', 'Baja California'), ('Baja California Sur', 'Baja California Sur'), ('Campeche', 'Campeche'), ('Coahuila de Zaragoza', 'Coahuila de Zaragoza'), ('Colima', 'Colima'), ('Chiapas', 'Chiapas'), ('Chihuahua', 'Chihuahua'), ('CDMX', 'CDMX'), ('Durango', 'Durango'), ('Guanajuato', 'Guanajuato'), ('Guerrero', 'Guerrero'), ('Hidalgo', 'Hidalgo'), ('Jalisco', 'Jalisco'), ('México', 'México'), ('Michoacán de Ocampo', 'Michoacán de Ocampo'), ('Morelos', 'Morelos'), ('Nayarit', 'Nayarit'), ('Nuevo León', 'Nuevo León'), ('Oaxaca', 'Oaxaca'), ('Puebla', 'Puebla'), ('Querétaro', 'Querétaro'), ('Quintana Roo', 'Quintana Roo'), ('San Luis Potosí', 'San Luis Potosí'), ('Sinaloa', 'Sinaloa'), ('Sonora', 'Sonora'), ('Tabasco', 'Tabasco'), ('Tamaulipas', 'Tamaulipas'), ('Tlaxcala', 'Tlaxcala'), ('Veracruz de Ignacio de la Llave', 'Veracruz de Ignacio de la Llave'), ('Yucatán', 'Yucatán'), ('Zacatecas', 'Zacatecas')], max_length=40, verbose_name='Estado')),
                ('referencias', models.TextField(verbose_name='Refrencias del domicilio')),
                ('slug', models.SlugField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Solicitud',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('folio', models.CharField(editable=False, max_length=20, unique=True, verbose_name='Folio')),
                ('creado', models.DateTimeField(editable=False)),
                ('modificado', models.DateTimeField()),
                ('descripcion_servicio', models.TextField(verbose_name='Descripción de servicio')),
                ('caracteristicas_carga', models.TextField(verbose_name='Tipo de carga')),
                ('peso_carga', models.FloatField(verbose_name='Peso de la carga(kg)')),
                ('volumen_carga', models.FloatField(verbose_name='Volumen de la carga(mts3)')),
                ('unidades_totales', models.IntegerField(verbose_name='Unidades totales de la carga')),
                ('fecha_servicio', models.DateTimeField(validators=[fletes.models.validate_date], verbose_name='Fecha de servicio')),
                ('hora', models.TimeField(verbose_name='Hora de servicio')),
                ('tiempo_carga', models.IntegerField(verbose_name='Tiempo máximo para la carga(min)')),
                ('estado_solicitud', models.CharField(choices=[('Guardada', 'Guardada'), ('Publicada', 'Publicada'), ('Cotizada', 'Cotizada'), ('Asignada', 'Asignada'), ('Cancelada', 'Cancelada')], default='Guardada', max_length=40, verbose_name='Estado')),
                ('slug', models.SlugField(blank=True, null=True)),
                ('material_peligroso', models.BooleanField(default=False, verbose_name='Es material peligroso')),
                ('motivo_cancelacion', models.TextField(verbose_name='Motivo de cancelación')),
                ('activo', models.BooleanField(default=True, verbose_name='Activo')),
            ],
        ),
    ]
