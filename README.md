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

## SEO

Pure Study is an authenticated SPA — most pages live behind login and have no business
being indexed. The SEO surface is intentionally small:

| Path | Served by | Indexed | Purpose |
|------|-----------|---------|---------|
| `/` | static `landing.html` | yes | marketing / acquisition |
| `/login` | SPA (`index.html`) | yes | brand keyword fallback |
| `/onboarding`, `/courses`, `/courses/:id`, `/graph` | SPA | **no** | per-user state, blocked in `robots.txt` |
| `/robots.txt`, `/sitemap.xml` | static | yes | crawler discovery |

### How search engines see the site

A search-engine crawler (Googlebot, Bingbot, etc.) doesn't run JavaScript reliably
or quickly. Static `landing.html` is plain server-rendered HTML — the crawler can
parse it in one request, extract meta tags and structured data, and add it to the
index. The SPA shell at `index.html` is mostly an empty `<div id="root">` until
React boots; crawlers still see the meta tags but the body content is hidden behind
JS execution, which Google does (delayed, in a second pass) but other crawlers
mostly don't.

That's why `/` serves a separate static HTML file and not the SPA. The route is
matched by nginx with an exact-match `location = /` block that sits **above** the
SPA fallback `location /` block — nginx picks the most specific match, so a request
for `/` hits the landing while `/login`, `/courses/abc`, etc. still fall through to
the SPA.

```nginx
# nginx.conf
location = / {
    try_files /landing.html =404;
}
location = /robots.txt { try_files $uri =404; }
location = /sitemap.xml { try_files $uri =404; }
location ~ ^/(auth|graph|ai|material|check)/ {
    proxy_pass http://gateway:8000;
}
location / {
    try_files $uri $uri/ /index.html;  # SPA fallback
}
```

### What's in the landing's `<head>`

Every SEO signal lives in `<head>` so the crawler picks them up before the body.

**1. Basic meta**
```html
<title>Pure.study — Learn anything as a personalized knowledge graph</title>
<meta name="description" content="..." />     <!-- ~155 chars, becomes the SERP snippet -->
<meta name="robots" content="index, follow" /> <!-- explicit allow -->
<link rel="canonical" href="https://pure.study/" /> <!-- dedupes URL variants -->
```
The `<title>` and `<meta description>` are what Google literally shows in the
search results. Title is a ranking signal; description is not (officially), but
it controls click-through rate.

**2. Open Graph** — for previews in Slack, Facebook, LinkedIn, iMessage, etc.
```html
<meta property="og:type" content="website" />
<meta property="og:title" content="..." />
<meta property="og:description" content="..." />
<meta property="og:image" content="https://pure.study/og-image.png" />
<meta property="og:url" content="https://pure.study/" />
```
When someone pastes a Pure Study link into Slack, Slack fetches the URL,
parses `og:*` tags, and renders the card. Same protocol for FB/LinkedIn/Discord.

**3. Twitter Card** — Twitter/X uses its own dialect.
```html
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="..." />
<meta name="twitter:image" content="..." />
```

**4. Structured data (JSON-LD)** — machine-readable description of *what the page
is*. Powers rich snippets (star ratings, sitelinks, search boxes, app cards).
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "Pure Study",
  "applicationCategory": "EducationalApplication",
  "offers": { "@type": "Offer", "price": "0", "priceCurrency": "USD" }
}
</script>
```
Schema.org defines hundreds of types (`Article`, `Product`, `Course`, `Person`,
`Organization`, `Recipe`, etc.). The crawler treats this as ground truth — much
more reliable than guessing from prose.

### `robots.txt` — controlling what gets crawled

Tells crawlers which paths are off-limits:
```
User-agent: *
Allow: /
Allow: /login
Disallow: /onboarding
Disallow: /courses
Disallow: /graph
Disallow: /auth/
Sitemap: https://pure.study/sitemap.xml
```
Two things to note:
- `Disallow` is a *request*, not a security control — well-behaved crawlers
  obey it, but it doesn't hide the URLs. Auth-gating is still what protects them.
- The `Sitemap:` line tells crawlers where the URL list lives.

### `sitemap.xml` — telling crawlers what to crawl

A simple XML list of every public URL. For a SaaS prototype it's tiny, but for
content sites (blogs, docs) it scales to thousands of entries:
```xml
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://pure.study/</loc><priority>1.0</priority></url>
  <url><loc>https://pure.study/login</loc><priority>0.6</priority></url>
</urlset>
```
Submit it once in Google Search Console; Google will recrawl it periodically.

### How a search query becomes a Pure Study visit

1. User types "learn python knowledge graph" into Google.
2. Google's index has Pure Study's landing because:
   - Googlebot fetched `https://pure.study/`
   - Read `<title>`, `<meta description>`, body text, JSON-LD
   - Stored relevance scores against keywords
3. Google ranks Pure Study among the results. Ranking factors:
   - **On-page**: keyword match in title/headings/body, freshness, page speed
     (Core Web Vitals — LCP, CLS, INP), mobile-friendliness, HTTPS
   - **Off-page**: backlinks from other sites (number + authority), brand mentions
   - **User signals**: click-through rate, dwell time, pogo-sticking
4. User clicks. Sees the static landing. Click "Start free" → `/login` → signup.

The landing exists *only* to win step 4. Nothing inside the app is for SEO.

### What's still missing in this repo

For a real deploy you'd want:
- A real **`og-image.png`** at 1200×630 (currently the meta links to a path that
  doesn't exist — Slack will render the card without a preview image).
- Real domain in `canonical` / `og:url` (currently hardcoded `pure.study`).
- A **proper landing prerender** if you want the SPA shell `/login` to score
  well too (use [`vite-plugin-prerender`](https://github.com/cap-js-community/vite-plugin-prerender)
  or migrate the landing into Next.js — current setup keeps the landing static,
  which is enough).
- **Google Search Console** verification + sitemap submission after deploy.
- **Analytics** (Plausible / GA4) to measure landing → signup conversion.
- If pursuing SEO seriously: a `/blog/...` or `/learn/...` section with one
  article per long-tail keyword (e.g. "How to learn Python in 4 weeks"), each
  ending in a CTA to the app. That's how every content-led SaaS grows organic.
| GET | `/material/sources/{source}/courses/{id}/topics` | Fetch course topics |
