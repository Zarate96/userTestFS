import googlemaps
import conekta
import requests
import datetime
import json
import mimetypes
from wsgiref.util import FileWrapper
from http.client import HTTPSConnection
from base64 import b64encode
from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse, reverse_lazy
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError, Sum
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views, login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView, ListView
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied

from .forms import (
    SolicitudForm,
    SolicitudMotivoCancelacioForm,
    DestinoForm,
    DomicilioForm,
    CotizacionForm,
    CotizacionMotivoCancelacioForm,
    AgregarSeguroForm,
    AgregarEvidenciaForm,
    AgregarFacturasForm,)
from .models import Solicitud, Destino, Domicilios,Cotizacion, Viaje, Orden
from usuarios.models import MyUser, Unidades, Contacto
from .filters import SolicitudesFilter

gmaps = googlemaps.Client(key='AIzaSyDHQMz-SW5HQm3IA2hSv2Bct9L76_E60Ec')
conekta.locale = 'es'
conekta.api_key = "key_BQzUZ8k2yyaXunkYaxZr23A"
conekta.api_version = "2.0.0"

class SolicitudClienteListView(UserPassesTestMixin, ListView):
    model = Solicitud
    template_name = 'fletes/solicitudes.html'
    context_object_name = 'solicitudes'

    def test_func(self):
        print(self.request.user.cliente)
        try:
            cliente = self.request.user.cliente
            return True
        except ObjectDoesNotExist:
            return False

    def get_queryset(self):
        return Solicitud.objects.filter(
            cliente_id=self.request.user.cliente
        ).order_by('-creado').exclude(
            activo=False
        )

class SolicitudListView(UserPassesTestMixin, ListView):
    model = Solicitud
    template_name = 'fletes/solicitudesFilterList.html'
    context_object_name = 'solicitudes'

    def test_func(self):
        try:
            cliente = self.request.user.transportista
            return True
        except ObjectDoesNotExist:
            return False

    def get_queryset(self):
        return Solicitud.objects.all().order_by('-creado').exclude(estado_solicitud="Guardada").exclude(estado_solicitud="Asignada").exclude(estado_solicitud="Cancelada").exclude(activo=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = SolicitudesFilter(self.request.GET, queryset=self.get_queryset())
        return context

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
        domicilios = Domicilios.objects.filter(cliente_id=id, is_valid=True)
        if domicilios:
            context['lenDom'] = len(domicilios)
        else:
            context['lenDom'] = 0
        context['domicilios'] = domicilios
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class=self.form_class)
        form.fields['domicilio_id'].queryset = Domicilios.objects.filter(cliente_id=self.request.user.id, is_valid=True)
        return form

    def form_valid(self, form):
        user = self.request.user
        self.object = form.save(commit=False)
        self.object.cliente_id = user.cliente
        self.object.estado_solicitud = "Guardada"
        self.object.save()
        messages.success(self.request, f'Solicitud agregada correctamente')
        return redirect(reverse('fletes:agregar-destino', kwargs={'id': self.object.id}))

class SolicitudDetalle(DetailView):
    model = Solicitud
    template_name = 'fletes/solicitud.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        solicitud = self.get_object()
        destinos = Destino.objects.filter(solicitud_id=solicitud)
        context['destinos'] = destinos
        return context

class SolicitudUpdate(UserPassesTestMixin, UpdateView):
    model = Solicitud
    form_class = SolicitudForm
    template_name = 'fletes/updateSolicitud.html'

    def test_func(self):
        solicitud = self.get_object()
        try:
            cliente = self.request.user.cliente
        except ObjectDoesNotExist:
            return False

        if solicitud.estado_solicitud != "Guardada":
            return False

        if solicitud.cliente_id == cliente:
            return True
        else:
            return False

    def get_form(self, form_class=None):
        form = super().get_form(form_class=self.form_class)
        form.fields['domicilio_id'].queryset = Domicilios.objects.filter(cliente_id=self.request.user.id, is_valid=True)
        # form.fields['material_peligroso'].initial = self.get_object().material_peligroso
        form.fields['material_peligroso'].initial = True
        return form
        
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['solicitud'] = self.get_object()
        domicilios = Domicilios.objects.filter(cliente_id=self.request.user.id, is_valid=True)
        context['domicilios'] = domicilios
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()
        messages.success(self.request, f'Solicitud actualizada correctamente')
        
        return redirect(reverse('fletes:agregar-destino', kwargs={'id': self.object.id}))

