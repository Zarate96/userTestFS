import googlemaps
import json
from django.conf import settings.base
from django.conf import settings

def getLonLat(direction):
    geocode_result = gmaps.geocode(direction)
    