from django.db import models


class Track(models.Model):
    """Трек (например, Premium)"""
    slug = models.SlugField(unique=True, verbose_name='Слаг')
    name = models.CharField(max_length=100, verbose_name='Название')

    class Meta:
        verbose_name = 'Трек'
        verbose_name_plural = 'Треки'
        ordering = ['slug']

    def __str__(self):
        return f"{self.name} ({self.slug})"


class Kart(models.Model):
    """Карт"""
    track = models.ForeignKey(
        Track,
        on_delete=models.CASCADE,
        related_name='karts',
        verbose_name='Трек'
    )
    number = models.PositiveSmallIntegerField(verbose_name='Номер')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    last_seen = models.DateTimeField(auto_now=True, verbose_name='Последнее обновление')

    class Meta:
        verbose_name = 'Карт'
        verbose_name_plural = 'Карты'
        ordering = ['track', 'number']
        unique_together = ('track', 'number')

    def __str__(self):
        status = 'активен' if self.is_active else 'неактивен'
        return f"Карт #{self.number} ({status})"


class Driver(models.Model):
    """Гонщик"""
    track = models.ForeignKey(
        Track,
        on_delete=models.CASCADE,
        related_name='drivers',
        verbose_name='Трек'
    )
    external_id = models.IntegerField(unique=True, verbose_name='Внешний ID')
    name = models.CharField(max_length=200, verbose_name='Имя')
    team = models.CharField(max_length=100, blank=True, verbose_name='Команда')

    class Meta:
        verbose_name = 'Гонщик'
        verbose_name_plural = 'Гонщики'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} (ID: {self.external_id})"


class Heat(models.Model):
    """Заезд"""
    track = models.ForeignKey(
        Track,
        on_delete=models.CASCADE,
        related_name='heats',
        verbose_name='Трек'
    )
    external_id = models.IntegerField(unique=True, verbose_name='Внешний ID')
    scheduled_at = models.DateTimeField(verbose_name='Дата и время')
    name = models.CharField(max_length=200, blank=True, verbose_name='Название')
    laps_count = models.PositiveSmallIntegerField(default=0, verbose_name='Количество кругов')

    class Meta:
        verbose_name = 'Заезд'
        verbose_name_plural = 'Заезды'
        ordering = ['-scheduled_at']

    def __str__(self):
        return f"Заезд {self.external_id}: {self.name or 'Без названия'}"


class HeatParticipation(models.Model):
    """Участие в заезде"""
    heat = models.ForeignKey(
        Heat,
        on_delete=models.CASCADE,
        related_name='results',
        verbose_name='Заезд'
    )
    driver = models.ForeignKey(
        Driver,
        on_delete=models.CASCADE,
        verbose_name='Гонщик'
    )
    kart = models.ForeignKey(
        Kart,
        on_delete=models.CASCADE,
        verbose_name='Карт'
    )
    position = models.PositiveSmallIntegerField(verbose_name='Позиция')
    best_lap_ms = models.IntegerField(verbose_name='Лучший круг (мс)')
    total_time_ms = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Общее время (мс)'
    )
    laps_completed = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='Пройдено кругов'
    )

    class Meta:
        verbose_name = 'Участие в заезде'
        verbose_name_plural = 'Участия в заездах'
        ordering = ['heat', 'position']
        unique_together = ('heat', 'driver')

    def __str__(self):
        return f"{self.driver.name} - {self.position} место, лучший круг: {self.best_lap_ms}мс"