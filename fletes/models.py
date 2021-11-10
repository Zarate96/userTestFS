from django.db import models
from usuarios.models import MyUser
from django.urls import reverse
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import post_save

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
    folio = models.CharField(verbose_name="Folio", max_length=20, editable=False, unique = True)
    creado = models.DateTimeField(editable=False)
    modificado = models.DateTimeField()
    descripcion_servicio = models.TextField(verbose_name="Descripción de servicio")
    caracteristicas_carga = models.TextField(verbose_name="Tipo de carga")
    peso_carga = models.FloatField(verbose_name="Peso de la carga(kg)")
    volumen_carga = models.FloatField(verbose_name="Volumen de la carga(mts3)")
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
    #estado de la solicitud

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.creado = timezone.now()
        self.modificado = timezone.now()
        return super(Solicitud, self).save(*args, **kwargs)
    
    def __str__(self):
        return f'{self.folio}' 
    
    def get_absolute_url(self):
        return reverse('detail-solicitud', kwargs={'pk':self.pk})


def createFolioSolicitud(sender,instance,**kwargs):
    folio = instance.id
    print(folio)
    Solicitud.objects.filter(
            id=folio
        ).update(
            folio=f'SC{instance.cliente_id.username}00{folio}'
        )

post_save.connect(createFolioSolicitud, sender=Solicitud)

@receiver(post_save, sender=Solicitud)
def create_ruta(sender, instance, created, **kwargs):
    if created:
        Ruta.objects.create(solicitud_id=instance)

@receiver(post_save, sender=Solicitud)
def save_ruta(sender, instance, **kwargs):
    instance.ruta.save()

class Ruta(models.Model):
    solicitud_id = models.OneToOneField(Solicitud, on_delete=models.CASCADE)
    creado = models.DateTimeField(editable=False)
    modificado = models.DateTimeField()

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.creado = timezone.now()
        self.modificado = timezone.now()
        return super(Ruta, self).save(*args, **kwargs)
    
    def __str__(self):
        return f'Ruta del folio {self.solicitud_id}' 

class Destino(models.Model):
    ruta_id = models.ForeignKey(Ruta, on_delete=models.CASCADE)
    calle = models.CharField(verbose_name="Calle", max_length=100)
    num_ext = models.CharField(verbose_name="Numero exterior", max_length=100)
    num_int = models.CharField(verbose_name="Numero interior", max_length=100, default="", blank=True)
    colonia = models.CharField(verbose_name="Colonia", max_length=100)
    municipio = models.CharField(verbose_name="Municipio o alcadía", max_length=100,)
    cp = models.CharField(verbose_name="Código postal",max_length=100,)
    tiempo_descarga = models.IntegerField(verbose_name="Tiempo máximo para la descarga(min)")
    estado = models.CharField(verbose_name="Estado", choices=ESTADOS, max_length=40, default="Aguascalientes") 
    unidades_entregar = models.IntegerField(verbose_name="Unidades a entregar en este destino")

    def __str__(self):
        return f'Destino {self.id} de {self.ruta_id}' 