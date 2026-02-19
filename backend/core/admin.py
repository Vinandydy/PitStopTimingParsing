# backend/core/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Avg, Min, Max, Count
from .models import Track, Kart, Driver, Heat, HeatParticipation


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ('slug', 'name')
    search_fields = ('slug', 'name')


class HeatParticipationInline(admin.TabularInline):
    """Отображение результатов заезда в деталях заезда"""
    model = HeatParticipation
    extra = 0
    can_delete = False
    show_change_link = True

    fields = ('position', 'driver_link', 'kart_link', 'best_lap_display', 'avg_lap_display',
              'laps_completed', 's1_laps', 's2_laps', 's3_laps')
    readonly_fields = ('position', 'driver_link', 'kart_link', 'best_lap_display', 'avg_lap_display',
                       'laps_completed', 's1_laps', 's2_laps', 's3_laps')

    def driver_link(self, obj):
        return format_html(
            '<a href="/admin/core/driver/{}/change/">{}</a>',
            obj.driver.id,
            obj.driver.name
        )

    driver_link.short_description = 'Гонщик'

    def kart_link(self, obj):
        return format_html(
            '<a href="/admin/core/kart/{}/change/">{}</a>',
            obj.kart.id,
            f"Карт #{obj.kart.number}"
        )

    kart_link.short_description = 'Карт'

    def best_lap_display(self, obj):
        if obj.best_lap_ms:
            minutes = obj.best_lap_ms // 60000
            seconds = (obj.best_lap_ms % 60000) // 1000
            ms = obj.best_lap_ms % 1000
            return f"{minutes}:{seconds:02d}.{ms:03d}" if minutes else f"{seconds}.{ms:03d}"
        return "-"

    best_lap_display.short_description = 'Лучший круг'

    def avg_lap_display(self, obj):
        if obj.avg_lap_ms:
            minutes = obj.avg_lap_ms // 60000
            seconds = (obj.avg_lap_ms % 60000) // 1000
            ms = obj.avg_lap_ms % 1000
            return f"{minutes}:{seconds:02d}.{ms:03d}" if minutes else f"{seconds}.{ms:03d}"
        return "-"

    avg_lap_display.short_description = 'Среднее время'


@admin.register(Heat)
class HeatAdmin(admin.ModelAdmin):
    list_display = ('external_id', 'name', 'track', 'scheduled_at', 'session_type',
                    'championship', 'laps_count', 'participants_count', 'best_lap_display')
    list_filter = ('track', 'session_type', 'championship', 'scheduled_at')
    search_fields = ('name', 'external_id')
    date_hierarchy = 'scheduled_at'
    inlines = [HeatParticipationInline]

    def participants_count(self, obj):
        return obj.results.count()

    participants_count.short_description = 'Участников'

    def best_lap_display(self, obj):
        best = obj.results.aggregate(Min('best_lap_ms'))['best_lap_ms__min']
        if best:
            minutes = best // 60000
            seconds = (best % 60000) // 1000
            ms = best % 1000
            return f"{minutes}:{seconds:02d}.{ms:03d}" if minutes else f"{seconds}.{ms:03d}"
        return "-"

    best_lap_display.short_description = 'Лучший круг заезда'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('track').prefetch_related('results')


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('external_id', 'name', 'team', 'track', 'total_races', 'avg_lap_display', 'best_lap_display')
    list_filter = ('track', 'team')
    search_fields = ('name', 'external_id', 'team')
    readonly_fields = ('total_races', 'avg_lap_ms', 'best_lap_ms')

    def total_races(self, obj):
        return obj.heatparticipation_set.count()

    total_races.short_description = 'Заездов'

    def avg_lap_display(self, obj):
        if obj.avg_lap_ms:
            minutes = obj.avg_lap_ms // 60000
            seconds = (obj.avg_lap_ms % 60000) // 1000
            ms = obj.avg_lap_ms % 1000
            return f"{minutes}:{seconds:02d}.{ms:03d}" if minutes else f"{seconds}.{ms:03d}"
        return "-"

    avg_lap_display.short_description = 'Средний круг'

    def best_lap_display(self, obj):
        if obj.best_lap_ms:
            minutes = obj.best_lap_ms // 60000
            seconds = (obj.best_lap_ms % 60000) // 1000
            ms = obj.best_lap_ms % 1000
            return f"{minutes}:{seconds:02d}.{ms:03d}" if minutes else f"{seconds}.{ms:03d}"
        return "-"

    best_lap_display.short_description = 'Лучший круг'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('track')


