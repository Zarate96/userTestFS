from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.forms.utils import ValidationError

from .models import MyUser, Cliente, Transportista, Contacto, DatosFiscales, Unidades, Encierro, Verifaciones, Verifaciones_encierros

class ClienteSignUpForm(UserCreationForm):
    email = forms.EmailField()
    es_empresa = forms.BooleanField(label='Persona moral', label_suffix = " : ",
                                  required = False,  disabled = False,
                                  widget=forms.widgets.CheckboxInput(attrs={'class': 'checkbox-inline'}),
                                  help_text = "Seleccione si desea registrarse como empresa.")
    username = forms.CharField(
        label="Nombre de usuario",
        strip=False,
        help_text='Tu nombre de usuario puede con tener 150 carácteres o menos. Letras, digítos, y @/./+/-/_  solamente, no están permitidos los espacios',
    )
    password1 = forms.CharField(
        label="Contraseña",
        strip=False,
        widget=forms.PasswordInput,
        help_text='La contraseña debe contener mayúsculas, minúsculas y al menos un carácter.',
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        strip=False,
        widget=forms.PasswordInput,
    )
    class Meta:
        model = MyUser
        fields = ['username', 'email', 'password1', 'password2']
    
    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.es_cliente = True
        moral = self.cleaned_data.get('es_empresa')
        if moral:
            user.es_empresa = True
        user.save()
        if moral:
            df = DatosFiscales.objects.create(user=user,es_empresa=True)
        else:
            df = DatosFiscales.objects.create(user=user,es_empresa=False)
        cliente = Cliente.objects.create(user=user)
        return user

class TransportistaSignUpForm(UserCreationForm):
    email = forms.EmailField()
    es_empresa = forms.BooleanField(label='Persona moral', label_suffix = " : ",
                                  required = False,  disabled = False,
                                  widget=forms.widgets.CheckboxInput(attrs={'class': 'checkbox-inline'}),
                                  help_text = "Seleccione si desea registrarse como empresa.")
    username = forms.CharField(
        label="Nombre de usuario",
        strip=False,
        help_text='Tu nombre de usuario puede con tener 150 carácteres o menos. Letras, digítos, and @/./+/-/_  solamente',
    )
    password1 = forms.CharField(
        label="Contraseña",
        strip=False,
        widget=forms.PasswordInput,
        help_text='La contraseña debe contener mayúsculas, minúsculas y al menos un carácter.',
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        strip=False,
        widget=forms.PasswordInput,
    )
    class Meta:
        model = MyUser
        fields = ['username', 'email', 'password1', 'password2']
    
    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.es_transportista = True
        moral = self.cleaned_data.get('es_empresa')
        if moral:
            user.es_empresa = True
        user.save()
        if moral:
            df = DatosFiscales.objects.create(user=user,es_empresa=True)
        else:
            df = DatosFiscales.objects.create(user=user,es_empresa=False)
        
        transportista = Transportista.objects.create(user=user)
        return user

class ProfileTransportistaUpdateForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):

        profile = kwargs.pop('profile',None)
        super(ProfileTransportistaUpdateForm, self).__init__(*args,**kwargs)
        
        if profile.is_empresa:
            self.fields['nombre'].label='Razón social'
            self.fields['ape_mat'].widget = forms.HiddenInput()
            self.fields['ape_pat'].widget = forms.HiddenInput()
        else:
            self.fields['nombre'].label='Nombre'
            self.fields['ape_pat'].required = True
            self.fields['ape_mat'].required = True

    class Meta:
        model = Transportista
        fields = ['nombre','ape_pat','ape_mat','telefono','calle','num_ext','num_int','colonia','municipio','cp','estado','image']

class AgregarVerificacionForm(forms.ModelForm):
    fecha_visita = forms.DateField(
        #widget=forms.DateTimeInput(format = '%Y-%m-%d %H:%M',attrs={'type': 'datetime-local'}),
        widget=forms.DateInput(format = '%Y-%m-%d',attrs={'type': 'date'}),
    )

    class Meta:
        model = Verifaciones
        fields = ['verificador','fecha_visita']

