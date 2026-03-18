"""Кастомные исключения CLI."""

from rich.console import Console

console = Console(stderr=True)


class CLIError(Exception):
    """Базовое исключение CLI."""
    exit_code: int = 1
    message: str

    def __init__(self, message: str, exit_code: int = 1, details: str | None = None):
        self.message = message
        self.exit_code = exit_code
        self.details = details
        super().__init__(message)

    def display(self) -> None:
        console.print(f"[bold red]❌ Ошибка:[/bold red] {self.message}")
        if self.details:
            console.print(f"[dim]{self.details}[/dim]")


class APIConnectionError(CLIError):
    def __init__(self, url: str, original_error: Exception | None = None):
        msg = f"Не удалось подключиться к API: {url}"
        details = "Проверьте: 1) запущен ли сервер 2) корректен ли URL"
        if original_error:
            details += f" ({type(original_error).__name__})"
        super().__init__(msg, exit_code=3, details=details)


class APIAuthError(CLIError):
    def __init__(self, hint: str | None = None):
        msg = "Отказано в доступе к API"
        details = hint or "Выполните авторизацию"
        super().__init__(msg, exit_code=4, details=details)


class APIResourceNotFound(CLIError):
    def __init__(self, resource: str, identifier: str = ""):
        msg = f"{resource} не найден" + (f" ({identifier})" if identifier else "")
        super().__init__(msg, exit_code=5)


class ValidationError(CLIError):
    def __init__(self, field: str, message: str, value: str | None = None):
        msg = f"Некорректное значение для --{field}: {message}"
        details = f"Получено: {value!r}" if value else None
        super().__init__(msg, exit_code=2, details=details)