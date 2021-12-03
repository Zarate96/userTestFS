from django.urls import include, path

from .views import *

urlpatterns = [
    path('solicitudes/', SolicitudListView.as_view(), name='solicitudes'),
    path('solicitudes/cliente', SolicitudClienteListView.as_view(), name='solicitudes-cliente'),
    path('solicitudes/agregar/', SolicitudesAgregar.as_view(), name='agregar-solicitud'),
    path('solicitudes/detalle/<slug:slug>', SolicitudDetalle.as_view(), name='detalle-solicitud'),
    path('solicitudes/delete/<int:id>', SolicitudDelete, name='delete-solicitud'),
    path('solicitudes/finalizar/<int:id>', FinalizarSolicitud, name='finalizar-solicitud'),
    path('solicitudes/agregar/destino/<int:id>', DestinoAgregar.as_view(), name='agregar-destino'),
    path('solicitudes/delete/destino/<int:id>', DestinoDelete, name='delete-destino'),
    path('domicilios/', DomiciliosListView.as_view(), name='domicilios'),
    path('domicilio/agregar/', DomicilioAgregar.as_view(), name='agregar-domiclio'),
    path('domicilio/update/<slug:slug>', DomiciliosUpdate.as_view(), name='update-domicilio'),
    path('domicilio/delete/<slug:slug>', DomiciliosDelete, name='delete-domicilio'),
    path('cotizacion/agregar/<slug:slug>', CotizacionAgregar.as_view(), name='agregar-cotizacion'),
    path('cotizaciones/', CotizacionListView.as_view(), name='cotizaciones'),
    path('cotizaciones/delete/<slug:slug>', ContizacionDelete, name='delete-cotizacion'),
    path('cotizaciones/<slug:slug>', CotizacionListClienteView.as_view(), name='cotizaciones-cliente'),
    path('cotizaciones/aceptar/<slug:slug>', aceptarCotizacion, name='aceptar-cotizacion'),
    path('cotizaciones/confirmar/<slug:slug>', confirmarCotizacion, name='confirmar-cotizacion'),
    path('cotizaciones/rechazar/<slug:slug>', rechazarCotizacion, name='rechazar-cotizacion'),
    path('cotizaciones/editar/<slug:slug>', CotizacionUpdate.as_view(), name='editar-cotizacion'),
    path('cotizaciones/detalle/<slug:slug>', CotizacionDetalle.as_view(), name='detalle-cotizacion'),
]