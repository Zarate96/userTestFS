from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse, reverse_lazy
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django.db.models import ProtectedError, Sum
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views, login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView, ListView
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied

from .forms import (
    SolicitudForm,
    DestinoForm,
    DomicilioForm,
    CotizacionForm,)
from .models import Solicitud, Destino, Domicilios,Cotizacion
from usuarios.models import MyUser, Unidades

class SolicitudClienteListView(ListView):
    model = Solicitud
    template_name = 'fletes/solicitudes.html'
    context_object_name = 'solicitudes'

    def get_queryset(self):
        return Solicitud.objects.filter(
            cliente_id=self.request.user.cliente
        ).order_by('-creado')

class SolicitudListView(ListView):
    model = Solicitud
    template_name = 'fletes/solicitudes.html'
    context_object_name = 'solicitudes'

    def get_queryset(self):
        return Solicitud.objects.all().order_by('-creado').exclude(estado_solicitud="Guardada")

class SolicitudesAgregar(UserPassesTestMixin, CreateView):
    model = Solicitud
    form_class = SolicitudForm
    template_name = 'fletes/agregarSolicitud.html'
    
    def test_func(self):
        if self.request.user.is_cliente:
            if self.request.user.has_datosfiscales and self.request.user.cliente.has_info:
                return True
            else:
                return False
        
        else:
            return False

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        id = self.request.user.id
        domicilios = Domicilios.objects.filter(cliente_id=id)
        context['domicilios'] = domicilios
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class=self.form_class)
        form.fields['domicilio_id'].queryset = Domicilios.objects.filter(cliente_id=self.request.user.id)
        return form

    def form_valid(self, form):
        user = self.request.user
        self.object = form.save(commit=False)
        self.object.cliente_id = user.cliente
        self.object.estado_solicitud = "Guardada"
        self.object.save()
        messages.success(self.request, f'Solicitud agregada correctamente')
        return redirect(reverse('agregar-destino', kwargs={'id': self.object.id}))

class SolicitudDetalle(DetailView):
    model = Solicitud
    template_name = 'fletes/solicitud.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        solicitud = self.get_object()
        destinos = Destino.objects.filter(solicitud_id=solicitud)
        context['destinos'] = destinos
        return context

@login_required
def SolicitudDelete(request, id):
    solicitud = get_object_or_404(Solicitud, id=id)
    cliente = request.user.cliente
    if solicitud.estado_solicitud == 'Cotizada':
        messages.success(request, f'No puedes eliminar una solicitud con cotizaciones activas')
        return HttpResponseRedirect(reverse('solicitudes-cliente'))
    
    if solicitud.cliente_id == cliente:
        solicitud.delete()
        messages.success(request, f'Solicitud eliminado correctamente')
        return HttpResponseRedirect(reverse('solicitudes-cliente'))
    else:
        raise PermissionDenied()

class DestinoAgregar(UserPassesTestMixin, CreateView):

    model = Destino
    form_class = DestinoForm
    template_name = 'fletes/ruta.html'

    def test_func(self):
        solicitudId = int([i for i in str(self.request.path).split('/') if i][-1])
        solicitud = get_object_or_404(Solicitud, id=solicitudId)
        
        if solicitud.estado_solicitud != "Guardada":
            return False
        elif self.request.user.is_cliente and solicitud.cliente_id == self.request.user.cliente :
            return True
        else:
            return False

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        solicitudId = int([i for i in str(self.request.path).split('/') if i][-1])
        id = self.request.user.id
        solicitud = get_object_or_404(Solicitud, id=solicitudId)
        domicilios = Domicilios.objects.filter(cliente_id=id)
        destinos = Destino.objects.filter(solicitud_id=solicitudId)
        context['domicilios'] = domicilios
        context['destinos'] = destinos
        context['solicitud'] = solicitud
        return context
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class=self.form_class)
        form.fields['domicilio_id'].queryset = Domicilios.objects.filter(cliente_id=self.request.user.cliente)
        return form

    def form_valid(self, form):
        self.object = form.save(commit=False)
        solicitudId = int([i for i in str(self.request.path).split('/') if i][-1])
        solicitud = Solicitud.objects.get(id=solicitudId)
        if self.object.domicilio_id.id in solicitud.get_domiciliosid_destinos():
            if Destino.objects.filter(solicitud_id=solicitud, domicilio_id=self.object.domicilio_id).exists():
                messages.success(self.request, f'No puedes agreagr el mismo domicilio a la ruta actual')
            else:
                messages.success(self.request, f'No puedes agreagr el mismo domicilio a la ruta actual')

            return redirect(reverse('agregar-destino', kwargs={'id': solicitudId}))

        if solicitud.domicilio_id == self.object.domicilio_id:
            messages.success(self.request, f'El domicilio de entrega no puede ser igual al domicilio de distino')
        else:
            self.object.solicitud_id = Solicitud.objects.get(id=solicitudId)
            self.object.save()
            messages.success(self.request, f'Destino agregado correctamente')

        return redirect(reverse('agregar-destino', kwargs={'id': solicitudId}))

