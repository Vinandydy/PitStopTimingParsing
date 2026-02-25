# backend/api/serializers.py

from rest_framework import serializers
from core.models import Track, Kart, Driver, Heat, HeatParticipation


class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        fields = ['id', 'slug', 'name']


class KartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kart
        fields = ['id', 'number', 'is_active', 'track', 'total_races', 'avg_lap_ms', 'best_lap_ms']


class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = ['id', 'external_id', 'name', 'team', 'track', 'total_races', 'avg_lap_ms', 'best_lap_ms']


class HeatSerializer(serializers.ModelSerializer):
    track_name = serializers.CharField(source='track.name', read_only=True)

    class Meta:
        model = Heat
        fields = [
            'id', 'external_id', 'name', 'scheduled_at', 'laps_count',
            'session_type', 'championship', 'track', 'track_name'
        ]


class HeatParticipationSerializer(serializers.ModelSerializer):
    """Serializer для результата — с защитой от None и удалённых объектов."""

    driver_name = serializers.SerializerMethodField()
    kart_number = serializers.SerializerMethodField()
    heat_name = serializers.CharField(source='heat.name', read_only=True)
    best_lap_formatted = serializers.SerializerMethodField()
    avg_lap_formatted = serializers.SerializerMethodField()

    class Meta:
        model = HeatParticipation
        fields = [
            'id', 'position', 'best_lap_ms', 'avg_lap_ms', 'laps_completed',
            'dev_lap_ms', 'gap_to_leader_ms', 's1_best_ms', 's1_laps',
            's2_best_ms', 's2_laps', 's3_best_ms', 's3_laps',
            'driver', 'driver_name', 'kart', 'kart_number', 'heat', 'heat_name',
            'best_lap_formatted', 'avg_lap_formatted'
        ]

    def get_driver_name(self, obj) -> str:
        """Безопасное получение имени пилота."""
        try:
            return obj.driver.name if obj.driver else '—'
        except Exception:
            return '—'

    def get_kart_number(self, obj) -> int:
        """Безопасное получение номера карта."""
        try:
            return obj.kart.number if obj.kart else 0
        except Exception:
            return 0

    def get_best_lap_formatted(self, obj) -> str:
        """Безопасное форматирование лучшего круга."""
        ms = getattr(obj, 'best_lap_ms', 0) or 0
        if ms <= 0:
            return '—'
        try:
            minutes = ms // 60000
            seconds = (ms % 60000) // 1000
            milliseconds = ms % 1000
            return f"{minutes}:{seconds:02d}.{milliseconds:03d}" if minutes else f"{seconds}.{milliseconds:03d}"
        except:
            return '—'

    def get_avg_lap_formatted(self, obj) -> str:
        """Безопасное форматирование среднего круга."""
        ms = getattr(obj, 'avg_lap_ms', 0) or 0
        if ms <= 0:
            return '—'
        try:
            minutes = ms // 60000
            seconds = (ms % 60000) // 1000
            milliseconds = ms % 1000
            return f"{minutes}:{seconds:02d}.{milliseconds:03d}" if minutes else f"{seconds}.{milliseconds:03d}"
        except:
            return '—'


class HeatDetailSerializer(serializers.ModelSerializer):
    """Детальный serializer для заезда с результатами."""

    track_name = serializers.CharField(source='track.name', read_only=True)
    # ✅ ИСПРАВЛЕНО: убран source='results' (избыточно)
    results = HeatParticipationSerializer(many=True, read_only=True)

    class Meta:
        model = Heat
        fields = [
            'id', 'external_id', 'name', 'scheduled_at', 'laps_count',
            'session_type', 'championship', 'track', 'track_name', 'results'
        ]