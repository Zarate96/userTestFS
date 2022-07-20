from django.conf import settings
from django.contrib import admin
from django.utils.html import mark_safe 
from django.contrib.admin.models import LogEntry
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from rangefilter.filters import DateRangeFilter, DateTimeRangeFilter
from .models import MyUser, Cliente, Transportista, Contacto, DatosFiscales, Unidades, Encierro, AuditEntry, Verificador, Verifaciones, Verifaciones_encierros
from fletes.models import Domicilios
admin.site.register(MyUser)

# REGISTRO DE IMPORTACIONES
class UsuariosResource(resources.ModelResource):
    class meta:
        model=(Cliente,Transportista,MyUser,AuditEntry)

@admin.register(Cliente)
class ClienteAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    resouce_class = UsuariosResource
    list_display = ('user','get_perfil_fiscal','get_contactos','get_domicilios')
    search_fields = ('user__username',)
    list_filter = ('estado',)

    def get_perfil_fiscal(self, obj):
        site = settings.SITE_URL
        perfil_fiscal = DatosFiscales.objects.get(user=obj.user.pk)
        urlf = f'{site}/admin/usuarios/datosfiscales/{perfil_fiscal.pk}/change/'
        return mark_safe(
            u' <a href="%s">%s</a>, ' % (urlf, f'{perfil_fiscal.rfc}')
        )
    
    def get_contactos(self, obj):
        site = settings.SITE_URL
        
        contactos = Contacto.objects.filter(user=obj.user.pk)
        finalStr = ""
        for contacto in contactos:
            urlf = f'{site}/admin/usuarios/contacto/{contacto.id}/change/'
            final = mark_safe(
            u' <a href="%s">%s</a>, ' % (urlf, f'{contacto.nombre} {contacto.ape_pat}')
            )
            finalStr += final
        return mark_safe(finalStr)

    def get_domicilios(self, obj):
        site = settings.SITE_URL
        domicilios = Domicilios.objects.filter(cliente_id=obj.user.pk)
        finalStr = ""
        for domicilio in domicilios:
            urlf = f'{site}/admin/fletes/domicilios/{domicilio.id}/change/'
            final = mark_safe(
            u' <a href="%s">%s</a>, ' % (urlf, f'{domicilio.nombre}')
            )
            finalStr += final
        return mark_safe(finalStr)

    get_perfil_fiscal.short_description = "Perfil fiscal"
    get_domicilios.short_description = "Domicilios"
    get_contactos.short_description = "Contactos"

@admin.register(Transportista)
class TransportistaAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    resouce_class = UsuariosResource
    list_display = ('user','get_perfil_fiscal','get_contactos','get_encierros','get_unidades')
    search_fields = ('user__username',)
    list_filter = ('estado',)

    def get_perfil_fiscal(self, obj):
        site = settings.SITE_URL
        perfil_fiscal = DatosFiscales.objects.get(user=obj.user.pk)
        urlf = f'{site}/admin/usuarios/datosfiscales/{perfil_fiscal.pk}/change/'
        return mark_safe(
            u' <a href="%s">%s</a>, ' % (urlf, f'{perfil_fiscal.rfc}')
        )

    def get_contactos(self, obj):
        site = settings.SITE_URL
        
        contactos = Contacto.objects.filter(user=obj.user.pk)
        finalStr = ""
        for contacto in contactos:
            urlf = f'{site}/admin/usuarios/contacto/{contacto.id}/change/'
            final = mark_safe(
            u' <a href="%s">%s</a>, ' % (urlf, f'{contacto.nombre} {contacto.ape_pat}')
            )
            finalStr += final
        return mark_safe(finalStr)
    
    def get_encierros(self, obj):
        site = settings.SITE_URL
        
        encierros = Encierro.objects.filter(user=obj.user.pk)
        finalStr = ""
        for encierro in encierros:
            urlf = f'{site}/admin/usuarios/encierro/{encierro.id}/change/'
            final = mark_safe(
            u' <a href="%s">%s</a>, ' % (urlf, f'{encierro.nombre}')
            )
            finalStr += final
        return mark_safe(finalStr)
    
    def get_unidades(self, obj):
        site = settings.SITE_URL
        
        unidades = Unidades.objects.filter(user=obj.user.pk)
        finalStr = ""
        for unidad in unidades:
            urlf = f'{site}/admin/usuarios/unidades/{unidad.id}/change/'
            final = mark_safe(
            u' <a href="%s">%s</a>, ' % (urlf, f'{unidad.placa}')
            )
            finalStr += final
        return mark_safe(finalStr)


    get_perfil_fiscal.short_description = "Perfil fiscal"
    get_unidades.short_description = "Unidades"
    get_encierros.short_description = "Encierros"
    get_contactos.short_description = "Contactos"

@admin.register(Contacto)
class ContactoAdmin(admin.ModelAdmin):
    list_display = ('nombre','ape_pat','telefono','email','user')
    search_fields = ('user__username',)

@admin.register(Encierro)
class EncierroAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(AuditEntry)
class AuditEntryAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    resouce_class = UsuariosResource
    search_fields = ('username',)
    list_filter = (
        ('created_at', DateRangeFilter),
    )
    list_display = ('action','ip','username','created_at')

admin.site.register(DatosFiscales)
admin.site.register(Unidades)
admin.site.register(Verificador)
admin.site.register(Verifaciones)
admin.site.register(Verifaciones_encierros)