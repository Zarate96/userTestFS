import datetime
import conekta
import requests
from django.dispatch import receiver
from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import AbstractUser
from http.client import HTTPSConnection
from base64 import b64encode
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed

conekta.locale = 'es'
conekta.api_key = settings.SANDBOX_PRIVADA_CONEKTA
conekta.api_version = "2.0.0"

TELEFONIAS = (
    ('Telcel','Telcel'),
    ('Movistar','Movistar'),
    ('Unefón','Unefón'),
    ('AT&T México','AT&T México'),
    ('Altán Redes','Altán Redes'),
)

RADIO_TYPE = (
    ('gsm','gsm'),
    ('lte','lte'),
)

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

class AuditEntry(models.Model):
    action = models.CharField(max_length=64)
    ip = models.GenericIPAddressField(null=True)
    username = models.CharField(max_length=256, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")

    def __unicode__(self):
        return '{0} - {1} - {2}'.format(self.action, self.username, self.ip)

    def __str__(self):
        return '{0} - {1} - {2}'.format(self.action, self.username, self.ip)

    class Meta:
        verbose_name = "Logs in/out"
        verbose_name_plural = "Logs in/out"

class MyUser(AbstractUser):
    email = models.EmailField(max_length=254, unique=True)
    es_transportista = models.BooleanField(default=False)
    es_cliente = models.BooleanField(default=False)
    es_empresa = models.BooleanField(
        verbose_name="Persona moral",
        default=False,
        help_text="Las empresas son personas morales")
    es_validado = models.BooleanField(default=False)
    penalizaciones = models.IntegerField(verbose_name="Número de penalizacionos", default=0)

    class Meta:
        db_table = 'auth_user'
        verbose_name_plural = "Usuarios"

    @property
    def is_cliente(self):
        return self.es_cliente == True

    @property
    def is_empresa(self):
        return self.es_empresa == True

    @property
    def is_transportista(self):
        return self.es_transportista == True

    @property
    def has_datosfiscales(self):
        try:
            if self.datosfiscales.has_rfc:
                return True
            else:
                return False
        except:
            return False

class Cliente(models.Model):
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE, primary_key=True)
    image = models.ImageField(verbose_name="Foto de perfil", default='default.jpg', upload_to='profile_pics')
    nombre = models.CharField(
        verbose_name="Nombre o Razon social(empresas)",
        max_length=100)
    ape_pat = models.CharField(
        verbose_name="Apellido paterno", max_length=100, blank=True, default="")
    ape_mat = models.CharField(
        verbose_name="Apellido materno", max_length=100, blank=True, default="")
    telefono = models.CharField(verbose_name="Numero teléfonico a 10 digitos", max_length=100)
    calle = models.CharField(verbose_name="Calle", max_length=100)
    num_ext = models.CharField(verbose_name="Numero exterior", max_length=100)
    num_int = models.CharField(verbose_name="Numero interior", max_length=100, default="", blank=True)
    colonia = models.CharField(verbose_name="Colonia", max_length=100)
    municipio = models.CharField(verbose_name="Municipio o alcadía", max_length=100,)
    cp = models.CharField(verbose_name="Código postal",max_length=100,)
    estado = models.CharField(verbose_name="Estado", choices=ESTADOS, max_length=40)
    slug = models.SlugField(null=True, blank=True)
    conektaId = models.CharField(verbose_name="Conekta ID", max_length=30, default="", blank=True)

    def __str__(self):
        return str(self.user.username)

    def save(self, *args, **kwargs):
        if self.slug is None:
            self.slug = slugify(self.user.username)

        super(Cliente, self).save(*args, **kwargs)

    @property
    def is_empresa(self):
        return self.user.es_empresa == True

    @property
    def has_info(self):
        if self.telefono == "" and self.municipio == "":
            return False
        else:
            return True

