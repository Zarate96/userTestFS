# Inicialización del cliente Conekta a través de la adición de la llave privada y versión del API
import conekta
import requests
import json
from http.client import HTTPSConnection
from base64 import b64encode
conekta.locale = 'es'
conekta.api_key = "key_bypUmRxRUxsqM5LbuFYzmQ"
conekta.api_version = "2.0.0"

from fletes.models import *

def checkLinkStatus():
    ordenes = Orden.objects.all()
    print(f"\n   {ordenes}")
    c = HTTPSConnection("www.google.com")
    #we need to base 64 encode it
    #and then decode it to acsii as python 3 stores it as a byte string
    #userAndPass = b64encode(b"username:password").decode("ascii")
    userAndPass = b64encode(b"key_bypUmRxRUxsqM5LbuFYzmQ").decode("ascii")
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
        print("\n  *** ORDEN TASK ***")
        print(f"   Current: {orden}")
        if orden.link_status == 'Finalized':
            print("   == Link de pago utilizado ==")
            if orden.orden_status != 'paid':
                print("   == Orden no pagada ==")
                print("\n   *** BUSCAR ORDEN PARA ACTULIZAR ESTADO ***")
                for key in ordenesConekta:
                    try:
                        if key['channel']['checkout_request_id'] == orden.link_id:
                            orden_id = key['id']
                    except:
                        pass
                if orden_id:
                    print(f"   {orden_id}")
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
                print(f"   Estado a guardar: {response['payment_status']}")
                orden.orden_status = response['payment_status']
                orden.save()
                if orden.orden_status == 'paid':
                    cotizacion = orden.cotizacion_id
                    cotizacion.estado_cotizacion = 'Pagada'
                    cotizacion.save()
                    solicitud = cotizacion.solicitud_id
                    solicitud.estado_solicitud = 'Pagada'
                    solicitud.save()
                    print(" ## Orden pagada se crea viaje #")
                    viaje = Viaje.objects.create(orden_id=orden)

        else:    
            linkId =  orden.link_id
            print("   == Link de pago no utilizado ==")
            print("\n   *** BUSCAR ORDEN PARA ACTULIZAR ESTADO ***")
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
            print(f"    Estado a guardar: {orden.link_status}")
            orden.save()