@login_required
def DestinoDelete(request, id):
    destino = get_object_or_404(Destino, id=id)
    solicitudId = destino.solicitud_id.id
    cliente = request.user.cliente
    if destino.solicitud_id.cliente_id == cliente:
        destino.delete()
        messages.success(request, f'Destino eliminado correctamente')
        return HttpResponseRedirect(reverse('agregar-destino', args=(solicitudId,)))
    else:
        raise PermissionDenied()

class DomiciliosListView(ListView):
    model = Domicilios
    template_name = 'fletes/domicilios.html'
    context_object_name = 'domicilios'

    def get_queryset(self):
        return Domicilios.objects.filter(
            cliente_id=self.request.user.cliente
        ).order_by(
            '-creado'
        )

class DomicilioAgregar(UserPassesTestMixin, CreateView):
    
    model = Domicilios
    form_class = DomicilioForm
    template_name = 'fletes/agregarDomicilio.html'

    def test_func(self):
        if self.request.user.is_cliente:
            return True
        else:
            return False
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['titulo'] = "Agregar domicilio"
        return context

    def form_valid(self, form):
        user = self.request.user.cliente
        self.object = form.save(commit=False)
        self.object.cliente_id = user
        self.object.save()
        return redirect(reverse('domicilios'))

class DomiciliosUpdate(UserPassesTestMixin, UpdateView):
    model = Domicilios
    template_name = 'fletes/agregarDomicilio.html'
    form_class = DomicilioForm

    def test_func(self):
        domicilio = self.get_object()
        
        if self.request.user.is_cliente and domicilio.cliente_id == self.request.user.cliente :
            return True
        else:
            return False

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['titulo'] = "Editar domicilio"
        return context

    def get_success_url(self):
        messages.success(self.request, f'Domicilio editado correctamente')
        return reverse('domicilios')

@login_required
def DomiciliosDelete(request, slug):
    domicilio = get_object_or_404(Domicilios, slug=slug)
    cliente = request.user.cliente
    
    if domicilio.cliente_id == cliente:
        try:
            domicilio.delete()
            messages.success(request, f'Domicilio eliminado correctamente')
        except ProtectedError:
            messages.success(request, f'No se puede eliminar este domicilio, esta referenciado a una o mas solicitudes')
        
        return HttpResponseRedirect(reverse('domicilios'))
    else:
        raise PermissionDenied()

@login_required
def FinalizarSolicitud(request, id):
    solicitud = get_object_or_404(Solicitud, id=id)
    cliente = request.user.cliente
    destinos = Destino.objects.filter(solicitud_id=solicitud)
    totales = Destino.objects.filter(solicitud_id=solicitud).aggregate(Sum('unidades_entregar'))
    if totales['unidades_entregar__sum'] == solicitud.unidades_totales:
        if solicitud.cliente_id == cliente:
            solicitud.estado_solicitud = "Publicada"
            solicitud.save()
            context = {
                'solicitud':solicitud,
                'destinos': destinos,
            }
            #messages.success(request, f'Ruta de solicitud agregada correctamente')
            return render(request, 'fletes/finalizar.html', context)
        else:
            raise PermissionDenied()
    else:
        messages.success(request, f'Las unidades a entregar son mayores o menores que las unidades totales')
        return HttpResponseRedirect((reverse('agregar-destino', kwargs={'id': solicitud.id})))