class Transportista(models.Model):
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE, primary_key=True)
    image = models.ImageField(verbose_name="Foto de perfil", default='default.jpg', upload_to='profile_pics')
    nombre = models.CharField(
        verbose_name="Nombre o Razon social(empresas)",
        max_length=100)
    ape_pat = models.CharField(
        verbose_name="Apellido paterno", max_length=100, blank=True, default="")
    ape_mat = models.CharField(
        verbose_name="Apellido materno", max_length=100, blank=True, default="")
    telefono = models.CharField(verbose_name="Numero teléfonico a 10 digitos", max_length=100)
    calle = models.CharField(verbose_name="Calle", max_length=100)
    num_ext = models.CharField(verbose_name="Numero exterior", max_length=100)
    num_int = models.CharField(verbose_name="Numero interior", max_length=100, default="", blank=True)
    colonia = models.CharField(verbose_name="Colonia", max_length=100)
    municipio = models.CharField(verbose_name="Municipio o alcadía", max_length=100,)
    cp = models.CharField(verbose_name="Código postal",max_length=100,)
    estado = models.CharField(verbose_name="Estado", choices=ESTADOS, max_length=40)
    calificacion = models.IntegerField(verbose_name="Calificación", default=5, null=False)
    viajes_realizados = models.IntegerField(verbose_name="Viajes realizados", default=0, null=False)
    licencia_mp = models.BooleanField(default=False, verbose_name="Permiso de transportación de matarial peligroso")
    licencia_conducir_mp_foto = models.ImageField(verbose_name="Foto de licencia de conducir material peligroso", upload_to='licencias_transportistas')
    licencia_conducir = models.CharField(verbose_name="Número de licencia de conducir", max_length=50, default="")
    licencia_conducir_foto = models.ImageField(verbose_name="Foto de licencia de conducir", upload_to='licencias_transportistas')
    fecha_vencimiento_licencia = models.DateTimeField(verbose_name="Fecha de vencimiento de la licencia de manejo")
    slug = models.SlugField(null=True, blank=True)

    def __str__(self):
        return f'{self.user.username}'

    def save(self, *args, **kwargs):
        if self.slug is None:
            self.slug = slugify(self.user.username)
        super(Transportista, self).save(*args, **kwargs)

    @property
    def is_empresa(self):
        return self.user.es_empresa == True

    @property
    def has_info(self):
        if self.telefono == "" and self.municipio == "":
            return False
        else:
            return True

    @property
    def has_unidades(self):
        try:
            unidades = Unidades.objects.filter(user=self.user.id)
            if unidades:
                return True
            else:
                return False
        except:
            return False
    
    @property
    def has_licencia_conducir(self):
        if self.licencia_conducir == "" and self.licencia_conducir_foto == "":
            return False
        else:
            return True

    @property
    def has_licencia_mp(self):
        if self.licencia_mp == "" and self.licencia_conducir_mp_foto == "":
            return False
        else:
            return True

class Contacto(models.Model):
    nombre = models.CharField(
        verbose_name="Nombre",
        max_length=100)
    ape_pat = models.CharField(
        verbose_name="Apellido paterno", max_length=100,
        default="",)
    ape_mat = models.CharField(
        verbose_name="Apellido materno", max_length=100,
        default="",)
    telefono = models.CharField(verbose_name="Numero teléfonico", max_length=50)
    email = models.EmailField(verbose_name="Correo electronico", max_length=254)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.nombre} contacto de {self.user.username} '

class DatosFiscales(models.Model):
    nombre = models.CharField(
        verbose_name="Nombre o Razon social(empresas)",
        max_length=100)
    ape_pat = models.CharField(
        verbose_name="Apellido paterno", max_length=100, blank=True, default="")
    ape_mat = models.CharField(
        verbose_name="Apellido materno", max_length=100,blank=True, default="")
    calle = models.CharField(verbose_name="Calle", max_length=100)
    num_ext = models.CharField(verbose_name="Numero exterior", max_length=100)
    num_int = models.CharField(verbose_name="Numero interior", max_length=100, blank=True)
    colonia = models.CharField(verbose_name="Colonia", max_length=100)
    municipio = models.CharField(verbose_name="Municipio o alcadía", max_length=100)
    cp = models.CharField(verbose_name="Código postal",max_length=100,)
    estado = models.CharField(verbose_name="Estado", choices=ESTADOS, max_length=40)
    telefono = models.CharField(verbose_name="Numero teléfonico", max_length=30)
    rfc = models.CharField(max_length=30)
    es_empresa = models.BooleanField(
        verbose_name="Persona moral",
        default=False,
        help_text="Las empresas son personas morales")
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE, primary_key=True)

    class Meta:
        verbose_name_plural = "Datos fiscales"

    @property
    def has_rfc(self):
        if self.rfc == "":
            return False
        else:
            return True

    def __str__(self):
        return f'{self.rfc} de {self.user.username}'

