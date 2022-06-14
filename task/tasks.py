# Inicialización del cliente Conekta a través de la adición de la llave privada y versión del API
import conekta
import requests
import json
import threading
from base64 import b64encode
from datetime import datetime
from datetime import timedelta
from datetime import date as todaysDate
from django.utils import timezone
from django.conf import settings
from http.client import HTTPSConnection
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

conekta.locale = 'es'
conekta.api_key = settings.SANDBOX_PRIVADA_CONEKTA 
conekta.api_version = "2.0.0"

from fletes.models import *

class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()

def checkLinkStatus():
    ordenes = Orden.objects.all()
    print(f"\n   {ordenes}")
    c = HTTPSConnection("www.google.com")
    #we need to base 64 encode it
    #and then decode it to acsii as python 3 stores it as a byte string
    #userAndPass = b64encode(b"username:password").decode("ascii")
    api_key = bytes(settings.SANDBOX_PRIVADA_CONEKTA, encoding='utf-8')
    userAndPass = b64encode(api_key).decode("ascii")
    headers = { 'Authorization' : 'Basic %s' %  userAndPass }
    #then connect
    c.request('GET', '/', headers=headers)
    #get the response back
    res = c.getresponse()
    # at this point you could check the status etc
    # this gets the page text
    data = res.read()

    url = "https://api.conekta.io/orders"

    headers = {
        "Accept": "application/vnd.conekta-v2.0.0+json",
        "Content-Type": "application/json",
        'Accept-Charset': 'UTF-8',
        'Authorization' : 'Basic %s' %  userAndPass,
    }

    response = requests.request("GET", url, headers=headers, data=data)
    response = response.json()
    ordenesConekta = response["data"]
    # print(linkId)
    # link = linkId

    for orden in ordenes:
        # print("\n  *** ORDEN TASK ***")
        # print(f"   Current: {orden}")
        if orden.link_status == 'Finalized':
            #print("   == Link de pago utilizado ==")
            if orden.orden_status != 'paid':
                #print("   == Orden no pagada ==")
                #print("\n   *** BUSCAR ORDEN PARA ACTULIZAR ESTADO ***")
                for key in ordenesConekta:
                    try:
                        if key['channel']['checkout_request_id'] == orden.link_id:
                            orden_id = key['id']
                    except:
                        pass
                if orden_id:
                    #print(f"   {orden_id}")
                    orden.orden_id = orden_id
                else:
                    print("Data no encontrada")
        
                url = f"https://api.conekta.io/orders/{orden_id}"

                headers = {
                    "Accept": "application/vnd.conekta-v2.0.0+json",
                    "Content-Type": "application/json",
                    'Accept-Charset': 'UTF-8',
                    'Authorization' : 'Basic %s' %  userAndPass,
                }
                response = requests.request("GET", url, headers=headers, data=data)
                response = response.json()
                #print(f"   Estado a guardar: {response['payment_status']}")
                orden.orden_status = response['payment_status']
                orden.save()
                if orden.orden_status == 'paid':
                    cotizacion = orden.cotizacion_id
                    cotizacion.estado_cotizacion = 'Pagada'
                    cotizacion.save()
                    solicitud = cotizacion.solicitud_id
                    solicitud.estado_solicitud = 'Pagada'
                    solicitud.save()
                    #print(" ## Orden pagada se crea viaje #")
                    viaje = Viaje.objects.create(orden_id=orden)

        else:    
            linkId =  orden.link_id
            #print("   == Link de pago no utilizado ==")
            #print("\n   *** BUSCAR ORDEN PARA ACTULIZAR ESTADO ***")
            url = "https://api.conekta.io/checkouts/" + linkId

            headers = {
                "Accept": "application/vnd.conekta-v2.0.0+json",
                "Content-Type": "application/json",
                'Accept-Charset': 'UTF-8',
                'Authorization' : 'Basic %s' %  userAndPass,
            }

            response = requests.request("GET", url, headers=headers, data=data)
            response = response.json()

            response_status = response['status']
            orden.link_status = response_status
            #print(f"    Estado a guardar: {orden.link_status}")
            orden.save()

