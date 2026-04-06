# PitStop Timing Parsing (Qwen-версия)

Демонстрационная версия проекта в каталоге `qwen`: парсинг данных с `timing.batyrshin.name`, хранение в БД, REST API и CLI.

По состоянию кода на 6 апреля 2026:
- Backend: Django + DRF (`qwen/backend`)
- Parser: Django management command `parse_track`
- CLI: Typer + Rich (`qwen/cli`)
- AI: endpoint `POST /api/ai/generate/`

## 1. Архитектура

```text
timing.batyrshin.name
        |
        v
Django parser (parse_track)
        |
        v
PostgreSQL (в test-режиме SQLite)
        |
        v
Django REST API (/api/...)
        |
        v
CLI (karting ...)
        |
        v
AI proxy (/api/ai/generate/)
```

## 2. REST API

Базовый URL: `http://localhost:8000/api`

Основные endpoint-ы:
- `GET /api/tracks/`, `GET /api/tracks/{id}/`
- `GET /api/drivers/`, `GET /api/drivers/{id}/`
- `GET /api/heats/`, `GET /api/heats/{id}/`
- `GET /api/results/`, `GET /api/results/{id}/`
- `POST /api/ai/generate/`

Документация API:
- `GET /api/schema/`
- `GET /api/docs/`

## 3. Каталог CLI-команд (для отчета)

Базовый запуск CLI:

```bash
cd qwen/cli
karting --help
```

Глобальные опции (доступны перед любой командой):
- `--version/-V [bool, optional, default=False]`
- `--verbose/-v [bool, optional, default=False, env=KARTING_VERBOSE]`
- `--api-url [str, optional, default=None, env=KARTING_API_URL]`

### 3.1 `tracks`

Подкоманды: `list`

| Команда | Описание | Аргументы и опции | Пример | Используемый endpoint API | Ожидаемый результат |
|---|---|---|---|---|---|
| `tracks list` | Показать список треков | `--search/-s [str, optional, default=None]`; `--limit/-l [int, optional, default=50, диапазон 1..200]`; `--format/-F [str, optional, default из config.default_format, значения: table/json/csv]` | `karting tracks list --search premium --limit 20` | `GET /tracks/?search=premium&limit=20` | Таблица треков или JSON в консоль |

### 3.2 `drivers`

Подкоманды: `list`, `detail`

| Команда | Описание | Аргументы и опции | Пример | Используемый endpoint API | Ожидаемый результат |
|---|---|---|---|---|---|
| `drivers list` | Список пилотов | `--track/-t [int, optional, default=None]`; `--team/-T [str, optional, default=None]`; `--search/-s [str, optional, default=None]`; `--limit/-l [int, optional, default=50, диапазон 1..200]`; `--format/-F [str, optional, default из config]` | `karting drivers list --track 1 --search Иван --limit 30` | `GET /drivers/?track=1&search=Иван&limit=30` | Таблица пилотов или JSON |
| `drivers detail` | Детали пилота | `driver_id [int, required]`; `--format/-F [str, optional, default из config]` | `karting drivers detail 159315` | `GET /drivers/159315/` | Карточка пилота/JSON; при 404 выход с кодом 5 |

### 3.3 `heats`

Подкоманды: `list`, `detail`

| Команда | Описание | Аргументы и опции | Пример | Используемый endpoint API | Ожидаемый результат |
|---|---|---|---|---|---|
| `heats list` | Список заездов с фильтрами | `--track/-t [int, optional]`; `--type/-T [str, optional]`; `--champ/-c [str, optional]`; `--from/-f [str YYYY-MM-DD, optional]`; `--to/-d [str YYYY-MM-DD, optional]`; `--search/-s [str, optional]`; `--limit/-l [int, optional, default=50, диапазон 1..200]`; `--format/-F [str, optional]` | `karting heats list --type Race --from 2026-03-01 --to 2026-03-31 --limit 25` | `GET /heats/?session_type=Race&scheduled_at_from=2026-03-01&scheduled_at_to=2026-03-31&ordering=-scheduled_at&limit=25` | Таблица заездов или JSON |
| `heats detail` | Детальная информация о заезде + результаты | `heat_id [int, required]`; `--format/-F [str, optional]` | `karting heats detail 105535` | `GET /heats/105535/` | Карточка заезда, мета и таблица top-10 результатов; при 404 выход с кодом 5 |

### 3.4 `results`

Подкоманды: `list`

| Команда | Описание | Аргументы и опции | Пример | Используемый endpoint API | Ожидаемый результат |
|---|---|---|---|---|---|
| `results list` | Список результатов заездов | `--heat/-H [int, optional]`; `--driver/-D [int, optional]`; `--kart/-K [int, optional]`; `--position/-p [int, optional]`; `--limit/-l [int, optional, default=50, диапазон 1..200]`; `--format/-F [str, optional]` | `karting results list --heat 105535 --limit 20` | `GET /results/?heat=105535&ordering=position&limit=20` | Таблица результатов или JSON |

