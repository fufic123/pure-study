# Pure Study

Персонализированная платформа для обучения, которая строит индивидуальный граф знаний на основе разговора с AI, а не статичного списка курсов.

## Идея

Когда человек хочет изучить что-то новое, он обычно получает стандартный курс, написанный для абстрактного среднего студента. Pure Study делает иначе: AI задаёт несколько вопросов, понимает уровень пользователя и его цель, а затем строит **персональный граф топиков** — что изучать, в каком порядке, что разблокируется после чего.

По мере прохождения граф расширяется: AI добавляет следующую волну топиков исходя из уже освоенного. Если объяснение не заходит — экскалирует стиль от first-principles к аналогиям и далее к сократовскому диалогу.

## Архитектура

```
Browser
   │
   ▼
┌─────────────────────────────────────────────────┐
│  Gateway (8000)                                  │
│  JWT middleware · Rate limiting · Proxy          │
└────┬────────┬────────┬────────┬──────────────────┘
     │        │        │        │
     ▼        ▼        ▼        ▼
  Auth     Graph      AI    Material
  (8001)  (8002)   (8003)   (8004)
     │        │        │        │
 Postgres  FalkorDB   Claude  Wikipedia
           (граф)     API     MIT OCW
```

### Сервисы

| Сервис | Порт | Стек | Назначение |
|--------|------|------|------------|
| **gateway** | 8000 | FastAPI, Redis | Единая точка входа. Верифицирует JWT, проксирует запросы, rate limiting |
| **auth** | 8001 | FastAPI, SQLAlchemy, bcrypt | Регистрация, логин, refresh-токены, Google OAuth. JWT RS256 |
| **graph** | 8002 | FastAPI, FalkorDB | Граф знаний: курсы, топики, рёбра CONTAINS/REQUIRES. Машина состояний топиков |
| **ai** | 8003 | FastAPI, Anthropic SDK | AI-агенты на Claude. Онбординг, объяснение, копилот, генерация графа |
| **material** | 8004 | FastAPI, httpx, BeautifulSoup | Парсинг курсов из внешних источников: MIT OCW, Wikipedia |
| **frontend** | 3000 | React, TypeScript, Vite, Nginx | SPA с графом знаний, чатом и страницами курсов |

### Инфраструктура

| Компонент | Назначение |
|-----------|------------|
| **PostgreSQL** | Пользователи и refresh-токены (auth service) |
| **FalkorDB** | Граф топиков (курсы, рёбра, статусы) |
| **Redis** | Rate limiting в gateway |

## AI-агенты

### OnboardingAgent
Двухфазный агент. Сначала проводит интервью (3–5 вопросов): что хочет изучить, зачем, текущий уровень, сколько часов в неделю. Потом ищет материалы через MIT OCW/Wikipedia и создаёт персонализированный граф из 5–10 топиков в FalkorDB — с учётом уровня пользователя.

### ExplanationAgent
Три режима объяснения, переключаемых по мере нужды:
1. **Level 1** (Haiku) — first-principles: объясняет через причинно-следственные цепочки
2. **Level 2** (Sonnet) — аналогии: находит реальный образ, который точно отображает концепцию
3. **Level 3** (Opus) — сократовский диалог: не объясняет напрямую, задаёт наводящие вопросы

### CopilotAgent
Чат-ассистент во время учёбы. Знает граф пользователя, видит какие топики доступны, направляет по пути. Автоматически сжимает длинную историю через Haiku-суммаризацию.

### GraphGenAgent
Генерирует следующую волну топиков (2–5 за раз) для существующего курса. Использует текущий граф и материалы как контекст, чтобы не дублировать уже пройденное.

## Граф знаний

Топики хранятся в FalkorDB с машиной состояний:

```
locked → available → in_progress → mastered
```

Ребро `REQUIRES(A → B)` означает: топик A разблокируется, когда B освоен. Когда пользователь осваивает топик, граф автоматически разблокирует зависимые топики.

## Источники материалов

### MIT OpenCourseWare
- **Поиск**: индексирует sitemap.xml (2500+ курсов) по ключевым словам в слаге
- **Топики**: парсит навигацию курс-страницы — только верхнеуровневые разделы