class SolicitudCancel(UserPassesTestMixin, UpdateView):
    model = Solicitud
    form_class = SolicitudMotivoCancelacioForm
    template_name = 'fletes/confirmations/cancel_solicitud_modal.html'

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def test_func(self):
        solicitud = self.get_object()
        try:
            cliente = self.request.user.cliente
        except ObjectDoesNotExist:
            return False

        if solicitud.estado_solicitud == "Cancelada":
            return False

        if solicitud.cliente_id == cliente:
            return True
        else:
            return False

    def form_valid(self, form):
        self.object = form.save(commit=False)
        with transaction.atomic():
            self.object.estado_solicitud = 'Cancelada'
            self.object.activo = False
            self.object.save()
            user = self.request.user
            user.penalizaciones = user.penalizaciones + 1
            user.save()
            Cotizacion.objects.filter(
                solicitud_id=self.object.id).update(
                estado_cotizacion='Solicitud cancelada')
        messages.success(self.request, f'Solicitud cancelada correctamente')
        
        return redirect(reverse('fletes:solicitudes-cliente'))

@login_required
def SolicitudDelete(request, id):
    solicitud = get_object_or_404(Solicitud, id=id)
    cliente = request.user.cliente
    if solicitud.estado_solicitud == 'Cotizada' or solicitud.estado_solicitud == 'Asignada':
        messages.success(request, f'No puedes eliminar una solicitud con cotizaciones activas')
        return HttpResponseRedirect(reverse('solicitudes-cliente'))
    
    if solicitud.cliente_id == cliente:
        solicitud.activo = False
        solicitud.estado_solicitud = 'Cancelada'
        solicitud.save()
        messages.success(request, f'Solicitud eliminada correctamente')
        return HttpResponseRedirect(reverse('fletes:solicitudes-cliente'))
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
        domicilios = Domicilios.objects.filter(cliente_id=id, is_valid=True)
        destinos = Destino.objects.filter(solicitud_id=solicitudId)
        context['domicilios'] = domicilios
        context['destinos'] = destinos
        context['solicitud'] = solicitud
        return context
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class=self.form_class)
        form.fields['domicilio_id'].queryset = Domicilios.objects.filter(cliente_id=self.request.user.cliente, is_valid=True)
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

            return redirect(reverse('fletes:agregar-destino', kwargs={'id': solicitudId}))

        if solicitud.domicilio_id == self.object.domicilio_id:
            messages.success(self.request, f'El domicilio de entrega no puede ser igual al domicilio de distino')
        else:
            self.object.solicitud_id = Solicitud.objects.get(id=solicitudId)
            self.object.save()
            messages.success(self.request, f'Destino agregado correctamente')

        return redirect(reverse('fletes:agregar-destino', kwargs={'id': solicitudId}))

class DestinoUpdate(UserPassesTestMixin, UpdateView):
    model = Destino
    form_class = DestinoForm
    template_name = 'fletes/confirmations/updateDestino.html'

    def test_func(self):
        destino = self.get_object()
        try:
            cliente = self.request.user.cliente
        except ObjectDoesNotExist:
            return False

        if destino.solicitud_id.cliente_id == cliente:
            return True
        else:
            return False

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()
        messages.success(self.request, f'Destino actualizada correctamente')
        
        return redirect(reverse('fletes:agregar-destino', kwargs={'id': self.object.solicitud_id.id}))

