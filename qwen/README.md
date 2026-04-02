# PitStop Timing Parsing (Qwen-версия)

Демонстрационная версия проекта, собранная в ветке `qwen`: парсинг данных с `timing.batyrshin.name`, хранение в PostgreSQL, выдача через Django REST API и работа через CLI.

По состоянию кода на **2 апреля 2026**:
- Backend: Django + DRF (`qwen/backend`)
- Parser: Django management command `parse_track`
- CLI: Typer + Rich (`qwen/cli`)
- AI: endpoint `POST /api/ai/generate/` (Ollama)

## 1. Соответствие ТЗ

Чек по требованиям из ТЗ:
- Практическая полезность: есть (парсинг и аналитика картинга)
- Средняя/высокая сложность: есть (парсер + API + CLI + AI)
- Срок 4-6 недель: архитектура этому соответствует
- Минимум 7 CLI команд/подкоманд: есть
- Обязательный REST API: есть
- README с endpoint-ами и примерами: есть в этом документе

## 2. Архитектура

```text
timing.batyrshin.name
        |
        v
Django parser (parse_track)
        |
        v
PostgreSQL
        |
        v
Django REST API (/api/...)
        |
        v
CLI (python -m karting ...)
        |
        v
AI proxy (/api/ai/generate/ -> Ollama)
```

## 3. Структура версии

```text
qwen/
├── backend/
│   ├── api/            # DRF viewsets, serializers, filters
│   ├── core/           # модели данных
│   ├── parser/         # парсер timing.batyrshin.name
│   └── config/         # settings/urls/asgi/wsgi
├── cli/
│   └── karting/
│       ├── commands/   # команды Typer
│       ├── client.py   # API клиент
│       └── config.py   # конфиг ~/.karting/config.json
├── docker-compose.yml
└── Dockerfile
```

## 4. Модель данных

Основные сущности (`backend/core/models.py`):
- `Track`
- `Kart`
- `Driver`
- `Heat`
- `HeatParticipation` (результаты пилота в заезде)

## 5. REST API (backend)

Базовый префикс: `http://localhost:8000/api`

### 5.1 Реализованные endpoint-ы

- `GET /api/tracks/`, `GET /api/tracks/{id}/`
- `GET /api/karts/`, `GET /api/karts/{id}/`
- `GET /api/drivers/`, `GET /api/drivers/{id}/`
- `GET /api/heats/`, `GET /api/heats/{id}/`
- `GET /api/results/`, `GET /api/results/{id}/`
- `POST /api/ai/generate/`

Дополнительно:
- `GET /api/schema/` (OpenAPI)
- `GET /api/docs/` (Swagger UI)

### 5.2 Ключевые фильтры

- `/api/heats/`: `session_type`, `championship`, `name`, даты (через filterset)
- `/api/results/`: `driver`, `kart`, `heat`, `track`, `position`, диапазоны
- `/api/drivers/`, `/api/karts/`: поиск/фильтры DRF

## 6. CLI команды (qwen/cli)

Запуск справки:

```bash
cd qwen/cli
python -m karting --help
```

Группы CLI (7 штук):
- `heats`
- `drivers`
- `results`
- `stats`
- `export`
- `tracks`
- `ai`

Глобальные опции:
- `--version`
- `--verbose`
- `--api-url`

### 6.1 Привязка CLI -> API

| CLI команда | Вызов API |
|---|---|
| `karting tracks list` | `GET /tracks/` |
| `karting drivers list` | `GET /drivers/` |
| `karting drivers detail <id>` | `GET /drivers/{id}/` |
| `karting heats list` | `GET /heats/` |
| `karting heats detail <id>` | `GET /heats/{id}/` |
| `karting results list` | `GET /results/` |
| `karting stats driver <id>` | `GET /drivers/{id}/` + `GET /results/?driver=...` |
| `karting export csv/json` | `GET /results/` |
| `karting ai analyze-heat <id>` | `GET /heats/{id}/` + `POST /ai/generate/` |

### 6.2 Примеры CLI

```bash
# Список треков
python -m karting tracks list --limit 20

# Детали заезда
python -m karting heats detail 105535

# Результаты конкретного заезда
python -m karting results list --heat 105535 --limit 20

# Статистика пилота
python -m karting stats driver 159315

# AI-анализ заезда
python -m karting ai analyze-heat 105535 --focus strategy

# Экспорт
python -m karting export csv --heat 105535 --output race_105535.csv
```

## 7. Парсер

Парсер реализован как Django command:

```bash
cd qwen/backend
python manage.py parse_track --pages 3
```

Что парсится:
- `/tracks/premium/karts`
- `/tracks/premium/drivers`
- `/tracks/premium/heats?page=N`
- `/tracks/premium/heats/{id}`

## 8. Запуск через Docker

```bash
cd qwen
docker compose up --build -d
```

После запуска:
- API: `http://localhost:8000/api/`
- Swagger: `http://localhost:8000/api/docs/`
- Ollama: `http://localhost:11434`
- Open WebUI: `http://localhost:3000`

Парсинг в контейнере backend:

```bash
docker compose exec backend python manage.py parse_track --pages 2
```

CLI в контейнере:

```bash
docker compose exec cli python -m karting tracks list
```

## 9. Тестирование

Есть тесты для:
- parser (`backend/parser/tests`)
- cli (`cli/tests`, включая команды)

Запуск:

```bash
# backend
cd qwen/backend
python manage.py test

# cli
cd qwen/cli
pytest -v
```

## 10. Ограничения текущей реализации

- CLI и backend не везде используют одинаковые имена фильтров (часть фильтров требует донастройки).
- Парсер вызывается только с backend-стороны (в CLI нет отдельной команды запуска парсинга).
- AI зависит от доступности контейнера `ollama`.
