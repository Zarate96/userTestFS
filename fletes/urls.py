from django.urls import include, path

from .views import *

app_name = 'fletes'
urlpatterns = [
    path('solicitudes/', SolicitudListView.as_view(), name='solicitudes'),
    path('solicitudes/cliente', SolicitudClienteListView.as_view(), name='solicitudes-cliente'),
    path('solicitud/agregar/', SolicitudesAgregar.as_view(), name='agregar-solicitud'),
    path('solicitud/detalle/<slug:slug>', SolicitudDetalle.as_view(), name='detalle-solicitud'),
    path('solicitud/editar/<slug:slug>', SolicitudUpdate.as_view(), name='editar-solicitud'),
    path('solicitud/cancelar/<slug:slug>', SolicitudCancel.as_view(), name='cancelar-solicitud'),
    path('solicitud/eliminar/<int:id>', SolicitudDelete, name='delete-solicitud'),
    path('solicitud/finalizar/<int:id>', FinalizarSolicitud, name='finalizar-solicitud'),
    path('solicitud/agregar/destino/<int:id>', DestinoAgregar.as_view(), name='agregar-destino'),
    path('solicitud/editar/destino/<int:pk>', DestinoUpdate.as_view(), name='editar-destino'),
    path('solicitud/eliminar/destino/<int:id>', DestinoDelete, name='delete-destino'),
    path('domicilios/', DomiciliosListView.as_view(), name='domicilios'),
    path('domicilio/agregar/', DomicilioAgregar.as_view(), name='agregar-domiclio'),
    path('domicilio/editar/<slug:slug>', DomiciliosUpdate.as_view(), name='update-domicilio'),
    path('domicilio/eliminar/<slug:slug>', DomiciliosDelete, name='delete-domicilio'),
    path('cotizaciones/', CotizacionListView.as_view(), name='cotizaciones'),
    path('cotizacion/agregar/<slug:slug>', CotizacionAgregar.as_view(), name='agregar-cotizacion'),
    path('cotizaciones/eliminar/<slug:slug>', ContizacionDelete, name='delete-cotizacion'),
    path('cotizaciones/<slug:slug>', CotizacionListClienteView.as_view(), name='cotizaciones-cliente'),
    path('cotizacion/aceptar/<slug:slug>', aceptarCotizacion, name='aceptar-cotizacion'),
    path('cotizacion/confirmar/<slug:slug>', confirmarCotizacion, name='confirmar-cotizacion'),
    path('cotizacion/rechazar/<slug:slug>', rechazarCotizacion, name='rechazar-cotizacion'),
    path('cotizacion/editar/<slug:slug>', CotizacionUpdate.as_view(), name='editar-cotizacion'),
    path('cotizacion/detalle/<slug:slug>', CotizacionDetalle.as_view(), name='detalle-cotizacion'),
    path('cotizacion/cancelar/<slug:slug>', CotizacionCancel.as_view(), name='cancelar-cotizacion'),
]