@login_required
def DestinoDelete(request, id):
    destino = get_object_or_404(Destino, id=id)
    solicitudId = destino.solicitud_id.id
    cliente = request.user.cliente
    if destino.solicitud_id.cliente_id == cliente:
        destino.delete()
        messages.success(request, f'Destino eliminado correctamente')
        return HttpResponseRedirect(reverse('fletes:agregar-destino', args=(solicitudId,)))
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
        self.object = form.save(commit=False)
        user = self.request.user.cliente
        current_name = self.object.nombre
        domicilios = Domicilios.objects.filter(
            cliente_id=user
        )
        flag = True
        for domicilio in domicilios:
            if flag == False:
                flag = False
            elif domicilio.nombre == current_name:
                flag = False
        
        if flag == False:
            messages.success(self.request, f'Ya existe un domicilio registrado con este nombre')
        else:
            self.object.cliente_id = user
            self.object.save()
            messages.success(self.request, f'Verifique que el domicilio sea válido, en caso contrario por favor actualize los datos correctamente.')
        
        return redirect(reverse('fletes:domicilios'))
            
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
        context['domicilio'] = self.get_object()
        return context

    def get_success_url(self):
        print(self.get_object())
        domicilio = self.get_object()
        if domicilio.is_valid:
            messages.success(self.request, f'Domicilio editado correctamente')
        else:
            messages.error(self.request, f'Domicilio incorrecto porfavor verifique la información propocionada')
        return reverse('fletes:domicilios')

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
        
        return HttpResponseRedirect(reverse('fletes:domicilios'))
    else:
        raise PermissionDenied()

@login_required
def FinalizarSolicitud(request, id):
    solicitud = get_object_or_404(Solicitud, id=id)
    cliente = request.user.cliente
    destinos = Destino.objects.filter(solicitud_id=solicitud)
    totales = Destino.objects.filter(solicitud_id=solicitud).aggregate(Sum('unidades_entregar'))
    if solicitud.domicilio_id.id in solicitud.get_domiciliosid_destinos():
            if Destino.objects.filter(solicitud_id=solicitud, domicilio_id=solicitud.domicilio_id).exists():
                messages.success(request, f'No puedes agreagr el mismo domicilio a la ruta actual')
            else:
                messages.success(request, f'No puedes agreagr el mismo domicilio a la ruta actual')

            return redirect(reverse('fletes:agregar-destino', kwargs={'id': solicitud.id}))

    if totales['unidades_entregar__sum'] == solicitud.unidades_totales:
        if solicitud.cliente_id == cliente:
            origen = solicitud.domicilio_id
            origenCoordenadas = []
            origenCoordenadas.append(origen.latitud)
            origenCoordenadas.append(origen.longitud)
            tiempoTotal = 0
            kmTotal = 0
            for destino in destinos:
                currentDestinoCoordenadas = []
                currentDestinoCoordenadas.append(destino.domicilio_id.latitud)
                currentDestinoCoordenadas.append(destino.domicilio_id.longitud)
                origins = [
                    origenCoordenadas,
                ]
                destinations = [
                    currentDestinoCoordenadas,
                ]
                currentMatrixData = gmaps.distance_matrix(origins,destinations)
                kmTotal += float(currentMatrixData["rows"][0]["elements"][0]["distance"]["text"][0:2])
                tiempoTotal += float(currentMatrixData["rows"][0]["elements"][0]["duration"]["text"][0:2])
                origenCoordenadas = currentDestinoCoordenadas

            solicitud.estado_solicitud = "Publicada"
            solicitud.tiempo_total = tiempoTotal
            solicitud.km_total = kmTotal
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
        return HttpResponseRedirect((reverse('fletes:agregar-destino', kwargs={'id': solicitud.id})))

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
        ).order_by('-creado').exclude(activo=False)

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
        locations = []
        locations.append({'lat':float(solicitud.domicilio_id.latitud), 'lng':float(solicitud.domicilio_id.longitud)})
        for destino in destinos:
            locations.append({'lat':float(destino.domicilio_id.latitud), 'lng':float(destino.domicilio_id.longitud)})
        center = locations[0]
        #print(locations)
        context['solicitud'] = solicitud
        context['center'] = center
        context['locations'] = locations
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
        if solicitud.estado_solicitud == 'Publicada' or solicitud.estado_solicitud == 'Cotizada':
            if Cotizacion.objects.filter(solicitud_id=solicitud, transportista_id=user.transportista).exists():
                messages.success(self.request, f'Ya has cotizado la solicitud {solicitud.folio}')
            else:  
                try:
                    self.object.save()
                    messages.success(self.request, f'Cotización agregada correctamente')
                except IntegrityError as e:
                    messages.success(self.request, f'Ya creaste una cotización para esta solicitud')
                    print(e)
        else:
            raise PermissionDenied()
        return redirect(reverse('fletes:cotizaciones'))

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
                with transaction.atomic():
                    cotizacion.activo = False
                    cotizacion.estado_cotizacion = "Cancelada"
                    cotizacion.save()
                    messages.success(request, f'Cotización eliminada correctamente')
            except ProtectedError:
                messages.success(request, f'No se puede eliminar esta cotización se encuentra en estado de confirmada')
        else:
            raise PermissionDenied()
        return HttpResponseRedirect(reverse('fletes:cotizaciones'))
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
                #Rechazar el resto de cotizaciones de la solicitud
                Cotizacion.objects.exclude(
                        id=cotizacion.id).filter(
                        solicitud_id=cotizacion.solicitud_id.id).update(
                        estado_cotizacion='Rechazada')
                messages.success(request, f'Cotización aceptada correctamente')
            except ProtectedError:
                messages.success(request, f'Algo salio mal!!!')
        
        else:
            messages.success(request, f'Ya has aceptado esta solicitud')
            return HttpResponseRedirect(reverse('fletes:cotizaciones-cliente', kwargs={'slug': cotizacion.solicitud_id.slug}))
        
        return HttpResponseRedirect(reverse('fletes:solicitudes-cliente'))
    else:
        raise PermissionDenied()

