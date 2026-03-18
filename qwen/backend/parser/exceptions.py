"""Исключения для парсера"""


class ParserError(Exception):
    """Базовое исключение парсера"""
    pass


class ParsingError(ParserError):
    """Ошибка при парсинге данных"""
    pass


class NetworkError(ParserError):
    """Ошибка сети при запросе"""
    pass


class DataValidationError(ParserError):
    """Ошибка валидации данных"""
    pass
