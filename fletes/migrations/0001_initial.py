# Generated by Django 3.2 on 2022-07-08 04:03

from django.db import migrations, models
import django.db.models.deletion
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
                ('folio', models.CharField(max_length=20, unique=True, verbose_name='Folio')),
                ('estado_cotizacion', models.CharField(choices=[('Pendiente', 'Pendiente'), ('Aceptada', 'Aceptada'), ('Rechazada', 'Rechazada'), ('Confirmada', 'Confirmada'), ('Cancelada', 'Cancelada'), ('Solicitud cancelada', 'Solicitud cancelada'), ('Pagada', 'Pagada'), ('Pendiente de pago', 'Pendiente de pago')], default='Pendiente', max_length=40, verbose_name='Estado')),
                ('motivo_cancelacion', models.TextField(blank=True, null=True, verbose_name='Motivo de cancelación')),
                ('fecha_servicio', models.DateTimeField(blank=True, default=None, null=True, verbose_name='Fecha de servicio de solictud')),
                ('correo_recordatorio', models.IntegerField(default=0, verbose_name='Corrreos enviados para recordatorio de confirmación')),
                ('total', models.FloatField(blank=True, null=True, verbose_name='Total')),
                ('slug', models.SlugField(blank=True, null=True)),
                ('es_asegurada', models.BooleanField(default=False, verbose_name='Viaje asegurado')),
                ('aceptar_tyc', models.BooleanField(default=False, verbose_name='Aceptación de términos y condiciones de seguro')),
                ('activo', models.BooleanField(default=True, verbose_name='Activo')),
            ],
            options={
                'verbose_name_plural': 'Cotizaciones',
            },
        ),
        migrations.CreateModel(
            name='Destino',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tiempo_descarga', models.IntegerField(verbose_name='Tiempo máximo para la descarga(min)')),
                ('unidades_entregar', models.IntegerField(verbose_name='Unidades a entregar en este destino')),
                ('foto1', models.ImageField(blank=True, null=True, upload_to='unidades_pics', verbose_name='Foto 1 evidencia de entrega')),
                ('foto2', models.ImageField(blank=True, null=True, upload_to='unidades_pics', verbose_name='Foto 2 evidencia de entrega')),
                ('foto3', models.ImageField(blank=True, null=True, upload_to='unidades_pics', verbose_name='Foto 3 evidencia de entrega')),
                ('foto4', models.ImageField(blank=True, null=True, upload_to='unidades_pics', verbose_name='Foto 4 evidencia de entrega')),
                ('foto5', models.ImageField(blank=True, null=True, upload_to='unidades_pics', verbose_name='Foto 5 evidencia de entrega')),
            ],
            options={
                'verbose_name_plural': 'Destinos',
            },
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
                ('longitud', models.FloatField(blank=True, null=True, verbose_name='Longitud')),
                ('latitud', models.FloatField(blank=True, null=True, verbose_name='Latitud')),
                ('is_valid', models.BooleanField(default=False, verbose_name='Es válido')),
                ('google_format', models.CharField(blank=True, max_length=100, null=True, verbose_name='Dirección completa')),
                ('google_place_id', models.CharField(blank=True, max_length=100, null=True, verbose_name='Google place ID')),
                ('slug', models.SlugField(blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Domicilios',
            },
        ),
        migrations.CreateModel(
            name='Orden',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('link_id', models.CharField(blank=True, max_length=500, null=True)),
                ('link_url', models.URLField(blank=True, max_length=500, null=True)),
                ('link_status', models.CharField(blank=True, max_length=200, null=True)),
                ('orden_id', models.CharField(blank=True, max_length=200, null=True)),
                ('orden_status', models.CharField(blank=True, max_length=200, null=True)),
                ('correo_recordatorio', models.IntegerField(default=0, verbose_name='Corrreos enviados para recordatorio de pago')),
            ],
            options={
                'verbose_name_plural': 'Ordenes',
            },
        ),
        migrations.CreateModel(
            name='Seguro',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(default='', max_length=40, verbose_name='Seguro')),
                ('costo', models.FloatField(verbose_name='Costo del seguro')),
                ('cobertura', models.FloatField(verbose_name='Cobertura del seguro')),
            ],
            options={
                'verbose_name_plural': 'Seguros',
            },
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
                ('estado_solicitud', models.CharField(choices=[('Guardada', 'Guardada'), ('Publicada', 'Publicada'), ('Cotizada', 'Cotizada'), ('Asignada', 'Asignada'), ('Pagada', 'Pagada'), ('Cancelada', 'Cancelada'), ('Vencida', 'Vencida')], default='Guardada', max_length=40, verbose_name='Estado de la solicitud')),
                ('tiempo_total', models.FloatField(blank=True, null=True, verbose_name='Tiempo total del viaje')),
                ('km_total', models.FloatField(blank=True, null=True, verbose_name='Km totales del viaje')),
                ('slug', models.SlugField(blank=True, null=True)),
                ('material_peligroso', models.BooleanField(default=False, verbose_name='Es material peligroso')),
                ('estado_origen', models.CharField(blank=True, choices=[('Aguascalientes', 'Aguascalientes'), ('Baja California', 'Baja California'), ('Baja California Sur', 'Baja California Sur'), ('Campeche', 'Campeche'), ('Coahuila de Zaragoza', 'Coahuila de Zaragoza'), ('Colima', 'Colima'), ('Chiapas', 'Chiapas'), ('Chihuahua', 'Chihuahua'), ('CDMX', 'CDMX'), ('Durango', 'Durango'), ('Guanajuato', 'Guanajuato'), ('Guerrero', 'Guerrero'), ('Hidalgo', 'Hidalgo'), ('Jalisco', 'Jalisco'), ('México', 'México'), ('Michoacán de Ocampo', 'Michoacán de Ocampo'), ('Morelos', 'Morelos'), ('Nayarit', 'Nayarit'), ('Nuevo León', 'Nuevo León'), ('Oaxaca', 'Oaxaca'), ('Puebla', 'Puebla'), ('Querétaro', 'Querétaro'), ('Quintana Roo', 'Quintana Roo'), ('San Luis Potosí', 'San Luis Potosí'), ('Sinaloa', 'Sinaloa'), ('Sonora', 'Sonora'), ('Tabasco', 'Tabasco'), ('Tamaulipas', 'Tamaulipas'), ('Tlaxcala', 'Tlaxcala'), ('Veracruz de Ignacio de la Llave', 'Veracruz de Ignacio de la Llave'), ('Yucatán', 'Yucatán'), ('Zacatecas', 'Zacatecas')], max_length=40, null=True, verbose_name='Estado')),
                ('motivo_cancelacion', models.TextField(blank=True, null=True, verbose_name='Motivo de cancelación')),
                ('activo', models.BooleanField(default=True, verbose_name='Activo')),
            ],
            options={
                'verbose_name_plural': 'Solicitudes',
            },
        ),
        migrations.CreateModel(
            name='Viaje',
            fields=[
                ('orden_id', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='fletes.orden')),
                ('folio', models.CharField(default='', max_length=20, verbose_name='Folio')),
                ('slug', models.SlugField(default='', null=True)),
                ('estado_viaje', models.CharField(choices=[('Creado', 'Creado'), ('Iniciado', 'Iniciado'), ('Cerrado', 'Cerrado'), ('Pendiente de pago', 'Pendiente de pago'), ('Terminado', 'Terminado'), ('Disputa', 'Disputa'), ('Accidente', 'Accidente'), ('Cancelado por cliente', 'Cancelado por cliente'), ('Cancelado por transportista', 'Cancelado por transportista')], default='Creado', max_length=40, verbose_name='Estado')),
                ('hora_inicio', models.TimeField(blank=True, null=True, verbose_name='Hora de inicio')),
                ('hora_llegada', models.TimeField(blank=True, null=True, verbose_name='Hora de llegada')),
                ('nip_checkin', models.IntegerField(blank=True, null=True, verbose_name='NIP de seguridad checkin')),
                ('nip_checkout', models.IntegerField(blank=True, null=True, verbose_name='NIP de seguridad checkout')),
                ('comentarios', models.TextField(blank=True, null=True)),
                ('fecha_servicio', models.DateTimeField(blank=True, default=None, null=True, verbose_name='Fecha de servicio de solictud')),
                ('factura_pdf', models.FileField(blank=True, null=True, upload_to='uploads/%Y/%m/%d/', verbose_name='Factura pdf')),
                ('factura_xml', models.FileField(blank=True, null=True, upload_to='uploads/%Y/%m/%d/', verbose_name='Factura xml')),
                ('es_validado', models.BooleanField(default=False, verbose_name='¿Esta válido por cliente?')),
                ('motivo_cancelacion', models.TextField(blank=True, null=True, verbose_name='Motivo de cancelación')),
            ],
            options={
                'verbose_name_plural': 'Viajes',
            },
        ),
    ]
