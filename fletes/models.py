import googlemaps
import json
import random
from datetime import date as todaysDate
from django.utils.timezone import make_aware
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
    is_valid = models.BooleanField(verbose_name="Es válido", default=False)
    google_format = models.CharField(verbose_name="Dirección completa", max_length=100, null=True, blank=True)
    google_place_id = models.CharField(verbose_name="Google place ID", max_length=100, null=True, blank=True)
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
    ('Pagada','Pagada'),
    ('Cancelada','Cancelada'),
    
)

def validate_date(date):
    if date.date() <= todaysDate.today():
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
    estado_solicitud = models.CharField(verbose_name="Estado de la solicitud", choices=ESTADO_SOLICITUD, max_length=40, default="Guardada")
    tiempo_total = models.FloatField(verbose_name="Tiempo total del viaje", null=True, blank=True)
    km_total = models.FloatField(verbose_name="Km totales del viaje", null=True, blank=True)
    slug = models.SlugField(null=True, blank=True)
    material_peligroso = models.BooleanField(
        verbose_name="Es material peligroso",
        default=False,)
    estado_origen = models.CharField(verbose_name="Estado", choices=ESTADOS, max_length=40,  null=True, blank=True)
    motivo_cancelacion = models.TextField(verbose_name="Motivo de cancelación",  null=True, blank=True)
    activo = models.BooleanField(
        verbose_name="Activo",
        default=True,)

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.creado = timezone.now()
        self.modificado = timezone.now()
        if not self.estado_origen:
            self.estado_origen = self.domicilio_id.estado
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
        cotizacion = Cotizacion.objects.filter(solicitud_id=self.id).filter(estado_cotizacion='Confirmada') | Cotizacion.objects.filter(solicitud_id=self.id).filter(estado_cotizacion='Pagada') | Cotizacion.objects.filter(solicitud_id=self.id).filter(estado_cotizacion='Pendiente de pago')
        return cotizacion[0] if cotizacion else False

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
    foto1 = models.ImageField(verbose_name="Foto 1 evidencia de entrega", upload_to='unidades_pics', null=True, blank=True)
    foto2 = models.ImageField(verbose_name="Foto 2 evidencia de entrega", upload_to='unidades_pics', null=True, blank=True)
    foto3 = models.ImageField(verbose_name="Foto 3 evidencia de entrega", upload_to='unidades_pics', null=True, blank=True)
    foto4 = models.ImageField(verbose_name="Foto 4 evidencia de entrega", upload_to='unidades_pics', null=True, blank=True)
    foto5 = models.ImageField(verbose_name="Foto 5 evidencia de entrega", upload_to='unidades_pics', null=True, blank=True)
    #registro de llegada
    #registo de hora de llegada

    def __str__(self):
        return f'Destino {self.id} de {self.solicitud_id}' 
    
    def hasEvidencias(self):
        return True if self.foto1 else False

