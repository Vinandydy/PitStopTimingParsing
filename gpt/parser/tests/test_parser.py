"""Тесты для parser приложения."""
from unittest.mock import Mock, patch

from bs4 import BeautifulSoup
from django.test import TestCase
from django.utils import timezone

from parser.management.commands.parse_premium import Command
from parser.utils import parse_date, time_to_ms
from timing.models import Heat, Track


class UtilsTest(TestCase):
    """Тесты вспомогательных функций parser.utils."""

    def test_time_to_ms(self):
        self.assertEqual(time_to_ms("01:23.456"), 83456)
        self.assertEqual(time_to_ms("1:23.456"), 83456)
        self.assertEqual(time_to_ms("01:23"), 83000)
        self.assertEqual(time_to_ms("45.678"), 45678)
        self.assertEqual(time_to_ms("123"), 123000)
        self.assertEqual(time_to_ms(""), 0)
        self.assertEqual(time_to_ms("invalid"), 0)
        self.assertEqual(time_to_ms("+21.194 28.423"), 28423)

    def test_parse_date(self):
        dt = parse_date("Feb 17", "22:09")
        self.assertEqual(dt.month, 2)
        self.assertEqual(dt.day, 17)
        self.assertEqual(dt.hour, 22)
        self.assertEqual(dt.minute, 9)


class FetchUrlTest(TestCase):
    """Тесты fetch_url с моками requests."""

    @patch("parser.utils.requests.get")
    def test_fetch_url_success(self, mock_get):
        from parser.utils import fetch_url

        mock_response = Mock()
        mock_response.text = "<html><body><h1>OK</h1></body></html>"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        soup = fetch_url("http://test.local")
        self.assertIsNotNone(soup)
        self.assertEqual(soup.find("h1").text, "OK")

    @patch("parser.utils.requests.get")
    def test_fetch_url_error_propagates(self, mock_get):
        from parser.utils import fetch_url

        mock_get.side_effect = Exception("Connection error")
        with self.assertRaises(Exception):
            fetch_url("http://test.local")


class HeatParsingTest(TestCase):
    """Тест парсинга деталей заезда."""

    def setUp(self):
        self.track = Track.objects.create(slug="premium", name="Premium Track")

    @patch("parser.management.commands.parse_premium.fetch_url")
    def test_parse_heat_details(self, mock_fetch):
        heat = Heat.objects.create(
            track=self.track,
            external_id=105535,
            scheduled_at=timezone.now(),
            name="Test Heat",
            laps_count=0,
        )

        # Матрица, на которую рассчитан текущий parser.
        html = """
        <html><body>
          <table>
            <tr><th>Driver</th>
              <td><a href="/tracks/premium/drivers/159315">Иван Петров</a></td>
              <td><a href="/tracks/premium/drivers/159316">Петр Иванов</a></td>
            </tr>
            <tr><th>Kart</th>
              <td><a href="/tracks/premium/karts/6">6</a></td>
              <td><a href="/tracks/premium/karts/7">7</a></td>
            </tr>
            <tr><th>Best</th><td>01:23.456</td><td>01:24.789</td></tr>
            <tr><th>Avg</th><td>01:24.100</td><td>01:25.200</td></tr>
            <tr><th>Dev</th><td>0.500</td><td>0.650</td></tr>
            <tr><th>S1 laps</th><td>4l</td><td>4l</td></tr>
            <tr><th>S1 best</th><td>27.500</td><td>27.900</td></tr>
            <tr><th>S2 laps</th><td>4l</td><td>4l</td></tr>
            <tr><th>S2 best</th><td>27.800</td><td>28.100</td></tr>
            <tr><th>S3 laps</th><td>4l</td><td>4l</td></tr>
            <tr><th>S3 best</th><td>28.000</td><td>28.300</td></tr>
          </table>
        </body></html>
        """

        mock_fetch.return_value = BeautifulSoup(html, "html.parser")

        command = Command()
        count = command.parse_heat_details(heat, "premium")

        self.assertEqual(count, 2)
        self.assertEqual(heat.results.count(), 2)

        first = heat.results.get(position=1)
        self.assertEqual(first.driver.name, "Иван Петров")
        self.assertEqual(first.kart.number, 6)
        self.assertEqual(first.best_lap_ms, 83456)
        self.assertEqual(first.laps_completed, 12)
