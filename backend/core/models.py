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
    number = models.PositiveSmallIntegerField()
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    # Статистика
    avg_lap_ms = models.IntegerField(default=0)  # Средний круг на этом карте
    best_lap_ms = models.IntegerField(default=0)  # Лучший круг на этом карте
    total_races = models.IntegerField(default=0)  # Всего заездов

    class Meta:
        verbose_name = 'Карт'
        verbose_name_plural = 'Карты'
        ordering = ['track', 'number']
        unique_together = ('track', 'number')

    def __str__(self):
        status = 'активен' if self.is_active else 'неактивен'
        return f"Карт #{self.number} ({status})"


class Driver(models.Model):
    external_id = models.IntegerField(unique=True)  # ID с сайта
    name = models.CharField(max_length=200)
    team = models.CharField(max_length=100, blank=True)
    track = models.ForeignKey(Track, on_delete=models.CASCADE)

    avg_lap_ms = models.IntegerField(default=0)  # Средний круг за всё время
    best_lap_ms = models.IntegerField(default=0)  # Лучший круг за всё время
    total_races = models.IntegerField(default=0)  # Всего заездов

    class Meta:
        verbose_name = 'Гонщик'
        verbose_name_plural = 'Гонщики'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} (ID: {self.external_id})"


class Heat(models.Model):
    external_id = models.IntegerField(unique=True)  # ID с сайта
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    scheduled_at = models.DateTimeField()  # Дата и время
    laps_count = models.PositiveSmallIntegerField()  # Общее количество кругов
    session_type = models.CharField(max_length=50, blank=True)  # "Race", "Qualification", "Practice"
    championship = models.CharField(max_length=50, blank=True)  # "ГГ2026", "OPEN2025"

    class Meta:
        verbose_name = 'Заезд'
        verbose_name_plural = 'Заезды'
        ordering = ['-scheduled_at']

    def __str__(self):
        return f"Заезд {self.external_id}: {self.name or 'Без названия'}"


class HeatParticipation(models.Model):
    heat = models.ForeignKey(Heat, on_delete=models.CASCADE, related_name='results')
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    kart = models.ForeignKey(Kart, on_delete=models.CASCADE)

    # Результаты заезда
    position = models.PositiveSmallIntegerField()  # Итоговая позиция
    laps_completed = models.PositiveSmallIntegerField()  # Пройдено кругов

    # Статистика кругов (в миллисекундах)
    best_lap_ms = models.IntegerField(default=0)  # Лучший круг
    avg_lap_ms = models.IntegerField(default=0)  # Среднее время круга
    dev_lap_ms = models.IntegerField(default=0)  # Стандартное отклонение

    # Сессии (если применимо)
    s1_laps = models.PositiveSmallIntegerField(default=0)
    s1_best_ms = models.IntegerField(default=0)
    s2_laps = models.PositiveSmallIntegerField(default=0)
    s2_best_ms = models.IntegerField(default=0)
    s3_laps = models.PositiveSmallIntegerField(default=0)
    s3_best_ms = models.IntegerField(default=0)

    # Отставание от лидера (в миллисекундах)
    gap_to_leader_ms = models.IntegerField(default=0)

    class Meta:
        unique_together = ('heat', 'driver')

    def __str__(self):
        return f"{self.driver.name} - {self.position} место, лучший круг: {self.best_lap_ms}мс"