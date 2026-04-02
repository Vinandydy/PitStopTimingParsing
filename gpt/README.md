# PitStop Timing Parsing (DeepSeek-версия в папке `gpt`)

Демонстрационная версия проекта, реализованная в каталоге `gpt` (по контексту проекта это решение на DeepSeek).

По состоянию кода на **2 апреля 2026**:
- Backend: Django + DRF (`gpt/`)
- Parser: Django management command `parse_premium`
- CLI: Typer + Rich (`gpt/cli`)
- Docker: backend + db + cli + ollama + open-webui

## 1. Соответствие ТЗ

Чек по требованиям из ТЗ:
- Практическая полезность: есть
- Средняя/высокая сложность: есть
- Минимум 7 CLI команд/подкоманд: есть
- REST API используется CLI: есть
- Описание endpoint-ов и примеров: есть в этом README

## 2. Архитектура

```text
timing.batyrshin.name
        |
        v
Django parser (parse_premium)
        |
        v
PostgreSQL
        |
        v
DRF API (/api/...)
        |
        v
CLI (timing-cli)
```

## 3. Структура версии

```text
gpt/
├── core/                    # django settings/urls
├── timing/                  # модели, сериализаторы, viewsets API
├── parser/                  # парсер timing.batyrshin.name
├── cli/
│   └── karting_cli/
│       ├── commands/        # команды Typer
│       ├── api_client.py    # клиент к DRF API
│       └── config.py        # ~/.timing-cli/config.json
├── docker-compose.yml
└── Dockerfile
```

## 4. Модель данных

Сущности (`timing/models.py`):
- `Track`
- `Kart`
- `Driver`
- `Heat`
- `HeatParticipation`

## 5. REST API (backend)

Базовый префикс: `http://localhost:8002/api`

### 5.1 Реализованные endpoint-ы

- `GET /api/tracks/`, `GET /api/tracks/{id}/`
- `GET /api/drivers/`, `GET /api/drivers/{id}/`
- `GET /api/karts/`, `GET /api/karts/{id}/`
- `GET /api/heats/`, `GET /api/heats/{id}/`
- `POST /api/ai/generate/`

### 5.2 Фильтрация

- `/drivers/`: `track`, `search`
- `/karts/`: `track`, `is_active`, `search`
- `/heats/`: `track`, `session_type`, `championship`, `ordering`, `search`

## 6. CLI команды (gpt/cli)

Запуск справки:

```bash
cd gpt/cli
python cli.py --help
```

Группы и команды:
- `tracks list`
- `drivers list|get|stats|top`
- `karts list|get|stats|active`
- `heats list|get|latest`
- `stats summary`
- `export drivers|karts|heats`
- `ai insight`
- `config`
- `version`

### 6.1 Привязка CLI -> API

| CLI команда | Вызов API |
|---|---|
| `tracks list` | `GET /tracks/` |
| `drivers list/get/top` | `GET /drivers/`, `GET /drivers/{id}/` |
| `drivers stats` | фактически `GET /drivers/{id}/` |
| `karts list/get/active` | `GET /karts/`, `GET /karts/{id}/` |
| `karts stats` | фактически `GET /karts/{id}/` |
| `heats list/get/latest` | `GET /heats/`, `GET /heats/{id}/` |
| `stats summary` | `GET /tracks/`, `/drivers/`, `/karts/`, `/heats/` |
| `export *` | те же list endpoint-ы |
| `ai insight` | `GET /heats/{id}` или `GET /drivers/{id}` + `POST /ai/generate/` |

### 6.2 Примеры CLI

```bash
# Показать треки
python cli.py tracks list

# Список заездов
python cli.py heats list --limit 20

# Детали заезда
python cli.py heats get 105535

# Топ пилотов
python cli.py drivers top --limit 10

# Экспорт в CSV
python cli.py export heats --format csv --output heats.csv

# AI-инсайт по заезду
python cli.py ai insight --heat 105535

# AI-инсайт по гонщику
python cli.py ai insight --driver 159315

# Настройка URL API
python cli.py config --set-api http://localhost:8002/api
```

## 7. Парсер

Парсер реализован как Django command:

```bash
cd gpt
python manage.py parse_premium --pages 3
```

Источники парсинга:
- `/tracks/premium/heats`
- `/tracks/premium/karts`
- `/tracks/premium/drivers`
- `/tracks/premium/heats/{id}`

## 8. Запуск через Docker

```bash
cd gpt
docker compose up --build -d
```

После запуска:
- API: `http://localhost:8002/api/`
- DB: `localhost:5433`
- Ollama: `http://localhost:11435`
- Open WebUI: `http://localhost:3001`

Парсер в контейнере backend:

```bash
docker compose exec backend python manage.py parse_premium --pages 2
```

CLI в контейнере:

```bash
docker compose exec cli python cli.py tracks list
```

## 9. Тестирование

Минимальные тесты есть для parser (`gpt/parser/tests`).

```bash
cd gpt
python manage.py test
```

## 10. Ограничения текущей реализации

- CLI-команды парсинга убраны из пользовательского интерфейса: парсер запускается только как backend-команда `manage.py parse_premium`.
- AI зависит от доступности Ollama (`ollama` контейнер и модель должны быть скачаны).
- Часть статистики (`drivers stats`, `karts stats`) считается на стороне CLI на основе базовых endpoint-ов, а не отдельного stats API.
