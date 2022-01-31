import googlemaps
import json
from django.db import models
from usuarios.models import MyUser, Cliente, Transportista, Unidades
from django.urls import reverse
from django.utils import timezone
from django.dispatch import receiver
from django.utils.text import slugify
from django.db.models.signals import post_save, post_delete
from django.core.exceptions import ValidationError


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

class Domicilios(models.Model):
    cliente_id = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    creado = models.DateTimeField(editable=False)
    modificado = models.DateTimeField()
    nombre = models.CharField(verbose_name="Nombre para identificar domicilio", max_length=100)
    calle = models.CharField(verbose_name="Calle", max_length=100)
    num_ext = models.CharField(verbose_name="Numero exterior", max_length=100)
    num_int = models.CharField(verbose_name="Numero interior", max_length=100, default="", blank=True)
    colonia = models.CharField(verbose_name="Colonia", max_length=100)
    municipio = models.CharField(verbose_name="Municipio o alcadía", max_length=100)
    cp = models.CharField(verbose_name="Código postal",max_length=100,)
    estado = models.CharField(verbose_name="Estado", choices=ESTADOS, max_length=40)
    referencias = models.TextField(verbose_name="Refrencias del domicilio")
    longitud = models.FloatField(verbose_name="Longitud", null=True, blank=True)
    latitud = models.FloatField(verbose_name="Latitud", null=True, blank=True)
    is_valid = models.BooleanField(verbose_name="Es válido", default=True)
    google_format = models.CharField(verbose_name="Dirección completa", max_length=100, null=True, blank=True)
    google_place_id = models.CharField(verbose_name="Google place ID", max_length=40, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True)

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.creado = timezone.now()
        self.modificado = timezone.now()
        if self.slug is None:
            self.slug = slugify(f"{self.nombre}-{self.cliente_id}")
        return super(Domicilios, self).save(*args, **kwargs)
    
    def __str__(self):
        return f'{self.nombre}' 
    
ESTADO_SOLICITUD = (
    ('Guardada','Guardada'),
    ('Publicada','Publicada'),
    ('Cotizada','Cotizada'),
    ('Asignada','Asignada'),
    ('Cancelada','Cancelada'),
)

def validate_date(date):
    if date.date() <= timezone.now().date():
        raise ValidationError("La fecha tiene que ser mayor a hoy")

class Solicitud(models.Model):
    cliente_id = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    folio = models.CharField(verbose_name="Folio", max_length=20, editable=False, unique = True)
    creado = models.DateTimeField(editable=False)
    modificado = models.DateTimeField()
    descripcion_servicio = models.TextField(verbose_name="Descripción de servicio")
    caracteristicas_carga = models.TextField(verbose_name="Tipo de carga")
    peso_carga = models.FloatField(verbose_name="Peso de la carga(kg)")
    volumen_carga = models.FloatField(verbose_name="Volumen de la carga(mts3)")
    unidades_totales = models.IntegerField(verbose_name="Unidades totales de la carga")
    fecha_servicio = models.DateTimeField(verbose_name="Fecha de servicio", validators=[validate_date])
    hora = models.TimeField(verbose_name="Hora de servicio")
    tiempo_carga = models.IntegerField(verbose_name="Tiempo máximo para la carga(min)")
    domicilio_id = models.ForeignKey(Domicilios, on_delete=models.PROTECT, verbose_name="Origen")
    estado_solicitud = models.CharField(verbose_name="Estado", choices=ESTADO_SOLICITUD, max_length=40, default="Guardada")
    tiempo_total = models.FloatField(verbose_name="Tiempo total del viaje", null=True, blank=True)
    km_total = models.FloatField(verbose_name="Km totales del viaje", null=True, blank=True)
    slug = models.SlugField(null=True, blank=True)
    material_peligroso = models.BooleanField(
        verbose_name="Es material peligroso",
        default=False,)
    motivo_cancelacion = models.TextField(verbose_name="Motivo de cancelación")
    activo = models.BooleanField(
        verbose_name="Activo",
        default=True,)

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.creado = timezone.now()
        self.modificado = timezone.now()
        return super(Solicitud, self).save(*args, **kwargs)
    
    def has_destinos(self):
        destinos =  Destino.objects.filter(solicitud_id=self.pk)
        if destinos:
            destinos = list(destinos)
            return "Ruta" if len(destinos) > 1 else "Sencillo"
        else:
            return "Sencillo"
        
    def __str__(self):
        return f'{self.folio}' 
    
    def get_absolute_url(self):
        return reverse('detail-solicitud', kwargs={'pk':self.pk})
    
    def get_domiciliosid_destinos(self):
        destinos = Destino.objects.filter(solicitud_id=self.id)
        lista =[]

        for destino in destinos:
                lista.append(destino.domicilio_id.id)
        
        return lista
    
    def has_cotizaciones(self):
        cotizaciones =  Cotizacion.objects.filter(solicitud_id=self.pk)
        return True if cotizaciones else False

    def cotizacionFinal(self):
        cotizacion = Cotizacion.objects.filter(solicitud_id=self.id).filter(estado_cotizacion='Confirmada')
        return cotizacion[0]


