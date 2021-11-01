from django.db import models
from django.contrib.auth.models import AbstractUser

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

class MyUser(AbstractUser):
    email = models.EmailField(max_length=254)
    es_transportista = models.BooleanField(default=False)
    es_cliente = models.BooleanField(default=False)
    es_empresa = models.BooleanField(
        verbose_name="Persona moral",
        default=False,
        help_text="Las empresas son personas morales")

    class Meta:
        db_table = 'auth_user'
    
    @property
    def is_cliente(self):
        return self.es_cliente == True
    
    @property
    def is_empresa(self):
        return self.es_empresa == True
    
    @property
    def is_transportista(self):
        return self.es_transportista == True

class Cliente(models.Model):
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE, primary_key=True)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    nombre = models.CharField(
        verbose_name="Nombre o Razon social(empresas)",
        max_length=100)
    ape_pat = models.CharField(
        verbose_name="Apellido paterno", max_length=100, blank=True, default=" ")
    ape_mat = models.CharField(
        verbose_name="Apellido materno", max_length=100, blank=True, default=" ")
    telefono = models.CharField(verbose_name="Numero teléfonico a 10 digitos", max_length=100)
    calle = models.CharField(verbose_name="Calle", max_length=100)
    num_ext = models.CharField(verbose_name="Numero exterior", max_length=100)
    num_int = models.CharField(verbose_name="Numero interior", max_length=100, default="", blank=True)
    colonia = models.CharField(verbose_name="Colonia", max_length=100)
    municipio = models.CharField(verbose_name="Municipio o alcadía", max_length=100,)
    cp = models.CharField(verbose_name="Código postal",max_length=100,)
    estado = models.CharField(verbose_name="Estado", choices=ESTADOS, max_length=40)

    def __str__(self):
        return str(self.user.username)
    
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
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    nombre = models.CharField(
        verbose_name="Nombre o Razon social(empresas)",
        max_length=100)
    ape_pat = models.CharField(
        verbose_name="Apellido paterno", max_length=100, blank=True, default=" ")
    ape_mat = models.CharField(
        verbose_name="Apellido materno", max_length=100, blank=True, default=" ")
    telefono = models.CharField(verbose_name="Numero teléfonico a 10 digitos", max_length=100)
    calle = models.CharField(verbose_name="Calle", max_length=100)
    num_ext = models.CharField(verbose_name="Numero exterior", max_length=100)
    num_int = models.CharField(verbose_name="Numero interior", max_length=100, default="", blank=True)
    colonia = models.CharField(verbose_name="Colonia", max_length=100)
    municipio = models.CharField(verbose_name="Municipio o alcadía", max_length=100,)
    cp = models.CharField(verbose_name="Código postal",max_length=100,)
    estado = models.CharField(verbose_name="Estado", choices=ESTADOS, max_length=40)
    
    def __str__(self):
        return f'{self.user.username}'
    
    @property
    def is_empresa(self):
        return self.user.es_empresa == True
    
    @property 
    def has_info(self):
        if self.telefono == "" and self.municipio == "":
            return False
        else:
            return True

class Contacto(models.Model):
    nombre = models.CharField(
        verbose_name="Nombre",
        max_length=100)
    ape_pat = models.CharField(
        verbose_name="Apellido paterno", max_length=100,
        default=" ",)
    ape_mat = models.CharField(
        verbose_name="Apellido materno", max_length=100,
        default=" ",)
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
        verbose_name="Apellido paterno", max_length=100, blank=True, default=" ")
    ape_mat = models.CharField(
        verbose_name="Apellido materno", max_length=100,blank=True, default=" ")
    calle = models.CharField(verbose_name="Calle", max_length=100)
    num_ext = models.CharField(verbose_name="Numero exterior", max_length=100)
    num_int = models.CharField(verbose_name="Numero interior", max_length=100, default="", blank=True)
    colonia = models.CharField(verbose_name="Colonia", max_length=100)
    municipio = models.CharField(verbose_name="Municipio o alcadía", max_length=100, null=True)
    cp = models.CharField(verbose_name="Código postal",max_length=100,)
    estado = models.CharField(verbose_name="Estado", choices=ESTADOS, max_length=40)
    telefono = models.CharField(verbose_name="Numero teléfonico", max_length=30)
    rfc = models.CharField(max_length=30)
    es_empresa = models.BooleanField(
        verbose_name="Persona moral",
        default=False,
        help_text="Las empresas son personas morales")
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE, primary_key=True)

    @property
    def has_rfc(self):
        if self.rfc == "":
            return False
        else:
            return True

    def __str__(self):
        return f'{self.rfc} de {self.user.username} '