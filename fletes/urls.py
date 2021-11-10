from django.urls import include, path

from .views import *

urlpatterns = [
    path('solicitudes', SolicitudListView.as_view(), name='solicitudes'),
    path('solicitudes/agregar/<int:pk>', SolicitudesAgregar.as_view(), name='agregar-solicitud'),
    path('destino/agregar/<int:pk>', DestinoAgregar.as_view(), name='agregar-destino'),
]