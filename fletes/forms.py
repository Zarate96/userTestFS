from django import forms
from .models import Solicitud, Destino, Domicilios, Cotizacion

class DateInput(forms.DateInput):
    input_type = 'date'
    
    def __init__(self, **kwargs):
        kwargs["format"] = "%d-%m-%Y"
        super().__init__(**kwargs)

class TimeInput(forms.TimeInput):
    input_type = "time"

class SolicitudForm(forms.ModelForm):
    descripcion_servicio = forms.CharField(widget=forms.Textarea(attrs={"rows":2, "cols":20}))
    caracteristicas_carga = forms.CharField(widget=forms.Textarea(attrs={"rows":2, "cols":20}), label="Tipo de carga",)
    tiempo_carga = forms.IntegerField(
        label="Tiempo de espera",
        help_text='Tiempo máximo de espera para la carga',
    )
    
    unidades_totales = forms.IntegerField(
        label="Unidades totales",
    )
    class Meta:
        model = Solicitud
        exclude = ('cliente_id','modificado','estado_solicitud',)
        widgets = {
            'fecha_servicio': DateInput(),
            'hora': TimeInput(),
        }
    
    field_order = ['fecha_servicio','hora','tiempo_carga']

class DestinoForm(forms.ModelForm):
    tiempo_descarga = forms.IntegerField(
        label="Tiempo de espera",
        help_text='Tiempo máximo de espera para la descarga',
    )
    unidades_entregar = forms.IntegerField(
        label="Unidades a entregar en este destino",
    )
    class Meta:
        model = Destino
        exclude = ('solicitud_id',)
    
    #field_order = ['fecha_servicio','hora','tiempo_carga']

class DomicilioForm(forms.ModelForm):
    colonia = forms.CharField(
        label="Colonia o alcadía",
    )
    class Meta:
        model = Domicilios
        exclude = ('cliente_id','modificado','slug')

class CotizacionForm(forms.ModelForm):
    class Meta:
        model = Cotizacion
        exclude = ('transportista_id','modificado','solicitud_id','slug','estado_cotizacion','activo',)