class CotizacionListView(UserPassesTestMixin, ListView):
    model = Cotizacion
    template_name = 'fletes/cotizaciones.html'
    context_object_name = 'cotizaciones'

    def test_func(self):
        if self.request.user.is_transportista:
            return True
        else:
            return False

    def get_queryset(self):
        return Cotizacion.objects.filter(
            transportista_id=self.request.user.transportista
        ).order_by('-creado')

class CotizacionAgregar(UserPassesTestMixin, CreateView):
    model = Cotizacion
    form_class = CotizacionForm
    template_name = 'fletes/agregarCotizacion.html'

    def test_func(self):
        if self.request.user.is_transportista:
            if self.request.user.has_datosfiscales and self.request.user.transportista.has_info and self.request.user.transportista.has_unidades:
                return True
            else:
                return False
        else:
            return False

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        slug = self.kwargs['slug']
        solicitud = get_object_or_404(Solicitud, slug=slug)
        destinos = Destino.objects.filter(solicitud_id=solicitud.id)
        context['destinos'] = destinos
        context['solicitud'] = solicitud
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class=self.form_class)
        form.fields['unidad_id'].queryset = Unidades.objects.filter(user=self.request.user.id)
        return form

    def form_valid(self, form):
        user = self.request.user
        slug = self.kwargs['slug']
        solicitud = get_object_or_404(Solicitud, slug=slug)
        self.object = form.save(commit=False)
        self.object.transportista_id = user.transportista
        self.object.solicitud_id = solicitud
        if Cotizacion.objects.filter(solicitud_id=solicitud, transportista_id=user.transportista).exists():
            messages.success(self.request, f'Ya creaste una cotización para la solicitud {solicitud.folio}')
        else:  
            try:
                self.object.save()
                messages.success(self.request, f'Cotización agregada correctamente')
            except IntegrityError:
                messages.success(self.request, f'Ya creaste una cotización para esta solicitud')
        
        return redirect(reverse('cotizaciones'))

class CotizacionListClienteView(ListView):
    model = Cotizacion
    template_name = 'fletes/cotizacionesCliente.html'
    context_object_name = 'cotizaciones'

    def test_func(self):
        if self.request.user.is_cliente:
            return True
        else:
            return False

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        solicitud = get_object_or_404(Solicitud, slug=self.kwargs['slug'])
        destinos = Destino.objects.filter(solicitud_id=solicitud.id)
        context['solicitud'] = solicitud
        context['destinos'] = destinos
        return context

    def get_queryset(self):
        solicitud = get_object_or_404(Solicitud, slug=self.kwargs['slug'])

        return Cotizacion.objects.filter(
            solicitud_id=solicitud
        ).order_by('-creado')

@login_required
def ContizacionDelete(request, slug):
    cotizacion = get_object_or_404(Cotizacion, slug=slug)
    
    try:
        transportista = request.user.transportista
    except ObjectDoesNotExist:
        raise PermissionDenied()

    if cotizacion.transportista_id == transportista:
        if cotizacion.estado_cotizacion == 'Pendiente' or cotizacion.estado_cotizacion == 'Rechazada':
            try:
                cotizacion.delete()
                messages.success(request, f'Cotización eliminada correctamente')
            except ProtectedError:
                messages.success(request, f'No se puede eliminar esta cotización se encuentra en estado de confirmada')
        else:
            messages.success(request, f'Cotización activa si la eliminas recibiras una penalización')
        return HttpResponseRedirect(reverse('cotizaciones'))
    else:
        raise PermissionDenied()

