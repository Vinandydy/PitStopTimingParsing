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
    driver_name = serializers.CharField(source='driver.name', read_only=True)
    kart_number = serializers.IntegerField(source='kart.number', read_only=True)
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

    def get_best_lap_formatted(self, obj):
        if obj.best_lap_ms:
            minutes = obj.best_lap_ms // 60000
            seconds = (obj.best_lap_ms % 60000) // 1000
            ms = obj.best_lap_ms % 1000
            return f"{minutes}:{seconds:02d}.{ms:03d}" if minutes else f"{seconds}.{ms:03d}"
        return None

    def get_avg_lap_formatted(self, obj):
        if obj.avg_lap_ms:
            minutes = obj.avg_lap_ms // 60000
            seconds = (obj.avg_lap_ms % 60000) // 1000
            ms = obj.avg_lap_ms % 1000
            return f"{minutes}:{seconds:02d}.{ms:03d}" if minutes else f"{seconds}.{ms:03d}"
        return None


class HeatDetailSerializer(serializers.ModelSerializer):
    track_name = serializers.CharField(source='track.name', read_only=True)
    results = HeatParticipationSerializer(many=True, read_only=True, source='results')

    class Meta:
        model = Heat
        fields = [
            'id', 'external_id', 'name', 'scheduled_at', 'laps_count',
            'session_type', 'championship', 'track', 'track_name', 'results'
        ]