from django.contrib import admin
from .models import MyUser, Cliente, Transportista, Contacto, DatosFiscales, Unidades, Encierro, Telefonias

admin.site.register(MyUser)
admin.site.register(Cliente)
admin.site.register(Transportista)
admin.site.register(Contacto)
admin.site.register(DatosFiscales)
admin.site.register(Unidades)
admin.site.register(Encierro)
admin.site.register(Telefonias)