def createFolioSolicitud(sender,instance,**kwargs):
    folio = instance.id
    Solicitud.objects.filter(
            id=folio
        ).update(
            folio=f'SC{instance.cliente_id.user.username}00{folio}',
    )
    if instance.slug is None:
        Solicitud.objects.filter(
                id=folio
            ).update(
                slug=slugify(f"{instance.cliente_id.user.username}-{instance.id}")
    )
    
post_save.connect(createFolioSolicitud, sender=Solicitud)

class Destino(models.Model):
    solicitud_id = models.ForeignKey(Solicitud, on_delete=models.CASCADE)
    domicilio_id = models.ForeignKey(Domicilios, on_delete=models.PROTECT)
    tiempo_descarga = models.IntegerField(verbose_name="Tiempo máximo para la descarga(min)") 
    unidades_entregar = models.IntegerField(verbose_name="Unidades a entregar en este destino")

    def __str__(self):
        return f'Destino {self.id} de {self.solicitud_id}' 

ESTADO_COTIZACION = (
    ('Pendiente','Pendiente'),
    ('Aceptada','Aceptada'),
    ('Rechazada','Rechazada'),
    ('Confirmada','Confirmada'),
    ('Cancelada','Cancelada'),
    ('Solicitud cancelada','Solicitud cancelada'),
    ('Pagada','Pagada'),
)

NIVEL_SEGURO = (
    ('Sin seguro', 'Sin seguro'),
    ('Nivel 1','Nivel 1'),
    ('Nivel 2','Nivel 2'),
    ('Nivel 3','Nivel 3'),
)

class Seguro(models.Model):
    nombre = models.CharField(verbose_name="Seguro", max_length=40, default="")
    costo = models.FloatField(verbose_name="Costo del seguro")
    cobertura = models.TextField()

    def __str__(self):
        return f'{self.nombre}'

class Cotizacion(models.Model):
    transportista_id = models.ForeignKey(
        Transportista, 
        verbose_name="Transportista",
        on_delete=models.CASCADE)
    solicitud_id = models.ForeignKey(
        Solicitud, 
        verbose_name="Solicitud",
        on_delete=models.CASCADE)
    unidad_id = models.ForeignKey(
        Unidades, 
        verbose_name="Unidad",
        on_delete=models.CASCADE)
    creado = models.DateTimeField(editable=False)
    modificado = models.DateTimeField()
    monto = models.FloatField(
        verbose_name="Monto")
    folio = models.CharField(verbose_name="Folio", max_length=20, editable=False, unique = True)
    estado_cotizacion = models.CharField(verbose_name="Estado", choices=ESTADO_COTIZACION, max_length=40, default="Pendiente")
    motivo_cancelacion = models.TextField(verbose_name="Motivo de cancelación")
    slug = models.SlugField(null=True, blank=True)
    nivel_seguro = models.ForeignKey(
        Seguro, 
        verbose_name="Nivel de Seguro",
        on_delete=models.CASCADE,
        null=True)
    es_asegurada = models.BooleanField(
        verbose_name="Viaje asegurado",
        default=False,)
    activo = models.BooleanField(
        verbose_name="Activo",
        default=True,)
    checkoutUrl = models.URLField(max_length = 200, default="")

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.creado = timezone.now()
        self.modificado = timezone.now()
        return super(Cotizacion, self).save(*args, **kwargs)
    
    def __str__(self):
        return f'Cotización de {self.transportista_id} para solicitud {self.solicitud_id}'

@receiver(post_save, sender=Cotizacion)
def create_ruta(sender, instance, **kwargs):
    solicitud = instance.solicitud_id
    if solicitud.estado_solicitud != 'Asignada':
        solicitud.estado_solicitud = "Cotizada"
        solicitud.save()

@receiver(post_save, sender=Cotizacion)
def createFolioCotizacion(sender,instance,**kwargs):
    folio = instance.id
    Cotizacion.objects.filter(
            id=folio
        ).update(
            folio=f'CO{instance.transportista_id.user.username}00{folio}',
    )
    if instance.slug is None:
        Cotizacion.objects.filter(
                id=folio
            ).update(
                slug=slugify(f"{instance.transportista_id.user.username}-{instance.id}")
    )

@receiver(post_delete, sender=Cotizacion)
def validarEsatdoCotizacion(sender,instance,**kwargs):
    solicitud = instance.solicitud_id
    if not solicitud.has_cotizaciones():
        solicitud.estado_solicitud = "Publicada"
        solicitud.save()

@receiver(post_save, sender=Domicilios)
def addLonLat(sender, instance, **kwargs):
    gmaps = googlemaps.Client(key='AIzaSyDHQMz-SW5HQm3IA2hSv2Bct9L76_E60Ec')
    direction = f'{instance.calle} {instance.num_ext} {instance.colonia} {instance.estado}'
    geocode_result = gmaps.geocode(direction)
    direccion_google = geocode_result[0]["formatted_address"]
    if len(geocode_result) == 0 or len(direccion_google) < 50:
        print("\n Favor de ingresar una direccion correcta")
        Domicilios.objects.filter(id=instance.id).update(
            is_valid = False,
            google_format = "Dirección no válida favor de verificar la información"
        )
    else:
        Domicilios.objects.filter(id=instance.id).update(
            latitud = geocode_result[0]["geometry"]["location"]["lat"],
            longitud = geocode_result[0]["geometry"]["location"]["lng"],
            google_place_id = geocode_result[0]["place_id"],
            google_format = direccion_google,
            is_valid = True
        )