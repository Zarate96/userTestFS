import django_filters
from django_filters import DateRangeFilter,DateFilter
from .models import Transportista, Verifaciones, Verifaciones_encierros

class TransportistasFilter(django_filters.FilterSet):

    class Meta:
        model = Transportista
        fields = ('es_verificado','es_validado','es_activo')

class VerificacionesFilter(django_filters.FilterSet):

    class Meta:
        model = Verifaciones
        fields = ('estado_verificacion',)

class VerificacionesEncierrosFilter(django_filters.FilterSet):

    class Meta:
        model = Verifaciones_encierros
        fields = ('estado_verificacion',)