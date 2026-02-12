.PHONY: lint lint-fix format test migrate server shell

# Линтинг кода
lint:
	ruff check .

# Автоисправление (импорты, лишние пробелы)
lint-fix:
	ruff check . --fix

# Форматирование кода
format:
	ruff format .

# Запуск тестов
test:
	python manage.py test

# Миграции БД
migrate:
	python manage.py migrate

# Запуск сервера
server:
	python manage.py runserver 0.0.0.0:8000

# Django shell
shell:
	python manage.py shell

# Создание суперпользователя
superuser:
	python manage.py createsuperuser

# Запуск парсера
parse:
	python manage.py parse_track premium