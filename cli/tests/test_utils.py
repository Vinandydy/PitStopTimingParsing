"""Тесты утилит CLI."""

import pytest

from karting.utils import ms_to_formatted, format_date, session_icon, format_position


class TestMsToFormatted:
    """Тесты функции ms_to_formatted."""

    def test_ms_without_minutes(self):
        """Тест миллисекунд без минут."""
        assert ms_to_formatted(28423) == "28.423"
        assert ms_to_formatted(59999) == "59.999"

    def test_ms_with_minutes(self):
        """Тест миллисекунд с минутами."""
        assert ms_to_formatted(60000) == "1:00.000"
        assert ms_to_formatted(83456) == "1:23.456"
        assert ms_to_formatted(120000) == "2:00.000"

    def test_ms_zero(self):
        """Тест нуля."""
        assert ms_to_formatted(0) == "—"

    def test_ms_negative(self):
        """Тест отрицательного значения."""
        assert ms_to_formatted(-100) == "—"

    def test_ms_none(self):
        """Тест None."""
        assert ms_to_formatted(None) == "—"


class TestFormatDate:
    """Тесты функции format_date."""

    def test_format_date_short(self):
        """Тест короткого формата."""
        result = format_date("2026-02-24T22:20:00+03:00", short=True)
        assert "24.02" in result
        assert "22:20" in result

    def test_format_date_long(self):
        """Тест полного формата."""
        result = format_date("2026-02-24T22:20:00+03:00", short=False)
        assert "24" in result
        assert "2026" in result

    def test_format_date_invalid(self):
        """Тест невалидной даты."""
        result = format_date("invalid-date")
        assert result == "invalid-date"  # Возвращает как есть


class TestSessionIcon:
    """Тесты функции session_icon."""

    def test_race_icon(self):
        """Тест иконки Race."""
        assert session_icon("Race") == "🏁"

    def test_qualification_icon(self):
        """Тест иконки Qualification."""
        assert session_icon("Qualification") == "⏱️"

    def test_practice_icon(self):
        """Тест иконки Practice."""
        assert session_icon("Practice") == "🔧"

    def test_unknown_icon(self):
        """Тест неизвестного типа."""
        assert session_icon("Unknown") == "❓"
        assert session_icon("") == "❓"
        assert session_icon(None) == "❓"


class TestFormatPosition:
    """Тесты функции format_position."""

    def test_position_1(self):
        """Тест первой позиции."""
        assert format_position(1) == "1st"

    def test_position_2(self):
        """Тест второй позиции."""
        assert format_position(2) == "2nd"

    def test_position_3(self):
        """Тест третьей позиции."""
        assert format_position(3) == "3rd"

    def test_position_4(self):
        """Тест четвёртой позиции."""
        assert format_position(4) == "4th"

    def test_position_11_12_13(self):
        """Тест позиций 11, 12, 13 (особый случай)."""
        assert format_position(11) == "11th"
        assert format_position(12) == "12th"
        assert format_position(13) == "13th"

    def test_position_21_22_23(self):
        """Тест позиций 21, 22, 23."""
        assert format_position(21) == "21st"
        assert format_position(22) == "22nd"
        assert format_position(23) == "23rd"

    def test_position_zero(self):
        """Тест нулевой позиции."""
        assert format_position(0) == "—"

    def test_position_none(self):
        """Тест None."""
        assert format_position(None) == "—"