@login_required
def aceptarCotizacion(request, slug):
    cotizacion = get_object_or_404(Cotizacion, slug=slug)

    try:
        cliente = request.user.cliente
    except ObjectDoesNotExist:
        raise PermissionDenied()

    if cotizacion.solicitud_id.cliente_id == cliente:
        if cotizacion.estado_cotizacion == "Pendiente":
            try:
                cotizacion.estado_cotizacion = "Aceptada"
                cotizacion.save()
                Cotizacion.objects.exclude(
                        id=cotizacion.id).filter(
                        solicitud_id=cotizacion.solicitud_id.id).update(
                        estado_cotizacion='Rechazada')
                messages.success(request, f'Cotización aceptada correctamente')
            except ProtectedError:
                messages.success(request, f'Algo salio mal!!!')
        
        else:
            messages.success(request, f'Ya has aceptado esta solicitud')
            return HttpResponseRedirect(reverse('cotizaciones-cliente', kwargs={'id': cotizacion.solicitud_id}))
        
        return HttpResponseRedirect(reverse('solicitudes-cliente'))
    else:
        raise PermissionDenied()

@login_required
def confirmarCotizacion(request, slug):
    cotizacion = get_object_or_404(Cotizacion, slug=slug)

    try:
        transportista = request.user.transportista
    except ObjectDoesNotExist:
        print("Error")
        raise PermissionDenied()

    if cotizacion.transportista_id == transportista:
        if cotizacion.estado_cotizacion == "Aceptada":
            try:
                cotizacion.estado_cotizacion = "Confirmada"
                cotizacion.save()
                messages.success(request, f'Cotización confirmada correctamente')
            except ProtectedError:
                messages.success(request, f'Algo salio mal!!!')
        
        else:
            messages.success(request, f'No puedes modificar el estado de esta cotización')
            return HttpResponseRedirect(reverse('cotizaciones-cliente', kwargs={'id': cotizacion.solicitud_id}))
        
        return HttpResponseRedirect(reverse('cotizaciones'))
    else:
        raise PermissionDenied()

@login_required
def rechazarCotizacion(request, slug):
    cotizacion = get_object_or_404(Cotizacion, slug=slug)

    try:
        cliente = request.user.cliente
    except ObjectDoesNotExist:
        raise PermissionDenied()

    if cotizacion.solicitud_id.cliente_id == cliente:
        if cotizacion.estado_cotizacion == "Pendiente":
            try:
                cotizacion.estado_cotizacion = "Rechazada"
                cotizacion.save()
                messages.success(request, f'Cotización rechazada correctamente')
            except ProtectedError:
                messages.success(request, f'Algo salio mal!!!')
        
        else:
            messages.success(request, f'Ya has rechazado esta solicitud')
            return HttpResponseRedirect(reverse('cotizaciones-cliente', kwargs={'id': cotizacion.solicitud_id}))
        
        return HttpResponseRedirect(reverse('solicitudes-cliente'))
    else:
        raise PermissionDenied()

class CotizacionUpdate(UserPassesTestMixin, UpdateView):
    model = Cotizacion
    template_name = 'fletes/cotizacionUpdate.html'
    form_class = CotizacionForm

    def test_func(self):
        cotizacion = self.get_object()
        try:
            transportista = self.request.user.transportista
        except ObjectDoesNotExist:
            return False

        if cotizacion.transportista_id == transportista:
            return True
        else:
            return False

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['cotizacion'] = self.get_object()
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        
        if self.object.estado_cotizacion != "Rechazada":
            messages.success(self.request, f'No puedes actualizar esta cotización')
        else:
            self.object.estado_cotizacion = "Pendiente"
            self.object.save()
            messages.success(self.request, f'Cotización actualizada correctamente')
        return redirect(reverse('cotizaciones'))

class CotizacionDetalle(DetailView):
    model = Cotizacion
    template_name = 'fletes/cotizacionDetalle.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        cotizacion = self.get_object()
        destinos = Destino.objects.filter(solicitud_id=cotizacion.solicitud_id)
        solicitud = Solicitud.objects.get(id=cotizacion.solicitud_id.id)
        context['destinos'] = destinos
        context['solicitud'] = solicitud
        return context
