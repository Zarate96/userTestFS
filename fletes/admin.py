from django.conf import settings
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from rangefilter.filters import DateRangeFilter, DateTimeRangeFilter
from .models import Solicitud, Destino, Domicilios, Cotizacion, Seguro, Viaje, Orden

# REGISTRO DE IMPORTACIONES
class FletesResource(resources.ModelResource):
    class meta:
        model=(Solicitud,Viaje,Orden,Cotizacion)

@admin.register(Domicilios)
class DomiciliosAdmin(admin.ModelAdmin):
    #readonly_fields = ('created', 'updated')
    list_display = ('google_format','cliente_id')
    search_fields = ('cliente_id__user__username',)

@admin.register(Destino)
class DestinoAdmin(admin.ModelAdmin):
    #readonly_fields = ('created', 'updated')
    list_display = ('__str__',)
    search_fields = ('solicitud_id__folio',)

@admin.register(Solicitud)
class SolicitudAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    resouce_class = FletesResource
    list_display = ('__str__','estado_solicitud','admin_fecha_servicio','get_cliente','get_destinos')
    search_fields = ('cliente_id__user__username',)
    list_filter = (
        ('fecha_servicio', DateRangeFilter), 'estado_solicitud',
    )

    @admin.display(description='Cliente')
    def get_cliente(self, obj):
        site = settings.SITE_URL
        urlf = f'{site}/admin/usuarios/cliente/{obj.cliente_id.pk}/change/'
        return mark_safe(u' <a href="%s">%s</a>, ' % (urlf, obj.cliente_id))
            

    @admin.display(description='Fecha servicio')
    def admin_fecha_servicio(self, obj):
        return obj.fecha_servicio.strftime('%d-%m-%Y')

    def get_destinos(self, obj):
        site = settings.SITE_URL
        destinos = Destino.objects.filter(solicitud_id=obj.pk)
        finalStr = ""
        for destino in destinos:
            urlf = f'{site}/admin/fletes/destino/{destino.id}/change/'
            final = mark_safe(
            u' <a href="%s">%s</a>, ' % (urlf, destino.domicilio_id)
            )
            finalStr += final
        return mark_safe(finalStr)
    
    get_destinos.short_description = "Destinos"
    get_destinos.allow_tags = True

@admin.register(Cotizacion)
class CotizacionAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    resouce_class = FletesResource
    list_display = ('__str__','estado_cotizacion','get_transportista')
    search_fields = ('cliente_id__user__username',)
    list_filter = (
        'estado_cotizacion',
    )

    @admin.display(description='Transpotista')
    def get_transportista(self, obj):
        site = settings.SITE_URL
        urlf = f'{site}/admin/usuarios/transportista/{obj.transportista_id.pk}/change/'
        return mark_safe(u' <a href="%s">%s</a>' % (urlf, obj.transportista_id))
            


@admin.register(Viaje)
class ViajeAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    resouce_class = FletesResource
    list_display = ('folio','estado_viaje','get_cliente','get_transportista','get_solicitud','get_cotizacion','get_total_cotizacion','get_seguro_cotizacion','get_fecha_servicio')
    list_filter = (
        ('fecha_servicio', DateRangeFilter), 'estado_viaje',
    )
    search_fields = ('orden_id__cotizacion_id__folio','orden_id__cotizacion_id__solicitud_id__folio','folio')

    def get_solicitud(self,obj):
        solicitud = obj.orden_id.cotizacion_id.solicitud_id
        site = settings.SITE_URL
        urlf = f'{site}/admin/fletes/solicitud/{solicitud.pk}/change/'
        return mark_safe(
            u' <a href="%s">%s</a> ' % (urlf, solicitud.folio)
        )
    
    def get_cotizacion(self,obj):
        cotizacion = obj.orden_id.cotizacion_id
        site = settings.SITE_URL
        urlf = f'{site}/admin/fletes/cotizacion/{cotizacion.pk}/change/'
        return mark_safe(
            u' <a href="%s">%s</a> ' % (urlf, cotizacion.folio)
        )
    
    def get_total_cotizacion(self,obj):
        return f'$ {obj.orden_id.cotizacion_id.total}'

    def get_seguro_cotizacion(self,obj):
        cotizacion = obj.orden_id.cotizacion_id
        if cotizacion.es_asegurada:
            return f'{cotizacion.nivel_seguro}'
        else:
            return None

    @admin.display(description='Fecha servcio')
    def get_fecha_servicio(self,obj):
        return obj.fecha_servicio.strftime('%d-%m-%Y')

    def get_cliente(self,obj):
        return obj.orden_id.cotizacion_id.solicitud_id.cliente_id

    def get_transportista(self,obj):
        return obj.orden_id.cotizacion_id.transportista_id

    get_cliente.short_description = "Cliente"
    get_solicitud.short_description = "Solicitud"
    get_cotizacion.short_description = "Cotizacion"
    get_total_cotizacion.short_description = "Total"
    get_seguro_cotizacion.short_description = "Seguro"
    get_transportista.short_description = "Transportista"

admin.site.register(Seguro)
admin.site.register(Orden)