def verificarSolicitudesVencidas():
    solicitudes = Solicitud.objects.all()
    today = datetime.now().timestamp()
    if solicitudes:
        for solicitud in solicitudes:
            fechaServicio = datetime.timestamp(solicitud.fecha_servicio)
            #Desactivar solicitudes y cotizaciones con 7 días de vencimiento
            if solicitud.estado_solicitud == 'Vencida':
                id_cotizaciones = []
                fecha_vencidas = solicitud.fecha_servicio + timedelta(days=6)
                fecha_vencidas_timestamp = datetime.timestamp(fecha_vencidas)
                if fecha_vencidas_timestamp < today:
                    cotizaciones = Cotizacion.objects.filter(solicitud_id=solicitud)
                    for cotizacion in cotizaciones:
                        id_cotizaciones.append(cotizacion.id)
                    Cotizacion.objects.filter(id__in=id_cotizaciones).update(activo=False)
                    solicitud.activo = False
                    solicitud.save()
            #Pasar a vencidas solicitudes con fecha de servicio vencidas
            if solicitud.estado_solicitud != 'Vencida' or solicitud.estado_solicitud != 'Pagada': 
                if today > fechaServicio:
                    id_cotizaciones = []
                    cotizaciones = Cotizacion.objects.filter(solicitud_id=solicitud)
                    for cotizacion in cotizaciones:
                        id_cotizaciones.append(cotizacion.id)
                    Cotizacion.objects.filter(id__in=id_cotizaciones).update(estado_cotizacion='Solicitud cancelada')
                    solicitud.motivo_cancelacion = 'Solicitud cancelada por fecha de servicio vencida'
                    solicitud.estado_solicitud = 'Vencida'
                    solicitud.save()

def envioRecordatorioConfirmacion():
    cotizaciones = Cotizacion.objects.filter(estado_cotizacion='Aceptada')
    print(cotizaciones)
    current_site = settings.SITE_URL
    for cotizacion in cotizaciones:
        transportista = cotizacion.transportista_id.user
        if cotizacion.correo_recordatorio < 3:
            solicitud = cotizacion.solicitud_id
            email_subject = 'Recordario de confirmación para cotización'
            email_body = render_to_string('fletes/mails/recordatorioConfirmacionEmail.html', {
                'user': transportista,
                'domain': current_site,
                'cotizacion': cotizacion,
                'solicitud': solicitud
            })
            email = EmailMessage(subject=email_subject, body=email_body,
                        from_email=settings.EMAIL_FROM_USER,
                        to=[transportista.email]
                        )
            if not settings.TESTING:
                cotizacion.correo_recordatorio = cotizacion.correo_recordatorio + 1
                cotizacion.save()
                EmailThread(email).start()
        else:
            #notificar a cliente cancelación de cotización
            transportista.penalizaciones = transportista.penalizaciones + 1
            cotizacion.estado_cotizacion = 'Cancelada'
            cotizacion.motivo_cancelacion = 'Transportista no confirmo cotización'
            cotizacion.save()

def envioRecordatorioPago():
    current_site = settings.SITE_URL
    ordenes = Orden.objects.all()
    for orden in ordenes:
        if orden.orden_status != 'paid' and orden.correo_recordatorio < 3:
            cliente = orden.cotizacion_id.solicitud_id.cliente_id.user
            solicitud = orden.cotizacion_id.solicitud_id
            cotizacion = orden.cotizacion_id
            email_subject = 'Recordario de pago'
            link = orden.link_url
            email_body = render_to_string('fletes/mails/recordatorioPago.html', {
                'user': cliente,
                'domain': current_site,
                'cotizacion': cotizacion,
                'solicitud': solicitud,
                'link': link
            })
            email = EmailMessage(subject=email_subject, body=email_body,
                        from_email=settings.EMAIL_FROM_USER,
                        to=[cliente.email]
                        )
            if not settings.TESTING:
                orden.correo_recordatorio = orden.correo_recordatorio + 1
                orden.save()
                EmailThread(email).start()