class AgregarVerificacionEncierroForm(forms.ModelForm):
    fecha_visita = forms.DateField(
        #widget=forms.DateTimeInput(format = '%Y-%m-%d %H:%M',attrs={'type': 'datetime-local'}),
        widget=forms.DateInput(format = '%Y-%m-%d',attrs={'type': 'date'}),
    )

    class Meta:
        model = Verifaciones_encierros
        fields = ['verificador','fecha_visita']

class AgregarLincenciaConducirForm(forms.ModelForm):
    fecha_vencimiento_licencia = forms.DateField(
        widget=forms.DateInput(format = '%Y-%m-%d',attrs={'type': 'date'}),
    )

    class Meta:
        model = Transportista
        fields = ['licencia_conducir','fecha_vencimiento_licencia','licencia_conducir_foto']

class AgregarLincenciaMpForm(forms.ModelForm):
    class Meta:
        model = Transportista
        fields = ['licencia_conducir_mp_foto',]

class ProfileClienteUpdateForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):

        profile = kwargs.pop('profile',None)
        super(ProfileClienteUpdateForm, self).__init__(*args,**kwargs)
        
        if profile.is_empresa:
            self.fields['nombre'].label='Razón social'
            self.fields['ape_mat'].widget = forms.HiddenInput()
            self.fields['ape_pat'].widget = forms.HiddenInput()
        else:
            self.fields['nombre'].label='Nombre'
            self.fields['ape_pat'].required = True
            self.fields['ape_mat'].required = True

    class Meta:
        model = Cliente
        fields = ['nombre','ape_pat','ape_mat','telefono','calle','num_ext','num_int','colonia','municipio','cp','estado','image']

class ContactoForm(forms.ModelForm):
    class Meta:
        model = Contacto
        exclude = ('user',)

class DatosFiscalesUpdateForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):

        profile = kwargs.pop('profile',None)
        super(DatosFiscalesUpdateForm, self).__init__(*args,**kwargs)
        
        if profile.is_empresa:
            self.fields['nombre'].label='Razón social'
            self.fields['ape_mat'].widget = forms.HiddenInput()
            self.fields['ape_pat'].widget = forms.HiddenInput()
        else:
            self.fields['nombre'].label='Nombre'
            self.fields['ape_pat'].required = True
            self.fields['ape_mat'].required = True

    class Meta:
        model = DatosFiscales
        fields = ['nombre','ape_pat','ape_mat','telefono','calle','num_ext','num_int','colonia','municipio','cp','estado','rfc']

class UnidadesForm(forms.ModelForm):
    class Meta:
        model = Unidades
        exclude = ('user','verificador_foto_unidad','verificado','tarjeta_circulacion_verificador_foto')
    
    field_order = ['encierro']

class EncierroForm(forms.ModelForm):
    class Meta:
        model = Encierro
        exclude = ('user','verificador_foto_encierro','verificado','es_validado','es_verificado','es_activo','slug')


#FORMULARIOS VERIFICADORES
class verificarLicenciaConducirForm(forms.ModelForm):
    class Meta:
        model = Transportista
        fields = ['licencia_conducir_verificador_foto',]
        labels = {
            'licencia_conducir_verificador_foto':'Foto de licencia de conducir de transportista'
        }

class verificarLicenciaMpForm(forms.ModelForm):
    class Meta:
        model = Transportista
        fields = ['licencia_conducir_mp_verificador_foto',]
        labels = {
            'licencia_conducir_mp_verificador_foto':'Foto de permiso para transportar metrial peligroso'
        }

class verificarUnidadForm(forms.ModelForm):
    class Meta:
        model = Unidades
        fields = ['verificador_foto_unidad','tarjeta_circulacion_verificador_foto',]
        labels = {
            'verificador_foto_unidad':'Foto de unidad',
            'tarjeta_circulacion_verificador_foto':'Foto de tarjeta de circulación'
        }

class verificarEncierroForm(forms.ModelForm):
    class Meta:
        model = Encierro
        fields = ['verificador_foto_encierro',]
        labels = {
            'verificador_foto_encierro':'Foto de encierro'
        }

class verificarDatosFiscalesForm(forms.ModelForm):
    class Meta:
        model = DatosFiscales
        fields = ['verificador_foto',]
        labels = {
            'verificador_foto':'Foto de dirección fiscal'
        }