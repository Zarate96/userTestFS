from django.db import models
from usuarios.models import MyUser

ESTADOS = (
    ('Aguascalientes','Aguascalientes'),
    ('Baja California','Baja California'),
    ('Baja California Sur','Baja California Sur'),
    ('Campeche','Campeche'),
    ('Coahuila de Zaragoza','Coahuila de Zaragoza'),
    ('Colima','Colima'),
    ('Chiapas','Chiapas'),
    ('Chihuahua','Chihuahua'),
    ('CDMX','CDMX'),
    ('Durango','Durango'),
    ('Guanajuato','Guanajuato'),
    ('Guerrero','Guerrero'),
    ('Hidalgo','Hidalgo'),
    ('Jalisco','Jalisco'),
    ('México','México'),
    ('Michoacán de Ocampo','Michoacán de Ocampo'),
    ('Morelos','Morelos'),
    ('Nayarit','Nayarit'),
    ('Nuevo León','Nuevo León'),
    ('Oaxaca','Oaxaca'),
    ('Puebla','Puebla'),
    ('Querétaro','Querétaro'),
    ('Quintana Roo','Quintana Roo'),
    ('San Luis Potosí','San Luis Potosí'),
    ('Sinaloa','Sinaloa'),
    ('Sonora','Sonora'),
    ('Tabasco','Tabasco'),
    ('Tamaulipas','Tamaulipas'),
    ('Tlaxcala','Tlaxcala'),
    ('Veracruz de Ignacio de la Llave','Veracruz de Ignacio de la Llave'),
    ('Yucatán','Yucatán'),
    ('Zacatecas','Zacatecas'),
)

class Solicitud(models.Model):
    cliente_id = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    folio = models.CharField(verbose_name="Folio", max_length=20, editable=False)
    creado = models.DateTimeField(editable=False)
    modificado = models.DateTimeField()
    descripcion_servicio = models.TextField(verbose_name="Descripción de servicio")
    caracteristicas_carga = models.TextField(verbose_name="Características de la carga")
    peso_carga = models.FloatField(verbose_name="Peso de la carga(kg)")
    volumen_carga = models.FloatField(verbose_name="Volumen de la carga")
    unidades_totales = models.IntegerField(verbose_name="Unidades totales de la carga")
    fecha_servicio = models.DateTimeField(verbose_name="Fecha de servicio")
    hora = models.TimeField(verbose_name="Hora de servicio")
    tiempo_carga = models.IntegerField(verbose_name="Tiempo máximo para la carga(min)")
    calle = models.CharField(verbose_name="Calle", max_length=100)
    num_ext = models.CharField(verbose_name="Numero exterior", max_length=100)
    num_int = models.CharField(verbose_name="Numero interior", max_length=100, default="", blank=True)
    colonia = models.CharField(verbose_name="Colonia", max_length=100)
    municipio = models.CharField(verbose_name="Municipio o alcadía", max_length=100,)
    cp = models.CharField(verbose_name="Código postal",max_length=100,)
    estado = models.CharField(verbose_name="Estado", choices=ESTADOS, max_length=40)
    
    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.creado = timezone.now()
        self.modificado = timezone.now()
        self.folio = f'SC{self.cliente_id.username}21{self.id}'
        return super(Solicitud, self).save(*args, **kwargs)

class Ruta(models.Model):
    solicitud_id = models.ForeignKey(Solicitud, on_delete=models.CASCADE)
    creado = models.DateTimeField(editable=False)
    modificado = models.DateTimeField()

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.creado = timezone.now()
        self.modificado = timezone.now()
        return super(Solicitud, self).save(*args, **kwargs)

class Destino(models.Model):
    ruta_id = models.ForeignKey(Ruta, on_delete=models.CASCADE)
    tiempo_carga = models.IntegerField(verbose_name="Tiempo máximo para la carga(min)")
    calle = models.CharField(verbose_name="Calle", max_length=100)
    num_ext = models.CharField(verbose_name="Numero exterior", max_length=100)
    num_int = models.CharField(verbose_name="Numero interior", max_length=100, default="", blank=True)
    colonia = models.CharField(verbose_name="Colonia", max_length=100)
    municipio = models.CharField(verbose_name="Municipio o alcadía", max_length=100,)
    cp = models.CharField(verbose_name="Código postal",max_length=100,)
    tiempo_descarga = models.IntegerField(verbose_name="Tiempo máximo para la descarga(min)")
    unidades_entregar = models.IntegerField(verbose_name="Unidades a entregar en este destino")