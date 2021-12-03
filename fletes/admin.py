from django.contrib import admin
from .models import Solicitud, Destino, Domicilios, Cotizacion

admin.site.register(Solicitud)
admin.site.register(Destino)
admin.site.register(Domicilios)
admin.site.register(Cotizacion)
