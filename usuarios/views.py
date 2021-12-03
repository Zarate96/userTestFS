import json
import threading

import urllib.request
from django.conf import settings
from django.core.mail import EmailMessage
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import views as auth_views, login
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str, force_text, DjangoUnicodeDecodeError
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied

from .utils import generate_token
from .models import MyUser, Cliente, Transportista, Contacto, DatosFiscales, Unidades, Encierro
from .forms import (
    ClienteSignUpForm, 
    TransportistaSignUpForm, 
    ProfileTransportistaUpdateForm,
    ProfileClienteUpdateForm,
    ContactoForm,
    DatosFiscalesUpdateForm,
    UnidadesForm,
    EncierroForm,)

class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()

def send_activation_email(user, request):
    current_site = get_current_site(request)
    email_subject = 'Activa tu cuenta'
    email_body = render_to_string('usuarios/active.html', {
        'user': user,
        'domain': current_site,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': generate_token.make_token(user)
    })

    email = EmailMessage(subject=email_subject, body=email_body,
                         from_email=settings.EMAIL_FROM_USER,
                         to=[user.email]
                         )

    if not settings.TESTING:
        EmailThread(email).start()

def activate_user(request, uidb64, token):

    try:
        uid = force_text(urlsafe_base64_decode(uidb64))

        user = MyUser.objects.get(pk=uid)

    except Exception as e:
        user = None

    if user and generate_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.add_message(request, messages.SUCCESS,
                             'Email verificado, ya puede iniciar sesion')
        return redirect(reverse('login'))

    return render(request, 'usuarios/activate_failed.html', {"user": user})

def home(request):
    return render(request, 'home.html')

class LoginUserView(auth_views.LoginView):
    template_name = "usuarios/login.html"
    def get_success_url(self):
        url = self.get_redirect_url()
        if self.request.user and not self.request.user.is_active:
            messages.add_message(request, messages.ERROR,
                                 'Correo no verificado porfavor revisa tu bandeja de entrada')
            return render(self.request, 'usuarios/login.html', status=401)
        if url:
            return url
        elif self.request.user.is_superuser:
            return reverse("admin")
        else:
            messages.success(self.request, f'Acceso correcto')
            return reverse("home")

class ClienteSignUpView(CreateView):
    model = MyUser
    template_name = 'registration/signup_form.html'
    form_class = ClienteSignUpForm

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        if 'cliente' in self.request.path:
            kwargs['user_type'] = 'cliente'
        else: 
            kwargs['user_type'] = 'transportista'

        kwargs['recaptcha_site_key'] = settings.GOOGLE_RECAPTCHA_SITE_KEY
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        recaptcha_response = self.request.POST.get('g-recaptcha-response')
        url = 'https://www.google.com/recaptcha/api/siteverify'
        values = {
            'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
        }
        data = urllib.parse.urlencode(values).encode()
        req =  urllib.request.Request(url, data=data)
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode())
        
        if result['success']:
            user = form.save()
            user.is_active = False
            user.save()
            send_activation_email(user, self.request)
            messages.add_message(self.request, messages.SUCCESS,
                                 'Hemos enviado un mensaje para verificar tu cuenta')
            return redirect('login')
        
        else:
            messages.success(self.request, f'Recaptcha no válido o no seleccionado')
            return redirect('home')

class TransportistaSignUpView(CreateView):
    model = MyUser
    template_name = 'registration/signup_form.html'
    form_class = TransportistaSignUpForm

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        if 'cliente' in self.request.path:
            kwargs['user_type'] = 'cliente'
        else: 
            kwargs['user_type'] = 'transportista'

        kwargs['recaptcha_site_key'] = settings.GOOGLE_RECAPTCHA_SITE_KEY
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        recaptcha_response = self.request.POST.get('g-recaptcha-response')
        url = 'https://www.google.com/recaptcha/api/siteverify'
        values = {
            'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
        }
        data = urllib.parse.urlencode(values).encode()
        req =  urllib.request.Request(url, data=data)
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode())
        
        if result['success']:
            user = form.save()
            user.is_active = False
            user.save()
            send_activation_email(user, self.request)
            messages.add_message(self.request, messages.SUCCESS,
                                 'Hemos enviado un mensaje para verificar tu cuenta')
            return redirect('login')
        
        else:
            messages.success(self.request, f'Recaptcha no válido o no seleccionado')
            return redirect('home')

class ProfileView(DetailView):
    model = MyUser
    template_name = 'usuarios/perfil.html'

    def get_object(self):
        return get_object_or_404(MyUser, pk=self.request.user.id)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        current_user = self.request.user
        contactos = Contacto.objects.filter(user=current_user.id)
        unidades = Unidades.objects.filter(user=current_user.id)

        context['contactos'] = contactos
        context['unidades'] = unidades
        return context

class ProfileTransportista(DeleteView):
    model = Transportista
    template_name = 'usuarios/perfilTransportista.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        transportista = self.get_object()
        context['transportista'] = transportista
        return context

class ProfileClienteUpdateView(UserPassesTestMixin, UpdateView):
    model = Cliente
    template_name = 'usuarios/updatePerfil.html'
    fields = ['nombre','ape_pat','ape_mat','telefono','calle','num_ext','num_int','colonia','municipio','cp','estado','image']

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        user = context['object']
        context['title'] = "Actualizar perfil"
        context['subtitle'] = "Datos personales"
        context['form'] = ProfileClienteUpdateForm(instance=user, profile=user)
        return context
    
    def test_func(self):
        user = self.get_object()
        if self.request.user.is_transportista:
            return False
        elif self.request.user.cliente == user:
            return True
        else:
            return False

    def get_success_url(self):
        messages.success(self.request, f'Perfil actualizado correctamente')
        return reverse('profile-user')

