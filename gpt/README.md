# PitStop Timing Parsing (DeepSeek-версия в папке `gpt`)

Демонстрационная версия проекта в каталоге `gpt`.

По состоянию кода на 6 апреля 2026:
- Backend: Django + DRF (`gpt/`)
- Parser: Django management command `parse_premium`
- CLI: Typer + Rich (`gpt/cli`)

## 1. Архитектура

```text
timing.batyrshin.name
        |
        v
Django parser (parse_premium)
        |
        v
PostgreSQL (в test-режиме SQLite)
        |
        v
DRF API (/api/...)
        |
        v
CLI (python cli.py ...)
```

## 2. REST API

Базовый URL: `http://localhost:8002/api`

Основные endpoint-ы:
- `GET /api/tracks/`, `GET /api/tracks/{id}/`
- `GET /api/drivers/`, `GET /api/drivers/{id}/`
- `GET /api/karts/`, `GET /api/karts/{id}/`
- `GET /api/heats/`, `GET /api/heats/{id}/`

Фильтры:
- `/drivers/`: `track`, `search`
- `/karts/`: `track`, `is_active`, `search`
- `/heats/`: `track`, `session_type`, `championship`, `ordering`, `search`

## 3. Каталог CLI-команд (для отчета)

Базовый запуск CLI:

```bash
cd gpt/cli
python cli.py --help
```

### 3.1 Глобальные команды

| Команда | Описание | Аргументы и опции | Пример | Используемый endpoint API | Ожидаемый результат |
|---|---|---|---|---|---|
| `config` | Управление конфигурацией CLI | `--show/-s [bool, optional, default=False]`; `--set-api [str, optional, default=None]`; `--set-verbose [bool, optional, default=None]`; `--reset/-r [bool, optional, default=False]` | `python cli.py config --set-api http://localhost:8002/api` | Не использует REST API (локальная конфигурация) | Печатает текущие настройки или сохраняет их в `~/.timing-cli/config.json` |
| `version` | Показать версию CLI | Без параметров | `python cli.py version` | Не использует REST API | Вывод строки версии в консоль |

### 3.2 `tracks`

Подкоманды: `list`

| Команда | Описание | Аргументы и опции | Пример | Используемый endpoint API | Ожидаемый результат |
|---|---|---|---|---|---|
| `tracks list` | Список треков | Нет параметров | `python cli.py tracks list` | `GET /tracks/` | Таблица треков в консоли, в конце `Всего: N треков` |

### 3.3 `drivers`

Подкоманды: `list`, `get`, `stats`, `top`

| Команда | Описание | Аргументы и опции | Пример | Используемый endpoint API | Ожидаемый результат |
|---|---|---|---|---|---|
| `drivers list` | Список гонщиков | `--track/-t [int, optional, default=None]`; `--search/-s [str, optional, default=None]`; `--limit/-l [int, optional, default=20]` | `python cli.py drivers list --track 1 --limit 50` | `GET /drivers/?track=1&page=1&page_size=20` | Таблица гонщиков, в конце `Показано: N гонщиков` |
| `drivers get` | Карточка гонщика | `driver_id [int, required]` | `python cli.py drivers get 159315` | `GET /drivers/159315/` | Детальная статистика гонщика в консоли |
| `drivers stats` | Статистика гонщика (синоним `get`) | `driver_id [int, required]` | `python cli.py drivers stats 159315` | `GET /drivers/159315/` | Детальная статистика гонщика |
| `drivers top` | Топ гонщиков по числу заездов | `--limit/-l [int, optional, default=10]`; `--track/-t [int, optional, default=None]` | `python cli.py drivers top --limit 10 --track 1` | `GET /drivers/?track=1&page=1&page_size=20` | Таблица топа после сортировки в CLI |

### 3.4 `karts`

Подкоманды: `list`, `get`, `stats`, `active`

| Команда | Описание | Аргументы и опции | Пример | Используемый endpoint API | Ожидаемый результат |
|---|---|---|---|---|---|
| `karts list` | Список картов | `--track/-t [int, optional, default=None]`; `--active/-a [bool, optional, default=False]`; `--limit/-l [int, optional, default=20]` | `python cli.py karts list --active --limit 30` | `GET /karts/?is_active=true&page=1&page_size=20` | Таблица картов, в конце `Показано: N картов` |
| `karts get` | Карточка карта | `kart_id [int, required]` | `python cli.py karts get 42` | `GET /karts/42/` | Детальная информация о карте |
| `karts stats` | Статистика карта | `kart_id [int, required]`; `--period/-p [str, optional, default=all, значения: all/7d/30d]` | `python cli.py karts stats 42 --period 30d` | `GET /karts/42/` | Карточка статистики карта |
| `karts active` | Только активные карты | `--track/-t [int, optional, default=None]` | `python cli.py karts active --track 1` | `GET /karts/?track=1&is_active=true&page=1&page_size=20` | Таблица активных картов |

### 3.5 `heats`

Подкоманды: `list`, `get`, `latest`