@login_required
def confirmarCotizacion(request, slug):
    cotizacion = get_object_or_404(Cotizacion, slug=slug)

    try:
        transportista = request.user.transportista
    except ObjectDoesNotExist:
        raise PermissionDenied()

    if cotizacion.transportista_id == transportista:
        if cotizacion.estado_cotizacion == "Aceptada":
            try:
                cotizacion.estado_cotizacion = "Confirmada"
                cotizacion.save()
                solicitud = get_object_or_404(Solicitud, id=cotizacion.solicitud_id.id)
                solicitud.estado_solicitud = "Asignada"
                solicitud.save()
                messages.success(request, f'Cotización confirmada correctamente')
            except ProtectedError:
                messages.success(request, f'Algo salio mal!!!')
        
        else:
            messages.success(request, f'No puedes modificar el estado de esta cotización')
            return HttpResponseRedirect(reverse('fletes:cotizaciones'))
        
        return HttpResponseRedirect(reverse('fletes:cotizaciones'))
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

class CotizacionCancel(UserPassesTestMixin, UpdateView):
    model = Cotizacion
    form_class = CotizacionMotivoCancelacioForm
    template_name = 'fletes/confirmations/cancel_solicitud_modal.html'

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def test_func(self):
        cotizacion = self.get_object()
        try:
            transportista = self.request.user.transportista
        except ObjectDoesNotExist:
            return False

        if cotizacion.estado_cotizacion == "Cancelada" or cotizacion.estado_cotizacion == "Solicitud cancelada":
            return False

        if cotizacion.transportista_id == transportista:
            return True
        else:
            return False

    def form_valid(self, form):
        self.object = form.save(commit=False)
        with transaction.atomic():
            self.object.estado_cotizacion = 'Cancelada'
            self.object.activo = False
            self.object.save()
            user = self.request.user
            user.penalizaciones = user.penalizaciones + 1
            user.save()

        messages.success(self.request, f'Cotización cancelada correctamente')
        
        return redirect(reverse('fletes:cotizaciones'))
        