### Wikipedia
- **Поиск**: `action=query&list=search` — полнотекстовый поиск по статьям
- **Топики**: `action=parse&prop=sections` — h2-разделы статьи без мусора (See also, References и т.д.)

## Структура проекта

```
pure-study/
├── docker-compose.yml
├── .env.example
├── keys/                        # RSA ключи для JWT
│   ├── private.pem
│   └── public.pem
├── frontend/
│   └── app/                     # React/TypeScript SPA
│       └── src/
│           ├── pages/           # AuthPage, OnboardingPage, CoursePage, GraphPage
│           ├── components/      # GraphView, StudyPanel, CommandPalette, ...
│           ├── api/             # HTTP-клиенты к gateway
│           └── store/           # Zustand stores
└── services/
    ├── gateway/                 # Proxy + JWT + rate limiting
    ├── auth/                    # Auth + Google OAuth
    ├── graph/                   # FalkorDB граф знаний
    ├── ai/                      # Claude AI агенты
    └── material/                # Парсинг курсов
```

## Запуск

### Требования
- Docker и Docker Compose
- Ключи RSA для JWT (или сгенерировать ниже)
- API-ключ Anthropic

### 1. Сгенерировать RSA-ключи

```bash
mkdir keys
openssl genrsa -out keys/private.pem 2048
openssl rsa -in keys/private.pem -pubout -out keys/public.pem
```

### 2. Настроить переменные окружения

```bash
cp .env.example .env
```

Заполнить `.env`:

```env
# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# JWT
JWT_PRIVATE_KEY_PATH=/app/keys/private.pem
JWT_PUBLIC_KEY_PATH=/app/keys/public.pem
JWT_ALGORITHM=RS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30

# Google OAuth (опционально)
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback
```

### 3. Запустить

```bash
docker compose up --build
```

Сервисы поднимутся в правильном порядке (postgres и falkordb healthcheck перед зависимыми сервисами).

| URL | Описание |
|-----|----------|
| http://localhost:3000 | Фронтенд |
| http://localhost:8000 | Gateway API |
| http://localhost:8001/docs | Auth Swagger |
| http://localhost:8002/docs | Graph Swagger |
| http://localhost:8003/docs | AI Swagger |
| http://localhost:8004/docs | Material Swagger |

## Запуск тестов

Каждый сервис тестируется изолированно через `uv`:

```bash
cd services/auth    && uv run pytest -v
cd services/gateway && uv run pytest -v
cd services/graph   && uv run pytest -v
cd services/ai      && uv run pytest -v
cd services/material && uv run pytest -v
```

Итого: **93 теста**, все unit, без внешних зависимостей.

## API

### Auth (`/auth/...`)
| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/auth/register` | Регистрация → access + refresh токены |
| POST | `/auth/login` | Логин → токены |
| POST | `/auth/refresh` | Обновить токены по refresh |
| POST | `/auth/logout` | Отозвать refresh-токен |
| GET | `/auth/google` | URL для OAuth |
| GET | `/auth/google/callback` | Callback Google OAuth |

### Graph (`/graph/...`)
| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/graph/courses` | Создать курс |
| GET | `/graph/courses` | Список курсов пользователя |
| GET | `/graph/courses/{id}` | Курс с топиками |
| POST | `/graph/topics` | Создать топик |
| GET | `/graph/topics/available` | Доступные топики |
| PATCH | `/graph/topics/{id}/transition` | Изменить статус топика |
| POST | `/graph/edges` | Создать ребро CONTAINS/REQUIRES |

### AI (`/ai/...`)
| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/ai/onboarding/message` | Шаг онбординг-чата |
| POST | `/ai/explain` | Объяснение топика (level 1/2/3) |
| POST | `/ai/copilot/message` | Сообщение копилоту |
| POST | `/ai/graph/next-level` | Сгенерировать следующую волну топиков |

### Material (`/material/...`)
| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/material/sources` | Список источников |
| POST | `/material/search` | Поиск курсов по запросу |
| GET | `/material/sources/{source}/courses/{id}/topics` | Топики курса |
