from rest_framework import filters, viewsets
from django_filters.rest_framework import DjangoFilterBackend

from .models import Track, Kart, Driver, Heat
from .serializers import (
    TrackSerializer, KartSerializer, DriverSerializer,
    HeatListSerializer, HeatDetailSerializer
)


class TrackViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для треков"""
    queryset = Track.objects.all()
    serializer_class = TrackSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['slug', 'name']


class DriverViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для гонщиков"""
    queryset = Driver.objects.select_related('track').all()
    serializer_class = DriverSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['track']
    search_fields = ['name', 'team']


class KartViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для картов"""
    queryset = Kart.objects.select_related('track').all()
    serializer_class = KartSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['track', 'is_active']
    search_fields = ['number']


class HeatViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для заездов"""
    queryset = Heat.objects.select_related('track').prefetch_related(
        'results__driver', 'results__kart'
    ).all()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['track', 'session_type', 'championship']
    ordering_fields = ['scheduled_at']
    ordering = ['-scheduled_at']
    search_fields = ['name', 'external_id']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return HeatDetailSerializer
        return HeatListSerializer