class SeleccionarSeguro(UserPassesTestMixin, UpdateView):
    model = Cotizacion
    form_class = AgregarSeguroForm
    template_name = 'fletes/seleccionarSeguro.html'

    def test_func(self):
        cotizacion = self.get_object()

        try:
            cliente = self.request.user.cliente
        except ObjectDoesNotExist:
            return False

        if cotizacion.getClienteId() == cliente:
            return True
        else:
            return False

        if cotizacion.getClienteId() == cliente:
            return False if cotizacion.estado_cotizacion != "Confirmada" else True
        else:
            return False

    def form_valid(self, form):
        self.object = form.save(commit=False)
        if self.object.es_asegurada:
            if self.object.nivel_seguro == '' or self.object.nivel_seguro == None:
                messages.error(self.request, f'Porfavor seleccione un nivel de seguro')
                return redirect(reverse('fletes:seleccionar-seguro', kwargs={'slug': self.object.slug}))
            if self.object.aceptar_tyc == False or self.object.aceptar_tyc == None:
                messages.error(self.request, f'Por favor acepte los términos y condiciones')
                return redirect(reverse('fletes:seleccionar-seguro', kwargs={'slug': self.object.slug}))
        else:
            self.object.nivel_seguro = None

        self.object.save()
        messages.success(self.request, f'Información validada correctamente')
        
        return redirect(reverse('fletes:checkout', kwargs={'slug': self.object.slug}))

class checkout(UserPassesTestMixin, DetailView):
    model = Cotizacion
    template_name = 'fletes/checkout.html'

    def test_func(self):
        cotizacion = self.get_object()
        try:
            cliente = self.request.user.cliente
        except ObjectDoesNotExist:
            return False

        if cotizacion.getClienteId() == cliente:
            return False if cotizacion.estado_cotizacion != "Confirmada" else True
        else:
            return False
            
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        cotizacion = self.get_object()
        destinos = Destino.objects.filter(solicitud_id=cotizacion.solicitud_id)
        solicitud = Solicitud.objects.get(id=cotizacion.solicitud_id.id)
        
        if cotizacion.es_asegurada:
            subtotal = cotizacion.monto + cotizacion.nivel_seguro.costo
        else:
            subtotal = cotizacion.monto
        iva = subtotal * 0.16
        context['destinos'] = destinos
        context['solicitud'] = solicitud
        context['subtotal'] = subtotal
        context['iva'] = iva
        return context

@login_required
def PagarCotizacion(request, slug):
    cotizacion = get_object_or_404(Cotizacion, slug=slug)

    try:
        cliente = request.user.cliente
    except ObjectDoesNotExist:
        raise PermissionDenied()

    if cotizacion.estado_cotizacion != 'Confirmada':
        raise PermissionDenied()
        
    else:
        try:
            total = f'{int(cotizacion.total)}00'
            today = datetime.datetime.now()
            fecha_limite = today + datetime.timedelta(days=3)
            fecha_limite_timestamp = datetime.datetime.timestamp(fecha_limite)
            cotizacionStr = (f'{cotizacion.folio}')
            print(f"DATA: {cotizacionStr} FECHA: {fecha_limite_timestamp}")
            print(cotizacionStr)
            order = {
                "name": "PagoFleteSeguro",
                "type": "PaymentLink",
                "recurrent": False,
                "expires_at": round(fecha_limite_timestamp),
                "allowed_payment_methods": ["cash", "card", "bank_transfer"],
                "needs_shipping_contact": False,
                "monthly_installments_enabled": False,
                "order_template": {
                    "line_items": [{
                        "name": cotizacionStr,
                        "unit_price": int(total),
                        "quantity": 1
                    }],
                    "currency": "MXN",
                    "customer_info": {
                        "customer_id": request.user.cliente.conektaId
                    },
                    "metadata": {
                        "mycustomkey": "12345",
                        "othercustomkey": "abcd"
                    }
                }
            }
        except Exception as e:
            print(e)
            messages.success(request, f'No se pudo generar la orden!! {e}')
            return HttpResponseRedirect(reverse(reverse('fletes:checkout', kwargs={'slug': cotizacion.slug})))
            
        
        try:
            checkout = conekta.Checkout.create(order)
            print(checkout)
            id_link = checkout.id
            url_link = checkout.url
            status_link = checkout.status
            orden = Orden.objects.create(cotizacion_id=cotizacion, link_id=id_link, link_url=url_link, link_status=status_link)
            cotizacion.estado_cotizacion = 'Pendiente de pago'
            cotizacion.save()
            return HttpResponseRedirect(url_link)
        except conekta.ConektaError as e:
            print(e.message)
            messages.success(request, f'No se pudo generar la orden!!{e.message} {cotizacionStr} {type(cotizacionStr)}')
            return HttpResponseRedirect(reverse('fletes:checkout', kwargs={'slug': cotizacion.slug}))

