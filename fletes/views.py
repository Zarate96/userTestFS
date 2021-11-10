from django.shortcuts import render
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.shortcuts import render, redirect
from django.contrib.auth import views as auth_views, login
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView, ListView

from .forms import (
    SolicitudForm,
    DestinoForm)
from .models import Solicitud, Ruta, Destino
from usuarios.models import MyUser


class SolicitudListView(ListView):
    model = Solicitud
    template_name = 'fletes/solicitudes.html'
    context_object_name = 'solicitudes'

    def get_queryset(self):
        return Solicitud.objects.filter(
            cliente_id=self.request.user
        ).order_by('-creado')

class SolicitudesAgregar(CreateView):
    model = Solicitud
    form_class = SolicitudForm
    template_name = 'fletes/agregarSolicitud.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        id = self.request.user.id
        #encierros = Encierro.objects.filter(user=id)
        #context['encierros'] = encierros
        return context

    def form_valid(self, form):
        user = MyUser.objects.get(pk=self.kwargs['pk'])
        self.object = form.save(commit=False)
        self.object.cliente_id = user
        self.object.save()
        messages.success(self.request, f'Solicitud agregada correctamente')
        return redirect(reverse('agregar-destino', kwargs={'pk': self.object.ruta.id}))

class DestinoAgregar(CreateView):
    model = Destino
    form_class = DestinoForm
    template_name = 'fletes/ruta.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        ruta_id = int([i for i in str(self.request.path).split('/') if i][-1])
        print(ruta_id)
        destinos = Destino.objects.filter(ruta_id=ruta_id)
        print(destinos)
        context['destinos'] = destinos
        return context

    def form_valid(self, form):
        #user_id = MyUser.objects.get(pk=self.kwargs['pk'])
        user_id = self.request.user.id
        sol_id = Solicitud.objects.filter(cliente_id=user_id).last()
        rut_id = Ruta.objects.filter(solicitud_id=sol_id).first()
        
        self.object = form.save(commit=False)
        self.object.ruta_id = rut_id
        self.object.save()
        messages.success(self.request, f'Destino agregado correctamente')
        return redirect(reverse('profile-cliente', kwargs={'pk': self.request.user.id}))