from django.contrib import admin
from django.db.models import Min, Avg
from django.utils.html import format_html
from django.urls import reverse

from .models import Track, Kart, Driver, Heat, HeatParticipation


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    """Админка для треков"""
    list_display = ('slug', 'name', 'created_at')
    search_fields = ('slug', 'name')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at',)


@admin.register(Kart)
class KartAdmin(admin.ModelAdmin):
    """Админка для картов"""
    list_display = ('number', 'track', 'is_active', 'total_races', 'avg_lap_display', 'best_lap_display')
    list_filter = ('track', 'is_active')
    search_fields = ('number',)
    list_editable = ('is_active',)
    readonly_fields = ('total_races', 'avg_lap_ms', 'best_lap_ms', 'created_at', 'updated_at')

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


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    """Админка для гонщиков"""
    list_display = ('external_id', 'name', 'team', 'track', 'total_races', 'avg_lap_display', 'best_lap_display')
    list_filter = ('track',)
    search_fields = ('name', 'external_id', 'team')
    readonly_fields = ('total_races', 'avg_lap_ms', 'best_lap_ms', 'created_at', 'updated_at')

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


class HeatParticipationInline(admin.TabularInline):
    """Инлайн для отображения результатов в заезде"""
    model = HeatParticipation
    extra = 0
    can_delete = False
    show_change_link = True
    verbose_name = 'Результат'
    verbose_name_plural = 'Результаты заезда'

    fields = (
        'position', 'driver_link', 'kart_link', 'best_lap_display',
        'avg_lap_display', 'laps_completed', 'gap_to_leader_ms',
        's1_laps', 's1_best_ms', 's2_laps', 's2_best_ms', 's3_laps', 's3_best_ms'
    )
    readonly_fields = (
        'position', 'driver_link', 'kart_link', 'best_lap_display',
        'avg_lap_display', 'laps_completed', 'gap_to_leader_ms',
        's1_laps', 's1_best_ms', 's2_laps', 's2_best_ms', 's3_laps', 's3_best_ms'
    )

    def driver_link(self, obj):
        url = reverse('admin:timing_driver_change', args=[obj.driver.id])
        return format_html('<a href="{}">{}</a>', url, obj.driver.name)
    driver_link.short_description = 'Гонщик'

    def kart_link(self, obj):
        url = reverse('admin:timing_kart_change', args=[obj.kart.id])
        return format_html('<a href="{}">Карт #{}</a>', url, obj.kart.number)
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
    """Админка для заездов"""
    list_display = (
        'external_id', 'name', 'track', 'scheduled_at', 'session_type',
        'championship', 'laps_count', 'participants_count', 'best_lap_display'
    )
    list_filter = ('track', 'session_type', 'championship')
    search_fields = ('name', 'external_id')
    date_hierarchy = 'scheduled_at'
    inlines = [HeatParticipationInline]
    readonly_fields = ('created_at', 'updated_at')

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


@admin.register(HeatParticipation)
class HeatParticipationAdmin(admin.ModelAdmin):
    """Админка для участий в заездах"""
    list_display = (
        'heat_link', 'driver_link', 'kart_number', 'position',
        'best_lap_display', 'avg_lap_display', 'laps_completed',
        'gap_to_leader_display', 'session_info'
    )
    list_filter = ('heat__track', 'heat__session_type', 'heat__championship', 'position')
    search_fields = ('driver__name', 'heat__name', 'kart__number')
    readonly_fields = (
        'heat', 'driver', 'kart', 'position', 'best_lap_ms', 'avg_lap_ms',
        'dev_lap_ms', 'laps_completed', 'gap_to_leader_ms',
        's1_laps', 's1_best_ms', 's2_laps', 's2_best_ms',
        's3_laps', 's3_best_ms', 'created_at', 'updated_at'
    )

    def heat_link(self, obj):
        url = reverse('admin:timing_heat_change', args=[obj.heat.id])
        name = obj.heat.name[:50] + '...' if len(obj.heat.name) > 50 else obj.heat.name
        return format_html('<a href="{}">{}</a>', url, name)
    heat_link.short_description = 'Заезд'

    def driver_link(self, obj):
        url = reverse('admin:timing_driver_change', args=[obj.driver.id])
        return format_html('<a href="{}">{}</a>', url, obj.driver.name)
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

    def gap_to_leader_display(self, obj):
        if obj.gap_to_leader_ms:
            minutes = obj.gap_to_leader_ms // 60000
            seconds = (obj.gap_to_leader_ms % 60000) // 1000
            ms = obj.gap_to_leader_ms % 1000
            return f"{minutes}:{seconds:02d}.{ms:03d}" if minutes else f"{seconds}.{ms:03d}"
        return "-"
    gap_to_leader_display.short_description = 'Отставание'

    def session_info(self, obj):
        sessions = []
        if obj.s1_laps:
            best_time = self._format_time(obj.s1_best_ms)
            sessions.append(f"S1: {obj.s1_laps}к ({best_time})")
        if obj.s2_laps:
            best_time = self._format_time(obj.s2_best_ms)
            sessions.append(f"S2: {obj.s2_laps}к ({best_time})")
        if obj.s3_laps:
            best_time = self._format_time(obj.s3_best_ms)
            sessions.append(f"S3: {obj.s3_laps}к ({best_time})")
        return " | ".join(sessions) if sessions else "-"
    session_info.short_description = 'Сессии'

    def _format_time(self, ms):
        if ms:
            minutes = ms // 60000
            seconds = (ms % 60000) // 1000
            ms_rest = ms % 1000
            return f"{minutes}:{seconds:02d}.{ms_rest:03d}" if minutes else f"{seconds}.{ms_rest:03d}"
        return "-"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('heat', 'driver', 'kart', 'heat__track')