def PagoConfirmado(request):
    print(request)
    data = request.path
    print(request.path)
    context = {
        'data' : data
    }

    return render(request, 'fletes/pagoConfirmado.html', context)

def PagoDenegado(request):
    print(request)
    data = request.path
    print(request.path)
    context = {
        'data' : data
    }

    return render(request, 'fletes/pagoDenegado.html', context)

class ViajesListView(ListView):
    model = Viaje
    template_name = 'fletes/viajes.html'
    context_object_name = 'viajes'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['user'] = self.request.user
        return context

class ViajesDetalle(DetailView):
    model = Viaje
    template_name = 'fletes/viajeDetalle.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        viaje = self.get_object()
        destinos = Destino.objects.filter(solicitud_id=viaje.orden_id.cotizacion_id.solicitud_id)
        cliente = viaje.orden_id.cotizacion_id.solicitud_id.cliente_id
        contactos = Contacto.objects.filter(user=cliente.user)
        allEvidencias = True
        for destino in destinos:
            if destino.hasEvidencias() is True:
                allEvidencias = True
                #print(destino.hasEvidencias())
            else:
                allEvidencias = False
                break;

        #print(allEvidencias)
        context['destinos'] = destinos
        context['contactos'] = contactos
        context['cliente'] = cliente
        context['allEvidencias'] = allEvidencias
        return context

class ViajesEvidencias(DetailView):
    model = Viaje
    template_name = 'fletes/evidenciasCliente.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        viaje = self.get_object()
        destinos = Destino.objects.filter(solicitud_id=viaje.orden_id.cotizacion_id.solicitud_id)

        #print(allEvidencias)
        context['destinos'] = destinos
        return context

class DestinoAregarEvidencia(UpdateView):
    model = Destino
    form_class = AgregarEvidenciaForm
    template_name = 'fletes/confirmations/agregar_evidencia.html'

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        return context

    # def test_func(self):
    #     cotizacion = self.get_object()
    #     try:
    #         transportista = self.request.user.transportista
    #     except ObjectDoesNotExist:
    #         return False

    #     if cotizacion.estado_cotizacion == "Cancelada" or cotizacion.estado_cotizacion == "Solicitud cancelada":
    #         return False

    #     if cotizacion.transportista_id == transportista:
    #         return True
    #     else:
    #         return False

    def form_valid(self, form):
        self.object = form.save(commit=False)
        destino = self.get_object()
        viaje = destino.solicitud_id.cotizacionFinal().orden
        self.object.save()
        messages.success(self.request, f'Evidencias agregadas correctamente')   
        return redirect(reverse('fletes:detalle-viaje', kwargs={'slug': viaje.viaje.slug}))

class ViajeAregarFacturas(UpdateView):
    model = Viaje
    form_class = AgregarFacturasForm
    template_name = 'fletes/confirmations/agregar_facturas.html'

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        return context

    # def test_func(self):
    #     cotizacion = self.get_object()
    #     try:
    #         transportista = self.request.user.transportista
    #     except ObjectDoesNotExist:
    #         return False

    #     if cotizacion.estado_cotizacion == "Cancelada" or cotizacion.estado_cotizacion == "Solicitud cancelada":
    #         return False

    #     if cotizacion.transportista_id == transportista:
    #         return True
    #     else:
    #         return False

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()
        messages.success(self.request, f'Facturas agregadas correctamente a viaje {self.object}')   
        return redirect(reverse('viajes'))

