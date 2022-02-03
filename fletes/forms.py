from django import forms
from .models import Solicitud, Destino, Domicilios, Cotizacion

class TimeInput(forms.TimeInput):
    input_type = "time"

class SolicitudForm(forms.ModelForm):
    descripcion_servicio = forms.CharField(widget=forms.Textarea(attrs={"rows":2, "cols":20}))
    caracteristicas_carga = forms.CharField(widget=forms.Textarea(attrs={"rows":2, "cols":20}), label="Tipo de carga",)
    tiempo_carga = forms.IntegerField(
        label="Tiempo de espera",
        help_text='Tiempo máximo de espera para la carga',
    )
    material_peligroso = forms.ChoiceField(choices=((True, 'Si'), (False, 'No')),
                               widget=forms.RadioSelect)
    unidades_totales = forms.IntegerField(
        label="Unidades totales",
    )
    fecha_servicio = forms.DateField(
        widget=forms.DateInput(format = '%Y-%m-%d',attrs={'type': 'date'}),
    )
    class Meta:
        model = Solicitud
        exclude = ('cliente_id','modificado','estado_solicitud','motivo_cancelacion','activo','slug')
        widgets = {
            'hora': TimeInput(),
        }
    
    field_order = ['fecha_servicio','hora','tiempo_carga']

class SolicitudMotivoCancelacioForm(forms.ModelForm):
    class Meta:
        model = Solicitud
        fields = ['motivo_cancelacion',]
        labels = {
            'motivo_cancelacion':'Motivo de la cancelación'
        }
        widgets = {
            'motivo_cancelacion': forms.TextInput(
                attrs = {
                    'class':'form-control',
                    'placeholder':'Inregese el motivo de cancelación'
                } 
            )
        }

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
    referencias = forms.CharField(widget=forms.Textarea(attrs={"rows":2, "cols":20}))
    class Meta:
        model = Domicilios
        exclude = ('cliente_id','modificado','slug','longitud','latitud','is_valid','google_format','google_place_id')

class CotizacionForm(forms.ModelForm):
    class Meta:
        model = Cotizacion
        exclude = ('transportista_id','modificado','solicitud_id','slug','estado_cotizacion','motivo_cancelacion','activo','es_asegurada','nivel_seguro','checkoutUrl')

class CotizacionMotivoCancelacioForm(forms.ModelForm):
    class Meta:
        model = Cotizacion
        fields = ['motivo_cancelacion',]
        labels = {
            'motivo_cancelacion':'Motivo de la cancelación'
        }
        widgets = {
            'motivo_cancelacion': forms.TextInput(
                attrs = {
                    'class':'form-control',
                    'placeholder':'Inregese el motivo de cancelación'
                } 
            )
        }

class AgregarSeguroForm(forms.ModelForm):
    es_asegurada = forms.ChoiceField(choices=((True, 'Si'), (False, 'No')),
                               widget=forms.RadioSelect,
                               label="¿Desea asegurar su viaje?",)
    class Meta:
        model = Cotizacion
        fields = ['nivel_seguro','es_asegurada']
        labels = {
            'nivel_seguro':'Nivel de seguro',
            'es_asegurada':'¿Desea asegurar su viaje?',
        }
    
    field_order = ['es_asegurada','nivel_seguro']