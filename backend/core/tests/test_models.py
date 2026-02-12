from django.test import TestCase
from core.models import Track, Kart, Driver, Heat, HeatParticipation


class TrackModelTest(TestCase):
    """Тесты модели Track"""

    def test_track_creation(self):
        track = Track.objects.create(slug="premium", name="Premium Track")
        self.assertEqual(str(track), "Premium Track (premium)")
        self.assertEqual(track.slug, "premium")
        self.assertEqual(track.name, "Premium Track")


class KartModelTest(TestCase):
    """Тесты модели Kart"""

    def setUp(self):
        self.track = Track.objects.create(slug="premium", name="Premium Track")

    def test_kart_creation(self):
        kart = Kart.objects.create(track=self.track, number=6, is_active=True)
        self.assertEqual(kart.number, 6)
        self.assertTrue(kart.is_active)
        self.assertEqual(str(kart), "Карт #6 (активен)")

    def test_kart_unique_constraint(self):
        Kart.objects.create(track=self.track, number=6, is_active=True)
        with self.assertRaises(Exception):
            Kart.objects.create(track=self.track, number=6, is_active=False)


class DriverModelTest(TestCase):
    """Тесты модели Driver"""

    def setUp(self):
        self.track = Track.objects.create(slug="premium", name="Premium Track")

    def test_driver_creation(self):
        driver = Driver.objects.create(
            track=self.track,
            external_id=159315,
            name="Иван Петров",
            team="Team Alpha"
        )
        self.assertEqual(driver.name, "Иван Петров")
        self.assertEqual(driver.external_id, 159315)
        self.assertEqual(driver.team, "Team Alpha")
        self.assertEqual(str(driver), "Иван Петров (ID: 159315)")


class HeatModelTest(TestCase):
    """Тесты модели Heat"""

    def setUp(self):
        self.track = Track.objects.create(slug="premium", name="Premium Track")

    def test_heat_creation(self):
        from datetime import datetime
        heat = Heat.objects.create(
            track=self.track,
            external_id=105535,
            scheduled_at=datetime(2026, 2, 10, 15, 30),
            name="Вечерний заезд",
            laps_count=10
        )
        self.assertEqual(heat.external_id, 105535)
        self.assertEqual(heat.name, "Вечерний заезд")
        self.assertEqual(heat.laps_count, 10)
        self.assertEqual(str(heat), "Заезд 105535: Вечерний заезд")


class HeatParticipationModelTest(TestCase):
    """Тесты модели HeatParticipation"""

    def setUp(self):
        self.track = Track.objects.create(slug="premium", name="Premium Track")
        self.driver = Driver.objects.create(
            track=self.track,
            external_id=159315,
            name="Иван Петров"
        )
        self.kart = Kart.objects.create(track=self.track, number=6, is_active=True)
        self.heat = Heat.objects.create(
            track=self.track,
            external_id=105535,
            scheduled_at="2026-02-10 15:30:00"
        )

    def test_participation_creation(self):
        participation = HeatParticipation.objects.create(
            heat=self.heat,
            driver=self.driver,
            kart=self.kart,
            position=1,
            best_lap_ms=83456,
            total_time_ms=500000,
            laps_completed=10
        )
        self.assertEqual(participation.position, 1)
        self.assertEqual(participation.best_lap_ms, 83456)
        self.assertEqual(str(participation), "Иван Петров - 1 место, лучший круг: 83456мс")