@login_required
def dataViajeSeguridad(request, slug):
    try:
        cliente = request.user.cliente
    except ObjectDoesNotExist:
        raise PermissionDenied()
    
    viaje = get_object_or_404(Viaje, slug=slug)
    
    if viaje.orden_id.cotizacion_id.getClienteId() != cliente:
        raise PermissionDenied()
    print(viaje)
    return render(request, 'fletes/viajeSeguridad.html',{'viaje':viaje})

@login_required
def registrarLlegada(request, slug):
    try:
        transportista = request.user.transportista
    except ObjectDoesNotExist:
        raise PermissionDenied()
    
    viaje = get_object_or_404(Viaje, slug=slug)
    
    if viaje.orden_id.cotizacion_id.transportista_id != transportista:
        raise PermissionDenied()

    if viaje:
        if 'nip' in request.POST:
            nip = request.POST['nip']
            if int(nip) == viaje.nip_checkin:
                try:
                    viaje.hora_llegada = datetime.datetime.now().time()
                    viaje.estado_viaje = 'Iniciado'
                    viaje.save()
                    messages.success(request, f'Registro de llegada correcto a las {viaje.hora_llegada}')
                except ProtectedError:
                    messages.success(request, f'Registro no realizado correctamente, porfavor espere 5 minutos e intente nuevamente')
            else:
                messages.success(request, f'NIP de viaje incorrecto, favor de verificar información')
        else:
            messages.success(request, f'NIP de viaje incorrecto, favor de verificar información')
    
    return HttpResponseRedirect(reverse('fletes:detalle-viaje', kwargs={'slug': viaje.slug}))

@login_required
def registrarSalida(request, slug):
    
    try:
        transportista = request.user.transportista
    except ObjectDoesNotExist:
        raise PermissionDenied()
    
    viaje = get_object_or_404(Viaje, slug=slug)
    
    if viaje.orden_id.cotizacion_id.transportista_id != transportista:
        raise PermissionDenied()

    if viaje:
        if 'nip' in request.POST:
            nip = request.POST['nip']
            if int(nip) == viaje.nip_checkout:
                try:
                    viaje.hora_inicio = datetime.datetime.now().time()
                    viaje.estado_viaje = 'Iniciado'
                    viaje.save()
                    messages.success(request, f'NIP Correcto, se inicia el viaje')
                except ProtectedError:
                    messages.success(request, f'Algo salio mal!!!')
            else:
                messages.success(request, f'NIP de viaje incorrecto!!!')
        else:
            messages.success(request, f'Algo salio mal!!!')
    
    return HttpResponseRedirect(reverse('fletes:detalle-viaje', kwargs={'slug': viaje.slug}))

@login_required
def finalizarViaje(request, slug):
    
    try:
        transportista = request.user.transportista
    except ObjectDoesNotExist:
        raise PermissionDenied()
    
    viaje = get_object_or_404(Viaje, slug=slug)
    
    if viaje.orden_id.cotizacion_id.transportista_id != transportista:
        raise PermissionDenied()

    if viaje:
        viaje.estado_viaje = "Cerrado"
        viaje.save()
        messages.success(request, f'Viaje finalizado correctamente')
    
    return HttpResponseRedirect(reverse('fletes:viajes'))

# def download_image(request, destino):
#     destino = Destino.objects.get(id=destino)
#     print(destino)
#     foto = request.GET.get('foto')
#     print(foto)
#     if foto == '1':
#         img = destino.foto1
#     elif foto == '2':
#         img = destino.foto2
#     else:
#         img = "Invalid"
#     wrapper      = FileWrapper(open(img.file))  # img.file returns full path to the image
#     content_type = mimetypes.guess_type(filename)[0]  # Use mimetypes to get file type
#     response     = HttpResponse(wrapper,content_type=content_type)  
#     response['Content-Length']      = os.path.getsize(img.file)    
#     response['Content-Disposition'] = "attachment; filename=%s" %  img.name
#     return response
    #return HttpResponseRedirect(reverse('fletes:viajes'))
