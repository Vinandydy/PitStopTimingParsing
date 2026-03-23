from rest_framework import serializers
from .models import Track, Kart, Driver, Heat, HeatParticipation


class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        fields = ['id', 'slug', 'name', 'created_at']


class KartSerializer(serializers.ModelSerializer):
    track_name = serializers.CharField(source='track.name', read_only=True)

    class Meta:
        model = Kart
        fields = [
            'id', 'number', 'track', 'track_name', 'is_active',
            'avg_lap_ms', 'best_lap_ms', 'total_races', 'created_at'
        ]


class DriverSerializer(serializers.ModelSerializer):
    track_name = serializers.CharField(source='track.name', read_only=True)

    class Meta:
        model = Driver
        fields = [
            'id', 'external_id', 'name', 'team', 'track', 'track_name',
            'avg_lap_ms', 'best_lap_ms', 'total_races', 'created_at'
        ]


class HeatParticipationSerializer(serializers.ModelSerializer):
    driver_name = serializers.CharField(source='driver.name', read_only=True)
    driver_id = serializers.IntegerField(source='driver.external_id', read_only=True)
    kart_number = serializers.IntegerField(source='kart.number', read_only=True)

    class Meta:
        model = HeatParticipation
        fields = [
            'position', 'driver', 'driver_id', 'driver_name',
            'kart', 'kart_number', 'laps_completed', 'best_lap_ms',
            'avg_lap_ms', 'dev_lap_ms', 'gap_to_leader_ms',
            's1_laps', 's1_best_ms', 's2_laps', 's2_best_ms',
            's3_laps', 's3_best_ms'
        ]


class HeatListSerializer(serializers.ModelSerializer):
    track_name = serializers.CharField(source='track.name', read_only=True)
    participants_count = serializers.IntegerField(source='results.count', read_only=True)

    class Meta:
        model = Heat
        fields = [
            'id', 'external_id', 'track', 'track_name', 'name',
            'scheduled_at', 'session_type', 'championship',
            'laps_count', 'participants_count'
        ]


class HeatDetailSerializer(serializers.ModelSerializer):
    track_name = serializers.CharField(source='track.name', read_only=True)
    results = HeatParticipationSerializer(many=True, read_only=True)

    class Meta:
        model = Heat
        fields = [
            'id', 'external_id', 'track', 'track_name', 'name',
            'scheduled_at', 'laps_count', 'session_type',
            'championship', 'results', 'raw_data', 'created_at'
        ]