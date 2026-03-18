import django_filters

from core.models import Heat, HeatParticipation


class HeatFilter(django_filters.FilterSet):
    track = django_filters.CharFilter(field_name='track__slug')
    session_type = django_filters.CharFilter(lookup_expr='iexact')
    championship = django_filters.CharFilter(lookup_expr='iexact')
    date_from = django_filters.DateFilter(field_name='scheduled_at', lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name='scheduled_at', lookup_expr='lte')
    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Heat
        fields = ['track', 'session_type', 'championship', 'name']


class HeatParticipationFilter(django_filters.FilterSet):
    driver = django_filters.CharFilter(field_name='driver__name', lookup_expr='icontains')
    kart = django_filters.NumberFilter(field_name='kart__number')
    heat = django_filters.NumberFilter(field_name='heat__external_id')
    track = django_filters.CharFilter(field_name='heat__track__slug')
    date_from = django_filters.DateFilter(field_name='heat__scheduled_at', lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name='heat__scheduled_at', lookup_expr='lte')
    position = django_filters.NumberFilter()
    position__lte = django_filters.NumberFilter(field_name='position', lookup_expr='lte')
    position__gte = django_filters.NumberFilter(field_name='position', lookup_expr='gte')

    class Meta:
        model = HeatParticipation
        fields = ['driver', 'kart', 'heat', 'track', 'position']
