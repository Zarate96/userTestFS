import django_filters
from django_filters import DateRangeFilter,DateFilter
from .models import Solicitud

class SolicitudesFilter(django_filters.FilterSet):
    fecha_servicio = django_filters.DateRangeFilter()

    class Meta:
        model = Solicitud
        fields = ('estado_origen','fecha_servicio')