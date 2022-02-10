from django.contrib import admin
from .models import Solicitud, Destino, Domicilios, Cotizacion, Seguro, Viaje

admin.site.register(Solicitud)
admin.site.register(Destino)
admin.site.register(Domicilios)
admin.site.register(Cotizacion)
admin.site.register(Seguro)
admin.site.register(Viaje)
