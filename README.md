# PitStop Timing Parsing: сравнение двух реализаций CLI + REST API

Репозиторий содержит две независимые реализации одного ТЗ:
- `qwen/` - версия, сгенерированная в сессиях с Qwen
- `gpt/` - версия, сгенерированная в сессиях с DeepSeek (папка исторически названа `gpt`)

Цель проекта: парсить статистику картинга с `timing.batyrshin.name`, сохранять в PostgreSQL, отдавать через REST API и работать с данными через CLI.

## 1. Что требовало ТЗ

Ключевые критерии:
- минимум 7 CLI команд/подкоманд;
- обязательное использование REST API;
- описание endpoint-ов и примеров вызова команд;
- описание аргументов/опций и ожидаемого результата;
- техническое описание (библиотеки, структура, ошибки, конфигурация, логирование, тесты).

Обе версии формально закрывают базовые требования.

## 2. Где смотреть полное описание команд

Полные каталоги команд по шаблону из отчета (команда, подкоманды, аргументы/опции с типами и default, пример, endpoint API, ожидаемый результат) вынесены в README каждой реализации:

- DeepSeek-версия: `gpt/README.md`
- Qwen-версия: `qwen/README.md`

## 3. Быстрый прогон всех тестов

Из корня проекта:

```bash
source .venv/bin/activate && (cd gpt && python manage.py test) && (cd gpt/cli && pytest tests -vv)
source .venv/bin/activate && (cd qwen/backend && python manage.py test) && (cd qwen/cli && pytest tests -vv)
```

Фактический статус на 6 апреля 2026:
- `gpt` backend: 5 тестов, `OK`
- `gpt/cli`: 25 passed
- `qwen/backend`: 11 тестов, `OK`
- `qwen/cli`: 62 passed

## 4. Краткое сравнение

| Критерий | `qwen/` | `gpt/` (DeepSeek) |
|---|---|---|
| REST API сущности | tracks, drivers, heats, results, ai | tracks, drivers, karts, heats |
| CLI группы | heats, drivers, results, stats, export, tracks, ai | tracks, drivers, karts, heats, stats, export, config, version |
| Swagger/OpenAPI | есть (`/api/schema/`, `/api/docs/`) | есть DRF API без отдельного Swagger UI в README |
| AI команда в CLI | есть (`ai analyze-heat`) | нет |
| Парсер | `manage.py parse_track` | `manage.py parse_premium` |
| Тесты CLI | 62 passed | 25 passed |

## 5. Итог для отчета

- Для детальной части отчета используй `gpt/README.md` и `qwen/README.md`: там уже развернуто заполнен шаблон по каждой команде и добавлены технические требования.
- Этот корневой README оставлен как индекс и сравнительное резюме.
