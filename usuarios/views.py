import json
import threading

import urllib.request
from django.conf import settings
from django.core.mail import EmailMessage
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import views as auth_views, login
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str, force_text, DjangoUnicodeDecodeError

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

class ProfileCliente(DetailView):
    model = MyUser
    template_name = 'usuarios/perfil.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        user = context['object']
        id = user.id
        contactos = Contacto.objects.filter(user=id)
        unidades = Unidades.objects.filter(user=id)

        context['contactos'] = contactos
        context['unidades'] = unidades
        return context

class ProfileClienteUpdate(UpdateView):
    model = Cliente
    template_name = 'usuarios/updatePerfil.html'
    fields = ['nombre','ape_pat','ape_mat','telefono','calle','num_ext','num_int','colonia','municipio','cp','estado','image']
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        user = context['object']
        perfil = context['cliente']
        context['title'] = "Actualizar perfil"
        context['subtitle'] = "Datos personales"
        context['form'] = ProfileClienteUpdateForm(instance=user, profile=perfil)
        return context

    def get_success_url(self):
        messages.success(self.request, f'Perfil actualizado correctamente')
        return reverse('profile-cliente', kwargs={'pk': self.request.user.pk})

class ProfileTransportistaUpdate(UpdateView):
    model = Transportista
    template_name = 'usuarios/updatePerfil.html'
    fields = ['nombre','ape_pat','ape_mat','telefono','calle','num_ext','num_int','colonia','municipio','cp','estado','image']

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        print(context)
        user = context['object']
        perfil = context['transportista']
        context['title'] = "Actualizar perfil"
        context['subtitle'] = "Datos personales"
        context['form'] = ProfileTransportistaUpdateForm(instance=user, profile=perfil)
        return context
    
    def get_success_url(self):
        messages.success(self.request, f'Perfil actualizado correctamente')
        return reverse('profile-cliente', kwargs={'pk': self.request.user.pk})

class ContactoAgregar(CreateView):
    model = Contacto
    form_class = ContactoForm
    template_name = 'usuarios/contacto.html'

    def form_valid(self, form):
        user = MyUser.objects.get(pk=self.kwargs['user_pk'])
        self.object = form.save(commit=False)
        self.object.user = user
        self.object.save()
        messages.success(self.request, f'Contacto agregado correctamente')
        return redirect(reverse('profile-cliente', kwargs={'pk': self.request.user.id}))

    def get_success_url(self):
        return redirect(reverse('profile-cliente', kwargs={'pk': self.request.user.id}))

class ContactoUpdate(UpdateView):
    model = Contacto
    template_name = 'usuarios/contacto.html'
    form_class = ContactoForm

    def get_success_url(self):
        return reverse_lazy('home')

def ContactoDelete(request, pk):
    contacto = Contacto.objects.get(id=pk)
    contacto.delete()
    return redirect(reverse('profile-cliente', kwargs={'pk': request.user.id}))

class DatosFiscalesUpdate(UpdateView):
    model = DatosFiscales
    template_name = 'usuarios/updatePerfil.html'
    fields = ['nombre','ape_pat','ape_mat','telefono','calle','num_ext','num_int','colonia','municipio','cp','estado','rfc']

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
        return reverse('profile-cliente', kwargs={'pk': self.request.user.pk})

class UnidadesAgregar(CreateView):
    model = Unidades
    form_class = UnidadesForm
    template_name = 'usuarios/unidades.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        id = self.request.user.id
        encierros = Encierro.objects.filter(user=id)
        context['encierros'] = encierros
        return context

    def form_valid(self, form):
        user = MyUser.objects.get(pk=self.kwargs['pk'])
        self.object = form.save(commit=False)
        self.object.user = user
        self.object.save()
        messages.success(self.request, f'Unidad agregada correctamente')
        return redirect(reverse('profile-cliente', kwargs={'pk': self.request.user.id}))

class EncierroAgregar(CreateView):
    model = Encierro
    form_class = EncierroForm
    template_name = 'usuarios/encierro.html'

    def form_valid(self, form):
        user = MyUser.objects.get(pk=self.kwargs['user_pk'])
        self.object = form.save(commit=False)
        self.object.user = user
        self.object.save()
        messages.success(self.request, f'Encierro agregado correctamente')
        return redirect(reverse('agregar-unidad', kwargs={'pk': self.request.user.id}))

class EncierroUpdate(UpdateView):
    model = Encierro
    template_name = 'usuarios/encierro.html'
    form_class = EncierroForm

    def get_success_url(self):
        return reverse_lazy('home')

def EncierroDelete(request, pk):
    encierro = Encierro.objects.get(id=pk)
    encierro.delete()
    return redirect(reverse('agregar-unidad', kwargs={'pk': request.user.id}))