| Команда | Описание | Аргументы и опции | Пример | Используемый endpoint API | Ожидаемый результат |
|---|---|---|---|---|---|
| `heats list` | Список заездов | `--track/-t [int, optional, default=None]`; `--type/-y [str, optional, default=None]`; `--champ/-c [str, optional, default=None]`; `--limit/-l [int, optional, default=20]` | `python cli.py heats list --type Race --limit 20` | `GET /heats/?session_type=Race&page=1&page_size=20` | Таблица заездов, в конце `Показано: N заездов` |
| `heats get` | Детали заезда | `heat_id [int, required]` | `python cli.py heats get 105535` | `GET /heats/105535/` | Подробная карточка заезда |
| `heats latest` | Последние заезды | `--track/-t [int, optional, default=None]`; `--limit/-l [int, optional, default=10]` | `python cli.py heats latest --limit 5` | `GET /heats/?page=1&page_size=20` | Таблица последних N записей |

### 3.6 `stats`

Подкоманды: `summary`

| Команда | Описание | Аргументы и опции | Пример | Используемый endpoint API | Ожидаемый результат |
|---|---|---|---|---|---|
| `stats summary` | Сводная статистика по данным API | `--track/-t [int, optional, default=None]` | `python cli.py stats summary --track 1` | `GET /tracks/`, `GET /drivers/?track=1`, `GET /karts/?track=1`, `GET /heats/?track=1` | Rich-таблица с агрегатами (кол-во заездов/гонщиков/картов, лучший круг) |

### 3.7 `export`

Подкоманды: `drivers`, `karts`, `heats`

| Команда | Описание | Аргументы и опции | Пример | Используемый endpoint API | Ожидаемый результат |
|---|---|---|---|---|---|
| `export drivers` | Экспорт гонщиков | `--format/-f [str, optional, default=json, значения: json/csv]`; `--output/-o [path, optional, default=None]`; `--track/-t [int, optional, default=None]` | `python cli.py export drivers --format csv --output drivers.csv` | `GET /drivers/?page=1&page_size=20` | Если `--output` задан: создается файл. Иначе данные печатаются в консоль |
| `export karts` | Экспорт картов | `--format/-f [str, optional, default=json, значения: json/csv]`; `--output/-o [path, optional, default=None]`; `--track/-t [int, optional, default=None]`; `--active/-a [bool, optional, default=False]` | `python cli.py export karts --active --output karts.json` | `GET /karts/?is_active=true&page=1&page_size=20` | Создается файл `karts.json` или вывод в консоль |
| `export heats` | Экспорт заездов | `--format/-f [str, optional, default=json, значения: json/csv]`; `--output/-o [path, optional, default=None]`; `--track/-t [int, optional, default=None]`; `--limit/-l [int, optional, default=100]` | `python cli.py export heats --format csv --limit 200 --output heats.csv` | `GET /heats/?page=1&page_size=20` | Создается файл `heats.csv` или вывод в консоль |

## 4. Парсер (backend-команда)

Команда: `python manage.py parse_premium`

- Описание: парсит треки, гонщиков, карты и заезды с `timing.batyrshin.name`.
- Основные опции: `--pages [int, optional, default зависит от команды]`.
- Пример:

```bash
cd gpt
python manage.py parse_premium --pages 3
```

- Ожидаемый результат: данные сохраняются в БД, логи выводятся в консоль.

## 5. Технические детали

- Библиотеки:
  - Backend: `django`, `djangorestframework`, `django-filter`, `drf-spectacular`, `psycopg2-binary`, `beautifulsoup4`, `lxml`, `requests`.
  - CLI: `typer`, `rich`, `httpx`, `python-dotenv`, `pydantic`, `tabulate`.
  - Тесты: `pytest`, `pytest-django`, `pytest-cov`.

- Предполагаемая структура проекта:

```text
gpt/
├── core/                         # settings, urls
├── timing/                       # модели и DRF API
├── parser/                       # парсер + management commands
├── cli/
│   ├── cli.py                    # entry point
│   ├── karting_cli/main.py       # root Typer app
│   ├── karting_cli/commands/     # группы команд
│   └── tests/                    # CLI unit tests
└── requirements.txt
```

- Обработка ошибок:
  - сетевые и HTTP ошибки в CLI обрабатываются в `APIClient` (`httpx.HTTPStatusError`, `httpx.RequestError`), ошибка печатается в консоль, команда завершает выполнение без traceback;
  - при отсутствии данных команды выводят человекочитаемое сообщение (`не найдено`, `нет данных для экспорта`).

- Конфигурация:
  - Backend: `.env` (через `load_dotenv`), ключи `DB_*`, `DJANGO_*`;
  - CLI: env-переменные `TIMING_API_URL`, `TIMING_TIMEOUT`, `TIMING_VERBOSE`, `TIMING_PAGE_SIZE`;
  - локальный конфиг CLI: `~/.timing-cli/config.json`.

- Логирование:
  - Backend: `LOGGING` в `core/settings.py`, вывод в консоль (уровень root `INFO`, logger `parser` -> `DEBUG`);
  - CLI: debug-вывод только при `verbose=true` в конфиге.

- Тесты:
  - Backend: `python manage.py test` -> 5 тестов (`OK`);
  - CLI: `pytest tests -vv` в `gpt/cli` -> 25 passed.

## 6. Запуск тестов

```bash
# backend
cd gpt
python manage.py test

# cli
cd gpt/cli
pytest tests -vv
```
