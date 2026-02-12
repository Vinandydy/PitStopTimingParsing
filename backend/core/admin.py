from django.contrib import admin
from .models import Track, Kart, Driver, Heat, HeatParticipation


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ('slug', 'name')
    search_fields = ('slug', 'name')


@admin.register(Kart)
class KartAdmin(admin.ModelAdmin):
    list_display = ('track', 'number', 'is_active', 'last_seen')
    list_filter = ('track', 'is_active')
    search_fields = ('number',)
    list_editable = ('is_active',)


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('name', 'external_id', 'team', 'track')
    list_filter = ('track', 'team')
    search_fields = ('name', 'external_id')


@admin.register(Heat)
class HeatAdmin(admin.ModelAdmin):
    list_display = ('external_id', 'track', 'scheduled_at', 'name', 'laps_count')
    list_filter = ('track', 'scheduled_at')
    search_fields = ('external_id', 'name')
    date_hierarchy = 'scheduled_at'


@admin.register(HeatParticipation)
class HeatParticipationAdmin(admin.ModelAdmin):
    list_display = ('heat', 'driver', 'kart', 'position', 'best_lap_ms', 'laps_completed')
    list_filter = ('heat__track', 'position')
    search_fields = ('driver__name',)
    raw_id_fields = ('heat', 'driver', 'kart')
    list_select_related = ('heat', 'driver', 'kart')