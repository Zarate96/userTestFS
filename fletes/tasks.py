import datetime
from django.utils import  timezone
from datetime import  timedelta
from .models import Solicitud

def validateExpiredSolicitudes():
    solicitudes = Solicitud.objects.all()
    if solicitudes is not None:
        for solicitud in solicitudes:
            if solicitud.fecha_servicio.date() <= timezone.now().date():
                solicitud.activo = False