class ProfileTransportistaUpdate(UserPassesTestMixin, UpdateView):
    model = Transportista
    template_name = 'usuarios/updatePerfil.html'
    fields = ['nombre','ape_pat','ape_mat','telefono','calle','num_ext','num_int','colonia','municipio','cp','estado','image']

    def test_func(self):
        user = self.get_object()
        if self.request.user.is_cliente:
            return False
        elif self.request.user.transportista == user:
            return True
        else:
            return False

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        user = context['object']
        context['title'] = "Actualizar perfil"
        context['subtitle'] = "Datos personales"
        context['form'] = ProfileTransportistaUpdateForm(instance=user, profile=user)
        return context
    
    def get_success_url(self):
        messages.success(self.request, f'Perfil actualizado correctamente')
        return reverse('profile-user')

class ContactoAgregar(UserPassesTestMixin,CreateView):
    model = Contacto
    form_class = ContactoForm
    template_name = 'usuarios/contacto.html'

    def test_func(self):
        if self.request.user.id == self.kwargs['user_pk']:
            return True
        else:
            return False

    def form_valid(self, form):
        user = MyUser.objects.get(pk=self.kwargs['user_pk'])
        self.object = form.save(commit=False)
        self.object.user = user
        self.object.save()
        messages.success(self.request, f'Contacto agregado correctamente')
        return redirect(reverse('profile-user'))

    def get_success_url(self):
        return redirect(reverse('profile-user'))

class ContactoUpdate(UserPassesTestMixin, UpdateView):
    model = Contacto
    template_name = 'usuarios/contacto.html'
    form_class = ContactoForm

    def test_func(self):
        contacto = self.get_object()
        if self.request.user == contacto.user:
            return True
        else:
            return False

    def get_success_url(self):
        return reverse_lazy('home')

@login_required
def ContactoDelete(request, pk):
    contacto = get_object_or_404(Contacto, id=pk)
    user = request.user
    if contacto.user == user:
        contacto.delete()
        return redirect(reverse('profile-user'))
    else:
        raise PermissionDenied()

class DatosFiscalesUpdate(UserPassesTestMixin,UpdateView):
    model = DatosFiscales
    template_name = 'usuarios/updatePerfil.html'
    fields = ['nombre','ape_pat','ape_mat','telefono','calle','num_ext','num_int','colonia','municipio','cp','estado','rfc']

    def test_func(self):
        user = self.get_object().user
        if self.request.user == user:
            return True
        else:
            return False

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        user = context['object']
        context['title'] = "Actualizar información fiscal"
        context['subtitle'] = "Datos fiscales"
        context['form'] = DatosFiscalesUpdateForm(instance=user, profile=user.user)
        return context
    
    def get_success_url(self):
        #return reverse_lazy('home')
        messages.success(self.request, f'Información fiscal actualizada correctamente')
        return reverse('profile-user')

class UnidadesAgregar(UserPassesTestMixin, CreateView):
    model = Unidades
    form_class = UnidadesForm
    template_name = 'usuarios/unidades.html'

    def test_func(self):
        if self.request.user.id == self.kwargs['user_pk']:
            return True
        else:
            return False

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        id = self.request.user.id
        encierros = Encierro.objects.filter(user=id)
        context['encierros'] = encierros
        return context
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class=self.form_class)
        form.fields['encierro'].queryset = Encierro.objects.filter(user=self.request.user.id)
        return form

    def form_valid(self, form):
        user = MyUser.objects.get(pk=self.kwargs['user_pk'])
        self.object = form.save(commit=False)
        self.object.user = user
        self.object.save()
        messages.success(self.request, f'Unidad agregada correctamente')
        return redirect(reverse('profile-user'))

class UnidadesDetalle(DetailView):
    model = Unidades
    template_name = 'usuarios/unidadesDetalle.html'
    context_object_name = 'unidad'

@login_required
def UnidadDelete(request, pk):
    unidad = get_object_or_404(Unidades, id=pk)
    user = request.user
    if unidad.user == user:
        unidad.delete()
        return redirect(reverse('profile-user'))
    else:
        raise PermissionDenied()

class EncierroAgregar(UserPassesTestMixin, CreateView):
    model = Encierro
    form_class = EncierroForm
    template_name = 'usuarios/encierro.html'

    def test_func(self):
        if self.request.user.id == self.kwargs['user_pk']:
            return True
        else:
            return False

    def form_valid(self, form):
        user = MyUser.objects.get(pk=self.kwargs['user_pk'])
        self.object = form.save(commit=False)
        self.object.user = user
        self.object.save()
        messages.success(self.request, f'Encierro agregado correctamente')
        return redirect(reverse('agregar-unidad', kwargs={'user_pk': self.request.user.id}))

class EncierroUpdate(UserPassesTestMixin, UpdateView):
    model = Encierro
    template_name = 'usuarios/encierro.html'
    form_class = EncierroForm

    def test_func(self):
        encierro = self.get_object()
        if self.request.user == encierro.user:
            return True
        else:
            return False

    def get_success_url(self):
        return reverse_lazy('home')

@login_required
def EncierroDelete(request, pk):
    encierro = get_object_or_404(Encierro, id=pk)
    user = request.user
    if encierro.user == user:
        encierro.delete()
        return redirect(reverse('agregar-unidad', kwargs={'user_pk': request.user.id}))
    else:
        raise PermissionDenied()

#Manage errors
def handle_not_found(request, exception, template_name="404.html"):
    return render(template_name)