### 3.5 `stats`

Подкоманды: `driver`

| Команда | Описание | Аргументы и опции | Пример | Используемый endpoint API | Ожидаемый результат |
|---|---|---|---|---|---|
| `stats driver` | Расчет статистики пилота из результатов | `driver_id [int, required]`; `--period/-p [str, optional, default=all, значения: all/7d/30d/90d]`; `--format/-F [str, optional]` | `karting stats driver 159315 --period 30d` | `GET /drivers/159315/` + `GET /results/?driver=159315&limit=500&ordering=-heat__scheduled_at` | Карточка статистики и таблица последних заездов, или JSON |

### 3.6 `export`

Подкоманды: `csv`, `json`

| Команда | Описание | Аргументы и опции | Пример | Используемый endpoint API | Ожидаемый результат |
|---|---|---|---|---|---|
| `export csv` | Экспорт результатов в CSV | `--heat/-H [int, optional]`; `--driver/-D [int, optional]`; `--output/-o [str, optional, default=export.csv]` | `karting export csv --heat 105535 --output race_105535.csv` | `GET /results/?heat=105535&limit=500` | Создается CSV-файл с колонками `position`, `driver_name`, `kart_number`, `best_lap_formatted`, `avg_lap_formatted`, `laps_completed` |
| `export json` | Экспорт результатов в JSON | `--heat/-H [int, optional]`; `--driver/-D [int, optional]`; `--output/-o [str, optional, default=export.json]` | `karting export json --driver 159315 --output driver_159315.json` | `GET /results/?driver=159315&limit=500` | Создается JSON-файл с массивом результатов |

### 3.7 `ai`

Подкоманды: `analyze-heat`

| Команда | Описание | Аргументы и опции | Пример | Используемый endpoint API | Ожидаемый результат |
|---|---|---|---|---|---|
| `ai analyze-heat` | AI-анализ конкретного заезда | `heat_id [int, required]`; `--focus/-f [str, optional, default=all, значения: all/podium/strategy/stability/advice]`; `--model/-m [str, optional, default=qwen2.5:7b]` | `karting ai analyze-heat 105535 --focus strategy --model qwen2.5:7b` | `GET /heats/105535/` + `POST /ai/generate/` | В консоль выводится markdown-панель с анализом, плюс `tokens_used` и длительность (если backend вернул) |

## 4. Парсер (backend-команда)

Команда: `python manage.py parse_track`

- Описание: парсит справочники и заезды трека `premium`, затем детальные результаты заездов.
- Опции: `--pages [int, optional, default=1]`.
- Пример:

```bash
cd qwen/backend
python manage.py parse_track --pages 3
```

- Ожидаемый результат: данные обновляются в БД, прогресс парсинга печатается в stdout.

## 5. Технические детали

- Библиотеки:
  - Backend: `django`, `djangorestframework`, `django-filter`, `django-cors-headers`, `drf-spectacular`, `beautifulsoup4`, `lxml`, `psycopg2-binary`.
  - CLI: `typer`, `rich`, `httpx`, `pydantic`, `python-decouple`.
  - Тесты: `pytest`, `pytest-cov`, `respx`, `pytest-asyncio`.

- Предполагаемая структура проекта:

```text
qwen/
├── backend/
│   ├── api/                     # DRF viewsets/serializers/filters
│   ├── core/                    # модели
│   ├── parser/                  # парсер + management command
│   ├── config/                  # settings/urls
│   └── manage.py
├── cli/
│   ├── karting/__main__.py      # entry point
│   ├── karting/client.py        # HTTP клиент
│   ├── karting/commands/        # Typer команды
│   ├── karting/config.py        # CLI config
│   └── tests/                   # unit tests
└── docker-compose.yml
```

- Обработка ошибок:
  - CLI: собственные исключения `CLIError`, `APIConnectionError`, `APIResourceNotFound`, `ValidationError`;
  - для `404` используется exit code `5`, для сетевых ошибок - `3`, для API-ошибок - `2`;
  - в командах есть валидация лимитов (`1..200`) через `typer.BadParameter`.

- Конфигурация:
  - Backend: `.env` (`SECRET_KEY`, `DEBUG`, `DB_*`, `LOG_LEVEL`);
  - CLI: env `KARTING_API_URL`, `KARTING_API_TOKEN`, `KARTING_VERBOSE`;
  - локальный конфиг CLI: `~/.karting/config.json`;
  - кэш GET-ответов CLI: `~/.karting/cache`.

- Логирование:
  - Backend: консоль + файл `qwen/backend/logs/django.log` (в test-режиме файловый handler отключается);
  - CLI: статусные сообщения Rich + optional verbose/кэш-индикаторы.

- Тесты:
  - Backend: `python manage.py test` -> 11 тестов (`OK`);
  - CLI: `pytest tests -vv` -> 62 passed.

## 6. Запуск тестов

```bash
# backend
cd qwen/backend
python manage.py test

# cli
cd qwen/cli
pytest tests -vv
```
