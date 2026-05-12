# Pure Study

A personalized learning platform that builds an individual knowledge graph through an AI conversation — not a static course catalogue.

## Concept

When someone wants to learn something new, they usually get a standard course written for an abstract average student. Pure Study works differently: an AI asks a few questions, understands the user's level and goal, then builds a **personal topic graph** — what to study, in what order, what unlocks after what.

As the user progresses, the graph expands: the AI adds the next wave of topics based on what has already been mastered. If an explanation isn't landing, it escalates its style from first-principles to analogies, then to Socratic dialogue.

## Architecture

```
Browser
   │
   ▼
┌─────────────────────────────────────────────────┐
│  Gateway :8000                                   │
│  JWT middleware · Rate limiting · Proxy          │
└────┬────────┬────────┬────────┬──────────────────┘
     │        │        │        │
     ▼        ▼        ▼        ▼
  Auth     Graph      AI    Material
  :8001    :8002    :8003    :8004
     │        │        │        │
 Postgres  FalkorDB  Claude   Wikipedia
           (graph)    API     MIT OCW
```

### Services

| Service | Port | Stack | Role |
|---------|------|-------|------|
| **gateway** | 8000 | FastAPI, Redis | Single entry point. Verifies JWT, proxies requests, rate limiting |
| **auth** | 8001 | FastAPI, SQLAlchemy, bcrypt | Registration, login, refresh tokens, Google OAuth. JWT RS256 |
| **graph** | 8002 | FastAPI, FalkorDB | Knowledge graph: courses, topics, CONTAINS/REQUIRES edges. Topic state machine |
| **ai** | 8003 | FastAPI, Anthropic SDK | AI agents on Claude. Onboarding, explanation, copilot, graph generation |
| **material** | 8004 | FastAPI, httpx, BeautifulSoup | Course parsing from external sources: MIT OCW, Wikipedia |
| **frontend** | 3000 | React, TypeScript, Vite, Nginx | SPA with knowledge graph view, study chat, and course pages |

### Infrastructure

| Component | Role |
|-----------|------|
| **PostgreSQL** | Users and refresh tokens (auth service) |
| **FalkorDB** | Topic graph (courses, edges, statuses) |
| **Redis** | Rate limiting in gateway |

## AI Agents

### OnboardingAgent
A two-phase agent. First it interviews the user (3–5 questions): what they want to learn, why, their current level, how many hours per week they can commit. Then it searches for materials via MIT OCW / Wikipedia and creates a personalised graph of 5–10 topics in FalkorDB, adapted to the user's level.

### ExplanationAgent
Three explanation modes, escalated on demand:
1. **Level 1** — Haiku — first-principles: explains through causal chains from fundamentals
2. **Level 2** — Sonnet — analogies: finds a vivid real-world analogy that maps cleanly onto the concept
3. **Level 3** — Opus — Socratic dialogue: never explains directly, asks leading questions to guide discovery

### CopilotAgent
A chat assistant during study sessions. Knows the user's graph, sees which topics are available, guides the user along the path. Automatically compresses long chat history via Haiku summarisation.

### GraphGenAgent
Generates the next wave of topics (2–5 at a time) for an existing course. Uses the current graph and source materials as context to avoid duplicating already-covered content.

## Knowledge Graph

Topics are stored in FalkorDB with a state machine:

```
locked → available → in_progress → mastered
```

A `REQUIRES(A → B)` edge means topic A unlocks when B is mastered. When the user masters a topic, the graph automatically unlocks dependent topics.

## Material Sources

### MIT OpenCourseWare
- **Search**: indexes `sitemap.xml` (2 500+ courses) by keyword match in the course slug
- **Topics**: parses the course page navigation — top-level sections only (sub-parts excluded)

### Wikipedia
- **Search**: `action=query&list=search` — full-text search across articles
- **Topics**: `action=parse&prop=sections` — h2-level sections, boilerplate filtered out (See also, References, etc.)

## Project Structure

```
pure-study/
├── docker-compose.yml
├── .env.example
├── keys/                        # RSA keys for JWT (generated locally)
│   ├── private.pem
│   └── public.pem
├── frontend/
│   └── app/                     # React / TypeScript SPA
│       └── src/
│           ├── pages/           # AuthPage, OnboardingPage, CoursePage, GraphPage
│           ├── components/      # GraphView, StudyPanel, CommandPalette, ...
│           ├── api/             # HTTP clients to gateway
│           └── store/           # Zustand stores
└── services/
    ├── gateway/                 # Proxy + JWT + rate limiting
    ├── auth/                    # Auth + Google OAuth
    ├── graph/                   # FalkorDB knowledge graph
    ├── ai/                      # Claude AI agents
    └── material/                # Course scraping
```

## Getting Started

### Prerequisites
- Docker and Docker Compose
- RSA key pair for JWT (generate below)
- Anthropic API key

### 1. Generate RSA keys

```bash
mkdir keys
openssl genrsa -out keys/private.pem 2048
openssl rsa -in keys/private.pem -pubout -out keys/public.pem
```

### 2. Configure environment

```bash
cp .env.example .env
```

Fill in `.env`:

```env
# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# JWT
JWT_PRIVATE_KEY_PATH=/app/keys/private.pem
JWT_PUBLIC_KEY_PATH=/app/keys/public.pem
JWT_ALGORITHM=RS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30

# Google OAuth (optional)
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback
```

### 3. Start

```bash
docker compose up --build
```

Services start in the correct order (postgres and falkordb healthcheck before dependent services).

| URL | Description |
|-----|-------------|
| http://localhost:3000 | Frontend |
| http://localhost:8000 | Gateway API |
| http://localhost:8001/docs | Auth Swagger |
| http://localhost:8002/docs | Graph Swagger |
| http://localhost:8003/docs | AI Swagger |
| http://localhost:8004/docs | Material Swagger |

## Running Tests

Each service is tested in isolation via `uv`:

```bash
cd services/auth     && uv run pytest -v   # 31 tests
cd services/gateway  && uv run pytest -v   # 18 tests
cd services/graph    && uv run pytest -v   # 23 tests
cd services/ai       && uv run pytest -v   # 14 tests
cd services/material && uv run pytest -v   #  7 tests
```

93 tests total, all unit tests, no external dependencies.

## API Reference

### Auth (`/auth/...`)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/register` | Register → access + refresh tokens |
| POST | `/auth/login` | Login → tokens |
| POST | `/auth/refresh` | Rotate tokens using refresh token |
| POST | `/auth/logout` | Revoke refresh token |
| GET | `/auth/google` | Get Google OAuth URL |
| GET | `/auth/google/callback` | Google OAuth callback |

### Graph (`/graph/...`)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/graph/courses` | Create a course |
| GET | `/graph/courses` | List user's courses |
| GET | `/graph/courses/{id}` | Course with topics |
| POST | `/graph/topics` | Create a topic |
| GET | `/graph/topics/available` | Available topics |
| PATCH | `/graph/topics/{id}/transition` | Change topic status |
| POST | `/graph/edges` | Create a CONTAINS or REQUIRES edge |

### AI (`/ai/...`)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/ai/onboarding/message` | Onboarding chat step |
| POST | `/ai/explain` | Explain a topic (level 1 / 2 / 3) |
| POST | `/ai/copilot/message` | Send a message to the copilot |
| POST | `/ai/graph/next-level` | Generate the next wave of topics |

### Material (`/material/...`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/material/sources` | List available sources |
| POST | `/material/search` | Search courses by query |
| GET | `/material/sources/{source}/courses/{id}/topics` | Fetch course topics |
