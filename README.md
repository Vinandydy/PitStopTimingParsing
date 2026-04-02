# PitStop Timing Parsing: сравнение двух реализаций CLI + REST API

Репозиторий содержит две независимые реализации одного ТЗ:
- `qwen/` — версия, сгенерированная в сессиях с Qwen
- `gpt/` — версия, сгенерированная в сессиях с DeepSeek (папка исторически названа `gpt`)

Цель проекта: парсить статистику картинга с `timing.batyrshin.name`, сохранять в PostgreSQL, отдавать через REST API и работать с данными через CLI.

## 1. Что требовало ТЗ

По презентации `Улучшенное_задание v2.pptx` ключевые критерии:
- минимум 7 CLI команд/подкоманд
- обязательное использование REST API
- описание endpoint-ов в README
- документация запуска, тестов, структуры
- сравнительный анализ двух ИИ-решений

Обе версии формально закрывают базовые пункты ТЗ.

## 2. Структура репозитория

```text
.
├── qwen/      # Реализация 1 (Qwen)
├── gpt/       # Реализация 2 (DeepSeek)
├── pyproject.toml
└── README.md  # этот файл
```

## 3. Источник данных

Обе версии парсят один и тот же сайт:
- `https://timing.batyrshin.name/tracks/premium/heats`
- `https://timing.batyrshin.name/tracks/premium/karts`
- `https://timing.batyrshin.name/tracks/premium/drivers`
- `https://timing.batyrshin.name/tracks/premium/heats/{id}`

## 4. Сравнение решений (главное для защиты)

### 4.1 Краткий итог

- **Qwen-версия** сильнее в API-документации и в пользовательском CLI-опыте (включая AI-команду).
- **DeepSeek-версия** проще и чище по структуре базового CRUD-потока, но часть CLI-функций ссылается на несуществующие API endpoint-ы.

### 4.2 Таблица различий

| Критерий | `qwen/` | `gpt/` (DeepSeek) |
|---|---|---|
| REST API сущности | tracks, karts, drivers, heats, results, ai | tracks, karts, drivers, heats |
| Документация API | есть `/api/schema/` и `/api/docs/` | swagger не подключен |
| CLI групп (>=7) | 7 групп: heats/drivers/results/stats/export/tracks/ai | 6 групп: tracks/drivers/karts/heats/stats/export + config/version |
| AI-интеграция в CLI | есть (`ai analyze-heat`) через `POST /ai/generate/` | нет |
| Парсер | `manage.py parse_track` | `manage.py parse_premium` |
| Тесты CLI | есть отдельный набор тестов в `qwen/cli/tests` | минимальные тесты, в основном parser |
| Согласованность CLI<->API | частично: есть расхождения имен фильтров | частично: есть команды, требующие несуществующие endpoint-ы |
| Порог входа | выше (больше функционала) | ниже (проще старт) |

### 4.3 Критические различия по связке CLI/API

`qwen/`:
- сильная сторона: покрыты `results` и `ai` endpoint-ы, есть богатый вывод в CLI;
- слабая сторона: часть CLI-параметров не идеально совпадает с backend filterset-полями.

`gpt/`:
- сильная сторона: стабильный read-only CRUD по `tracks/drivers/karts/heats`;
- слабая сторона: нет endpoint-ов `results`, поэтому часть аналитики собирается через агрегирование базовых endpoint-ов;
- слабая сторона: запуск парсера вынесен только в backend (`manage.py parse_premium`), без пользовательской CLI-команды.

## 5. Какие CLI команды реализованы и с какими API связаны

### 5.1 Qwen (`qwen/cli`)

| Команда | API |
|---|---|
| `karting tracks list` | `GET /tracks/` |
| `karting drivers list/detail` | `GET /drivers/`, `GET /drivers/{id}/` |
| `karting heats list/detail` | `GET /heats/`, `GET /heats/{id}/` |
| `karting results list` | `GET /results/` |
| `karting stats driver` | `GET /drivers/{id}/` + `GET /results/` |
| `karting export csv/json` | `GET /results/` |
| `karting ai analyze-heat` | `GET /heats/{id}/` + `POST /ai/generate/` |

### 5.2 DeepSeek (`gpt/cli`)

| Команда | API |
|---|---|
| `timing-cli tracks list` | `GET /tracks/` |
| `timing-cli drivers list/get/top` | `GET /drivers/`, `GET /drivers/{id}/` |
| `timing-cli karts list/get/active` | `GET /karts/`, `GET /karts/{id}/` |
| `timing-cli heats list/get/latest` | `GET /heats/`, `GET /heats/{id}/` |
| `timing-cli stats summary` | агрегирует `GET /tracks,/drivers,/karts,/heats` |
| `timing-cli export *` | использует list endpoint-ы |

## 6. Рекомендации для презентации

1. Показывать `qwen/` как более "витринную" версию (docs + AI + results endpoint + CLI UX).
2. Показывать `gpt/` как более минималистичную версию CRUD/парсинга.
3. Честно отметить технические расхождения CLI/API в обеих версиях и предложить план доводки.
4. Делать акцент, что оба решения соответствуют обязательному требованию REST API и минимуму CLI-команд.

## 7. Где смотреть детали

- Подробное README версии Qwen: `qwen/README.md`
- Подробное README версии DeepSeek: `gpt/README.md`
