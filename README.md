# 📊 PitStop Timing Parsing

> Программа для парсинга данных с сайта тайминга заездов и предоставления доступа к ним через REST API и CLI.

**Статус:** в разработке  
**LLM:** Qwen3‑Coder
**Стек:** Django + DRF + PostgreSQL + CLI (Typer + Rich) + BeautifulSoup + Docker

---

# 📚 О проекте

Данный проект предназначен для:

- парсинга данных с сайта: https://timing.batyrshin.name/
- сохранения данных в базу PostgreSQL
- предоставления доступа к данным через REST API
- взаимодействия с системой через CLI‑утилиту
- анализа данных с помощью локальной LLM

Проект разрабатывается как CLI‑инструмент, удовлетворяющий требованиям:

- практическая полезность
- средняя / высокая сложность
- срок реализации: **4–6 недель**
- минимум **7 CLI команд / подкоманд**
- обязательное использование **REST API**

---

# 🌐 Источник данных

Используемые страницы:

| Тип данных | URL |
|---|---|
| Календарь заездов | https://timing.batyrshin.name/tracks/premium/heats |
| Карты | https://timing.batyrshin.name/tracks/premium/karts |
| Гонщики | https://timing.batyrshin.name/tracks/premium/drivers |
| Статистика гонщика | https://timing.batyrshin.name/tracks/premium/drivers/{id} |
| Статистика карта | https://timing.batyrshin.name/tracks/premium/karts/{id} |
| Заезд | https://timing.batyrshin.name/tracks/premium/heats/{id} |

---

# 🏗 Архитектура проекта

## Основные компоненты

```
Parser (BeautifulSoup)
        ↓
PostgreSQL
        ↓
Django REST API
        ↓
CLI утилита
        ↓
LLM интеграция (Qwen)
```

---

# 🤖 Используемый стек

## Backend

- Django
- Django REST Framework
- PostgreSQL

## CLI

- Typer
- Rich

## Парсинг

- BeautifulSoup

## Инфраструктура

- Docker
- docker‑compose
- uv

## Конфигурация

- .env

## LLM

- Qwen
- Ollama

---

# 🧠 История разработки и проблемы

Проект разрабатывался поэтапно с использованием Qwen3‑Coder.

---

# Этап 1 — Создание Django‑проекта

## ✅ Получено

- skeleton Django проекта
- docker конфигурация
- docker‑compose.yaml
- .env
- .dockerignore
- settings.py
- схема базы данных

## ❌ Проблемы

### 1. Несогласованность .env и Docker

Разные названия переменных → контейнер не запускался.

Решение:

- синхронизация переменных

---

### 2. Устаревший стек линтеров

Предложено:

- flake8
- isort
- black

Заменено на:

- ruff

Также:

- заменена библиотека env
- заменён psycopg → psycopg[binary]

---

# Этап 2 — Создание парсера

## Подход

Использованы Django custom commands.

Это позволило:

- легко интегрировать с CLI
- управлять парсингом

---

## ❌ Проблемы

### Ошибки импорта

- забытые импорты
- неправильные пути

Исправлено вручную.

---

### Основная проблема — структура заездов

Результаты представлены в виде матрицы.

Парсер не был готов к этому.

Проблемы:

- неправильные колонки
- разные типы заездов:

  - квалификация
  - гонка
  - тренировка


## Решение

Использование ключевых слов для определения типа заезда.

Результат:

✔ корректный парсинг

---

# Этап 3 — Реализация REST API

## ❌ Проблемы

### 1. Использование не оптимальной архитектуры

Использовано:

- View
- ViewSet

Вместо:

- GenericAPIView
- mixins


### 2. Потеря контекста settings.py

Qwen забыл предыдущую конфигурацию.

Добавлено вручную.

---

### 3. Ошибки сериализаторов

Ошибка:

Kart.last_seen — поле не существует

Исправлено.

---

### 4. Отсутствие drf_spectacular

Добавлен в requirements.

---

### 5. Ошибка 500 при открытии заезда

Причина:

некорректный код view

Исправлено.

---

# Этап 4 — CLI утилита

## Используемый стек

- Typer
- Rich


## Результат

Получен:

- удобный
- красивый
- читаемый CLI

---

## Проблемы

### Импорты

Исправлены вручную.

---

### Алиасы

Создан batch файл для сокращения команд.

Пример:

```
karting drivers list
```

---

# Этап 5 — Интеграция LLM

Используется:

- Qwen
- Ollama

Размер модели:

4.7 GB

---

## Функционал

LLM получает:

- данные заезда

LLM возвращает:

- анализ
- описание
- вывод


---

# 📁 Структура проекта

```
project
│
├── backend
│
├── parser
│
├── cli
│
├── docker
│
├── .env
│
└── README.md
```

---

# ⚙️ Функциональность API

API позволяет:

- получать гонщиков
- получать карты
- получать заезды
- получать статистику

---

# 🖥 CLI инструкция

------------------------------------------------------------------------

# 🏁 heats --- Heats commands

## heats list

Description: list heats

    karting heats list [OPTIONS]

Options:

  Option     Type   Description
  ---------- ------ -------------------------------
  --track    INT    Track ID
  --type     STR    Race, Qualification, Practice
  --champ    STR    Championship
  --from     DATE   Start date
  --to       DATE   End date
  --limit    INT    Limit
  --format   STR    table, json

Example:

    karting heats list
    karting heats list --limit 100

------------------------------------------------------------------------
## heats detail

    karting heats detail <heat_id>

Example:

    karting heats detail 123

------------------------------------------------------------------------
# 👤 drivers

## drivers list

    karting drivers list

## drivers detail

    karting drivers detail <driver_id>

------------------------------------------------------------------------

# 📊 results

    karting results list

------------------------------------------------------------------------

# 📈 stats

    karting stats driver <driver_id>

------------------------------------------------------------------------
# 📤 export

## CSV

    karting export csv

## JSON

    karting export json

------------------------------------------------------------------------

# 🏎 tracks

    karting tracks list

------------------------------------------------------------------------

# 🤖 AI

## Analyze heat

    karting ai analyze-heat <heat_id>

------------------------------------------------------------------------
---

# 🚀 Итог

В результате получена система:

✔ Парсер  
✔ REST API  
✔ CLI  
✔ LLM интеграция  
✔ Docker  
✔ PostgreSQL  


---

# 🧠 Вывод

Основная сложность проекта:

парсинг структуры заездов.


LLM значительно ускорил разработку,

но требовал:

- контроля
- исправлений
- уточнения промтов


---

# 📌 Автор

Разработано с использованием:

Qwen3‑Coder

и ручной доработки

---

# 📄 License

MIT