@admin.register(Kart)
class KartAdmin(admin.ModelAdmin):
    list_display = ('number', 'track', 'is_active', 'total_races', 'avg_lap_display', 'best_lap_display')
    list_filter = ('track', 'is_active')
    search_fields = ('number',)
    readonly_fields = ('total_races', 'avg_lap_ms', 'best_lap_ms')

    def total_races(self, obj):
        return obj.heatparticipation_set.count()

    total_races.short_description = 'Заездов'

    def avg_lap_display(self, obj):
        if obj.avg_lap_ms:
            minutes = obj.avg_lap_ms // 60000
            seconds = (obj.avg_lap_ms % 60000) // 1000
            ms = obj.avg_lap_ms % 1000
            return f"{minutes}:{seconds:02d}.{ms:03d}" if minutes else f"{seconds}.{ms:03d}"
        return "-"

    avg_lap_display.short_description = 'Средний круг'

    def best_lap_display(self, obj):
        if obj.best_lap_ms:
            minutes = obj.best_lap_ms // 60000
            seconds = (obj.best_lap_ms % 60000) // 1000
            ms = obj.best_lap_ms % 1000
            return f"{minutes}:{seconds:02d}.{ms:03d}" if minutes else f"{seconds}.{ms:03d}"
        return "-"

    best_lap_display.short_description = 'Лучший круг'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('track')


@admin.register(HeatParticipation)
class HeatParticipationAdmin(admin.ModelAdmin):
    list_display = ('heat_link', 'driver_link', 'kart_number', 'position', 'best_lap_display',
                    'avg_lap_display', 'laps_completed', 'session_info')
    list_filter = ('heat__track', 'heat__session_type', 'heat__championship', 'position')
    search_fields = ('driver__name', 'heat__name', 'kart__number')
    readonly_fields = ('heat', 'driver', 'kart', 'position', 'best_lap_ms', 'avg_lap_ms',
                       'laps_completed', 'dev_lap_ms', 's1_best_ms', 's1_laps',
                       's2_best_ms', 's2_laps', 's3_best_ms', 's3_laps', 'gap_to_leader_ms')

    def heat_link(self, obj):
        return format_html(
            '<a href="/admin/core/heat/{}/change/">{}</a>',
            obj.heat.id,
            obj.heat.name[:50] + '...' if len(obj.heat.name) > 50 else obj.heat.name
        )

    heat_link.short_description = 'Заезд'

    def driver_link(self, obj):
        return format_html(
            '<a href="/admin/core/driver/{}/change/">{}</a>',
            obj.driver.id,
            obj.driver.name
        )

    driver_link.short_description = 'Гонщик'

    def kart_number(self, obj):
        return obj.kart.number

    kart_number.short_description = 'Карт'

    def best_lap_display(self, obj):
        if obj.best_lap_ms:
            minutes = obj.best_lap_ms // 60000
            seconds = (obj.best_lap_ms % 60000) // 1000
            ms = obj.best_lap_ms % 1000
            return f"{minutes}:{seconds:02d}.{ms:03d}" if minutes else f"{seconds}.{ms:03d}"
        return "-"

    best_lap_display.short_description = 'Лучший круг'

    def avg_lap_display(self, obj):
        if obj.avg_lap_ms:
            minutes = obj.avg_lap_ms // 60000
            seconds = (obj.avg_lap_ms % 60000) // 1000
            ms = obj.avg_lap_ms % 1000
            return f"{minutes}:{seconds:02d}.{ms:03d}" if minutes else f"{seconds}.{ms:03d}"
        return "-"

    avg_lap_display.short_description = 'Среднее время'

    def session_info(self, obj):
        sessions = []
        if obj.s1_laps:
            sessions.append(f"S1: {obj.s1_laps}к")
        if obj.s2_laps:
            sessions.append(f"S2: {obj.s2_laps}к")
        if obj.s3_laps:
            sessions.append(f"S3: {obj.s3_laps}к")
        return " | ".join(sessions) if sessions else "-"

    session_info.short_description = 'Сессии'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('heat', 'driver', 'kart', 'heat__track')