class Encierro(models.Model):
    nombre = models.CharField(verbose_name="Nombre para identificar el encierro", max_length=50)
    calle = models.CharField(verbose_name="Calle", max_length=100)
    num_ext = models.CharField(verbose_name="Numero exterior", max_length=100)
    num_int = models.CharField(verbose_name="Numero interior", max_length=100, default="", blank=True)
    colonia = models.CharField(verbose_name="Colonia", max_length=100)
    municipio = models.CharField(verbose_name="Municipio o alcadía", max_length=100)
    cp = models.CharField(verbose_name="Código postal",max_length=100,)
    estado = models.CharField(verbose_name="Estado", choices=ESTADOS, max_length=40)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.nombre}'

YEAR_CHOICES = [(r,r) for r in range(1950, datetime.date.today().year+1)]
class Unidades(models.Model):
    marca = models.CharField(verbose_name="Marca", max_length=50)
    modelo = models.CharField(verbose_name="Modelo", max_length=50)
    año = models.IntegerField(verbose_name="Año", choices=YEAR_CHOICES, default=datetime.datetime.now().year)
    tipo_caja = models.CharField(verbose_name="Tipo de caja", max_length=50)
    capacidad_carga = models.FloatField(verbose_name="Capacidad de carga(toneladas)")
    placa = models.CharField(verbose_name="Placa", max_length=50, default="")
    tarjeta_circulacion = models.CharField(verbose_name="Tarjeta de circulación", max_length=50, default="")
    tarjeta_circulacion_foto = models.ImageField(verbose_name="Foto de tarjeta de circulación", upload_to='tarjetas_circulacion')
    foto1 = models.ImageField(verbose_name="Foto 1 de unidad", upload_to='unidades_pics')
    foto2 = models.ImageField(verbose_name="Foto 2 de unidad", upload_to='unidades_pics', null=True, blank=True)
    encierro = models.ForeignKey(Encierro, on_delete=models.CASCADE,)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Unidades"

    def __str__(self):
        return f'{self.placa}'




#SIGNALS

@receiver(post_save, sender=Cliente)
def createConketaId(sender,instance,**kwargs):
    cliente = instance

    if (cliente.conektaId is None or cliente.conektaId == "") and cliente.nombre != "":
        try:
            c = HTTPSConnection("www.google.com")
            api_key = bytes(settings.SANDBOX_PRIVADA_CONEKTA, encoding='utf-8')
            userAndPass = b64encode(api_key).decode("ascii")
            headers = { 'Authorization' : 'Basic %s' %  userAndPass }
            c.request('GET', '/', headers=headers)
            res = c.getresponse()
            data = res.read()
            url = "https://api.conekta.io/customers"
            user = {"name": f'{cliente.nombre} {cliente.ape_pat}', "email":cliente.user.email}
            headers = {
                "Accept": "application/vnd.conekta-v2.0.0+json",
                "Content-Type": "application/json",
                'Accept-Charset': 'UTF-8',
                'Authorization' : 'Basic %s' %  userAndPass,
            }
            response = requests.request("POST", url, json=user, headers=headers)
            if response.status_code == 200:
                response = response.json()
                idConekta = response["id"]
                Cliente.objects.filter(user=instance.user).update(
                    conektaId = idConekta
                )       
            else:
                cliente.conektaId = 'Data incorrecta'
        except conekta.ConektaError as e:
            print(e.message)

@receiver(user_logged_in)
def user_logged_in_callback(sender, request, user, **kwargs):  
    ip = request.META.get('REMOTE_ADDR')
    AuditEntry.objects.create(action='user_logged_in', ip=ip, username=user.username)


@receiver(user_logged_out)
def user_logged_out_callback(sender, request, user, **kwargs):  
    ip = request.META.get('REMOTE_ADDR')
    AuditEntry.objects.create(action='user_logged_out', ip=ip, username=user.username)


@receiver(user_login_failed)
def user_login_failed_callback(sender, credentials, **kwargs):
    AuditEntry.objects.create(action='user_login_failed', username=credentials.get('username', None))
