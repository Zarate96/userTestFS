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
    municipio = models.CharField(verbose_name="Municipio o alcadía", max_length=100,)
    cp = models.CharField(verbose_name="Código postal",max_length=100,)
    estado = models.CharField(verbose_name="Estado", choices=ESTADOS, max_length=40)
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
    domicilio_id = models.ForeignKey(Domicilios, on_delete=models.PROTECT, verbose_name="Domicilio")
    estado_solicitud = models.CharField(verbose_name="Estado", choices=ESTADO_SOLICITUD, max_length=40, default="Guardada")
    slug = models.SlugField(null=True, blank=True)
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
)

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
    slug = models.SlugField(null=True, blank=True)
    activo = models.BooleanField(
        verbose_name="Activo",
        default=True,)

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
    print(solicitud)
    if not solicitud.has_cotizaciones():
        solicitud.estado_solicitud = "Publicada"
        solicitud.save()

# ejemplos de signals
# @receiver(post_save, sender=Solicitud)
# def save_ruta(sender, instance, **kwargs):
#     instance.ruta.save() 