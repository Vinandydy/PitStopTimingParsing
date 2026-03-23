"""Тесты для парсера"""
from datetime import datetime
from unittest.mock import Mock, patch

from bs4 import BeautifulSoup
from django.test import TestCase

from parser.utils import ms_to_time, parse_datetime, time_to_ms


class UtilsTest(TestCase):
    """Тесты вспомогательных функций"""

    def test_time_to_ms(self):
        """Тест конвертации времени в миллисекунды"""
        # Стандартный формат
        self.assertEqual(time_to_ms("01:23.456"), 83456)
        self.assertEqual(time_to_ms("1:23.456"), 83456)

        # Без миллисекунд
        self.assertEqual(time_to_ms("01:23"), 83000)

        # Только секунды
        self.assertEqual(time_to_ms("45.678"), 45678)

        # Только миллисекунды
        self.assertEqual(time_to_ms("123"), 123)

        # Ошибка - возвращаем 0
        self.assertEqual(time_to_ms(""), 0)
        self.assertEqual(time_to_ms("invalid"), 0)

    def test_ms_to_time(self):
        """Тест конвертации миллисекунд в строку времени"""
        self.assertEqual(ms_to_time(83456), "01:23.456")
        self.assertEqual(ms_to_time(61000), "01:01.000")
        self.assertEqual(ms_to_time(0), "00:00.000")

    def test_parse_datetime(self):
        """Тест парсинга даты и времени"""
        result = parse_datetime("12.02.2026", "15:30")
        self.assertEqual(result.year, 2026)
        self.assertEqual(result.month, 2)
        self.assertEqual(result.day, 12)
        self.assertEqual(result.hour, 15)
        self.assertEqual(result.minute, 30)


class ParserMockTest(TestCase):
    """Тесты парсера с моками"""

    @patch('parser.utils.requests.get')
    def test_fetch_url_success(self, mock_get):
        """Тест успешного запроса"""
        from parser.utils import fetch_url

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><body><h1>Test</h1></body></html>'
        mock_response.headers = {'Content-Type': 'text/html'}
        mock_get.return_value = mock_response

        soup = fetch_url('http://test.com')
        self.assertIsNotNone(soup)
        self.assertEqual(soup.find('h1').text, 'Test')

    @patch('parser.utils.requests.get')
    def test_fetch_url_error(self, mock_get):
        """Тест ошибки запроса"""
        from parser.exceptions import NetworkError
        from parser.utils import fetch_url

        mock_get.side_effect = Exception("Connection error")

        with self.assertRaises(NetworkError):
            fetch_url('http://test.com')


class HeatParsingTest(TestCase):
    """Тесты парсинга заездов"""

    def setUp(self):
        from core.models import Track
        self.track = Track.objects.create(slug='premium', name='Premium Track')

    @patch('backend.parser.management.commands.parse_track.fetch_url')
    def test_parse_heat_details(self, mock_fetch):
        """Тест парсинга деталей заезда"""
        from backend.parser.management.commands.parse_track import Command
        from core.models import Heat

        # Создаём заезд
        heat = Heat.objects.create(
            track=self.track,
            external_id=105535,
            scheduled_at=datetime.now(),
            name="Test Heat"
        )

        # HTML с результатами заезда
        html = '''
        <html>
        <body>
            <table id="results">
                <tbody>
                    <tr>
                        <td>1</td>
                        <td><a href="/tracks/premium/drivers/159315">Иван Петров</a></td>
                        <td><a href="/tracks/premium/karts/6">6</a></td>
                        <td>01:23.456</td>
                        <td></td>
                        <td>10</td>
                    </tr>
                    <tr>
                        <td>2</td>
                        <td><a href="/tracks/premium/drivers/159316">Петр Иванов</a></td>
                        <td><a href="/tracks/premium/karts/7">7</a></td>
                        <td>01:24.789</td>
                        <td></td>
                        <td>10</td>
                    </tr>
                </tbody>
            </table>
        </body>
        </html>
        '''

        soup = BeautifulSoup(html, 'lxml')
        mock_fetch.return_value = soup

        # Вызываем метод парсинга
        command = Command()
        command._parse_heat_details(heat, 'premium')

        # Проверяем, что результаты сохранены
        self.assertEqual(heat.results.count(), 2)

        first_result = heat.results.get(position=1)
        self.assertEqual(first_result.driver.name, "Иван Петров")
        self.assertEqual(first_result.kart.number, 6)
        self.assertEqual(first_result.best_lap_ms, 83456)
        self.assertEqual(first_result.laps_completed, 10)
