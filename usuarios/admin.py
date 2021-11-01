from django.contrib import admin
from .models import MyUser, Cliente, Transportista, Contacto, DatosFiscales

admin.site.register(MyUser)
admin.site.register(Cliente)
admin.site.register(Transportista)
admin.site.register(Contacto)
admin.site.register(DatosFiscales)