#Cambiar Rechazada a No exitosa
ESTADO_COTIZACION = (
    ('Pendiente','Pendiente'),
    ('Aceptada','Aceptada'),
    ('Rechazada','Rechazada'),
    ('Confirmada','Confirmada'),
    ('Cancelada','Cancelada'),
    ('Solicitud cancelada','Solicitud cancelada'),
    ('Pagada','Pagada'),
    ('Pendiente de pago','Pendiente de pago')
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
    cobertura = models.FloatField(verbose_name="Cobertura del seguro")

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
    folio = models.CharField(verbose_name="Folio", max_length=20, editable=True, unique = True)
    estado_cotizacion = models.CharField(verbose_name="Estado", choices=ESTADO_COTIZACION, max_length=40, default="Pendiente")
    motivo_cancelacion = models.TextField(verbose_name="Motivo de cancelación", null=True, blank=True)
    total = models.FloatField(
        verbose_name="Total", null=True, blank=True)
    slug = models.SlugField(null=True, blank=True)
    nivel_seguro = models.ForeignKey(
        Seguro, 
        verbose_name="Nivel de Seguro",
        on_delete=models.CASCADE,
        null=True,
        blank=True)
    es_asegurada = models.BooleanField(
        verbose_name="Viaje asegurado",
        default=False,)
    aceptar_tyc = models.BooleanField(
        verbose_name="Aceptación de términos y condiciones de seguro",
        default=False,)
    activo = models.BooleanField(
        verbose_name="Activo",
        default=True,)

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        iva = 0.16
        if not self.id:
            self.creado = timezone.now()
        
        self.total = 0
        if self.es_asegurada:
            subtotal = self.monto + self.nivel_seguro.costo
        else:
            subtotal = self.monto
        self.total = int(subtotal + subtotal * iva)
        
        self.modificado = timezone.now()
        
        return super(Cotizacion, self).save(*args, **kwargs)
    
    def __str__(self):
        return f'{self.folio}'
    
    def getClienteId(self):
        cliente_id = self.solicitud_id.cliente_id
        return cliente_id

ESTADO_ORDEN = (
    ('paid','paid'),
    ('Pendiente','Pendiente'),
)

class Orden(models.Model):
    cotizacion_id = models.OneToOneField(Cotizacion, on_delete=models.CASCADE)
    link_id = models.CharField(max_length = 500, null=True, blank=True)
    link_url = models.URLField(max_length = 500, null=True, blank=True)
    link_status = models.CharField(max_length = 200, null=True, blank=True)
    orden_id = models.CharField(max_length = 200, null=True, blank=True)
    orden_status = models.CharField(max_length = 200, null=True, blank=True)

    def __str__(self):
        return f'Orden de cotización {self.cotizacion_id}'

    def has_orden(self):
        return True if self.orden_id else False 

ESTADO_VIAJE = (
    ('Creado','Creado'),
    ('Iniciado','Iniciado'),
    ('Cerrado','Cerrado'),
    ('Pendiente pago','Pendiente pago'),
    ('Terminado','Terminado'),
    ('Disputa','Disputa'),
    ('Accidente','Accidente'),
)

class Viaje(models.Model):
    orden_id = models.OneToOneField(Orden, on_delete=models.CASCADE, primary_key=True)
    folio = models.CharField(verbose_name="Folio", max_length=20,  default="")
    slug = models.SlugField(null=True, default="")
    estado_viaje = models.CharField(verbose_name="Estado", choices=ESTADO_VIAJE, max_length=40, default="Creado")
    hora_inicio = models.TimeField(verbose_name="Hora de inicio", null=True, blank=True)
    hora_llegada = models.TimeField(verbose_name="Hora de llegada", null=True, blank=True)
    localizacion_transportista = models.CharField(verbose_name="Localización de transportista", max_length=40)
    nip_checkin = models.IntegerField(verbose_name="NIP de seguridad checkin", null=True, blank=True)
    nip_checkout = models.IntegerField(verbose_name="NIP de seguridad checkout", null=True, blank=True)
    comentarios = models.TextField(null=True, blank=True)
    factura_pdf = models.FileField(upload_to='uploads/%Y/%m/%d/', verbose_name="Factura pdf", null=True, blank=True)
    factura_xml = models.FileField(upload_to='uploads/%Y/%m/%d/', verbose_name="Factura xml", null=True, blank=True)
    es_validado = models.BooleanField(verbose_name="¿Esta válido por cliente?", default=False)

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if self.nip_checkin is None:
            number = f'{random.randint(1,9)}{random.randint(0,9)}{random.randint(0,9)}{random.randint(0,9)}'
            self.nip_checkin = int(number)
        if self.nip_checkout is None:
            number = f'{random.randint(1,9)}{random.randint(0,9)}{random.randint(0,9)}{random.randint(0,9)}'
            self.nip_checkout = int(number)
        if self.folio is None or self.folio == "":
            self.folio = f'FS{self.orden_id.cotizacion_id.getClienteId()}00{self.orden_id.cotizacion_id.id}'
        if self.slug is None or self.slug == "":
            self.slug = f'FS{self.orden_id.cotizacion_id.getClienteId()}00{self.orden_id.cotizacion_id.id}'
        return super(Viaje, self).save(*args, **kwargs)
    
    def __str__(self):
        return f'{self.folio}'

    def getClienteId(self):
        return self.orden_id.cotizacion_id.getClienteId()
    
    def hasLlegada(self):
        return True if self.hora_llegada else False

    def hasInicio(self):
        return True if self.hora_inicio else False

        
#signals
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
            google_format = "Invalid"
        )
    else:
        Domicilios.objects.filter(id=instance.id).update(
            latitud = geocode_result[0]["geometry"]["location"]["lat"],
            longitud = geocode_result[0]["geometry"]["location"]["lng"],
            google_place_id = geocode_result[0]["place_id"],
            google_format = direccion_google,
            is_valid = True
        )

@receiver(post_save, sender=Orden)
def crearViaje(sender, instance, **kwargs):
    orden = instance

    if orden.orden_status == 'Pagada':
        viaje = Viaje.objects.create(orden_id=orden)


# @receiver(post_save, sender=Cotizacion)
# def estadoPago(sender, instance, **kwargs):
#     cotizacion = instance

#     if cotizacion.estado_cotizacion == 'Confirmada' and cotizacion.checkoutUrl:
#         Cotizacion.objects.filter(id=instance.id).update(
#             estado_cotizacion = 'Pendiente de pago'
#         )
        

# @receiver(post_save, sender=Viaje)
# def createFolioViaje(sender,instance,**kwargs):
#     print(instance.id)
#     folio = instance.id
#     Viaje.objects.filter(
#             id=folio
#         ).update(
#             folio=f'FLE00{folio}',
#     )
#     if instance.slug is None or instance.slug == "":
#         Viaje.objects.filter(
#                 id=folio
#             ).update(
#                 slug=slugify(f"fle-{instance.id}")
#     )