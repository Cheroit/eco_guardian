# EcoGuardian — прототип сервиса мониторинга экологической обстановки

EcoGuardian — учебный прототип интеллектуальной системы мониторинга экологической обстановки в (квазирежиме) реального времени.  
Сервис собирает (в прототипе — генерирует) экологические показатели для выбранного города, оценивает интегральный риск и показывает краткое объяснение и рекомендации.

## Стек

- Backend: **Python + FastAPI**
- Frontend: статическая страница **HTML + Tailwind CSS + Fetch API**

## Структура проекта

- `backend/main.py` — FastAPI-приложение с эндпоинтами:
  - `GET /api/environment/current?city=...` — псевдоданные и оценка риска.
  - `POST /api/qa` — упрощённый Q&A по текущей обстановке (без реального LLM).
  - `GET /health` — health-check.
- `frontend/index.html` — простая одностраничная веб-страница (дашборд).
- `requirements.txt` — зависимости Python.

## Запуск backend (FastAPI)

```bash
cd eco_guardian
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cd backend
uvicorn main:app --reload
```

Backend будет доступен по адресу `http://localhost:8000`.

Проверьте, что всё работает:

- `http://localhost:8000/health`
- `http://localhost:8000/docs` — Swagger UI.

## Запуск frontend

Простейший вариант — открыть локально `frontend/index.html` в браузере.

Если браузер блокирует запросы из файловой системы, можно поднять простой HTTP-сервер:

```bash
cd eco_guardian/frontend
python -m http.server 5500
```

И затем открыть в браузере:

- `http://localhost:5500/index.html`

## Интеграция с LLM (дальнейшее развитие)

Сейчас `/api/qa` формирует ответ без обращения к реальной LLM.  
Для интеграции, например, с OpenAI API:

1. Добавить переменную окружения `OPENAI_API_KEY`.
2. В `backend/main.py` реализовать вызов LLM внутри эндпоинта `/api/qa` или отдельного сервиса.

Этот прототип можно разместить в отдельной ветке репозитория, например, `feature/ecoguardian-prototype`.

## Проработка сценариев и архитектуры

См. `ARCHITECTURE_RU.md` — сценарии, первичная архитектура модулей и структура данных (контракты для LLM).

