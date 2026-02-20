from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from core.models import Track, Kart, Driver, Heat, HeatParticipation
from .serializers import (
    TrackSerializer, KartSerializer, DriverSerializer,
    HeatSerializer, HeatDetailSerializer, HeatParticipationSerializer
)
from .filters import HeatFilter, HeatParticipationFilter


class TrackViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Track.objects.all()
    serializer_class = TrackSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'slug']


class KartViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Kart.objects.select_related('track').all()
    serializer_class = KartSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['track', 'is_active']
    search_fields = ['number']
    ordering_fields = ['number', 'total_races', 'best_lap_ms']


class DriverViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Driver.objects.select_related('track').all()
    serializer_class = DriverSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['track', 'team']
    search_fields = ['name']
    ordering_fields = ['name', 'total_races', 'best_lap_ms']


class HeatViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Heat.objects.select_related('track').prefetch_related('results__driver', 'results__kart').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = HeatFilter
    search_fields = ['name', 'championship']
    ordering_fields = ['scheduled_at', 'name']
    ordering = ['-scheduled_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return HeatDetailSerializer
        return HeatSerializer


class HeatParticipationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = HeatParticipation.objects.select_related(
        'heat', 'driver', 'kart', 'heat__track'
    ).all()
    serializer_class = HeatParticipationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = HeatParticipationFilter
    search_fields = ['driver__name']
    ordering_fields = ['position', 'best_lap_ms', 'avg_lap_ms', 'heat__scheduled_at']
    ordering = ['position']