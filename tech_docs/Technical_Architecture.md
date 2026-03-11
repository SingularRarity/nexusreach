# NexusReach — Technical Architecture Document

**Version:** 1.0
**Author:** SingularRarity Labs
**Status:** Approved
**Last Updated:** March 2026

---

## 1. Architecture Philosophy

This document defines the technical architecture of NexusReach. Every decision recorded here is grounded in SingularRarity's engineering principles: **understand before you build, performance is a feature, design for failure, observability before launch, security cannot be retrofitted, documentation is code, and build to be replaced.**

These are not aspirational values. They are contractual constraints that shape every layer of this system — from database schema to deployment pipeline.

> *"Good enough" software ships. Elite software compounds.*

---

## 2. System Overview

NexusReach is a full-stack, production-grade influencer-brand intelligence platform. It combines semantic AI matching, geo-targeted discovery, real-time notifications, and CQRS-based analytics — all deployed as independent, horizontally scalable services.

```
┌────────────────────────────────────────────────────────┐
│                      CLIENT LAYER                      │
│         React 18 + Vite + TypeScript (Vercel)          │
└────────────────────┬───────────────────────────────────┘
                     │ HTTPS / WebSocket
┌────────────────────▼───────────────────────────────────┐
│                    API GATEWAY LAYER                   │
│             FastAPI 0.111 (Railway / uvicorn)          │
│          JWT Auth · Rate Limiting · CORS · RBAC        │
└──────┬─────────────┬──────────────┬────────────────────┘
       │             │              │
┌──────▼──────┐ ┌────▼─────┐ ┌─────▼──────┐
│  Core APIs  │ │ AI Match │ │  WebSocket │
│  /v1/...    │ │  Engine  │ │  /ws/{uid} │
└──────┬──────┘ └────┬─────┘ └─────┬──────┘
       │             │              │
┌──────▼─────────────▼──────────────▼──────────────────┐
│                   SERVICE LAYER                       │
│   InfluencerService · CampaignService · Analytics     │
│   MatcherService · NotificationService                │
└──────┬─────────────────────────────┬─────────────────┘
       │                             │
┌──────▼──────┐               ┌──────▼──────┐
│  PostgreSQL │               │   Redis 7   │
│  16+pgvector│               │  Cache+PubSub│
└─────────────┘               └──────┬──────┘
                                     │
                              ┌──────▼──────┐
                              │   Celery 5  │
                              │  Worker+Beat│
                              └─────────────┘
```

---

## 3. Tech Stack

| Layer | Technology | Rationale |
|---|---|---|
| Frontend | React 18 + Vite + TypeScript (strict) + Tailwind CSS + Zustand | Compound component patterns; strict typing eliminates runtime surprises |
| Backend | FastAPI 0.111+, Python 3.12, SQLAlchemy 2.0 async, Pydantic v2 | Async-first; OpenAPI auto-generation; Pydantic validates every boundary |
| Database | PostgreSQL 16 + pgvector extension | ACID guarantees + semantic vector search in a single engine |
| Cache / Queue | Redis 7 + Celery 5 + Celery Beat | Sub-millisecond cache hits; Pub/Sub for WebSocket fan-out; idempotent job scheduling |
| AI Layer | LangChain + Anthropic Claude API | 1536-dim embeddings; cosine similarity via pgvector; cacheable results |
| Auth | JWT + OAuth2 Google via fastapi-users | No password storage; refresh token rotation with Redis blacklist |
| Infra (dev) | Docker Compose | Reproducible local environment; production-parity from Day 1 |
| Infra (prod) | Vercel (frontend) + Railway (backend + DB + Redis) | Zero-config Vite deploys; managed Postgres with pgvector plugin |
| Testing | Pytest + Vitest + Playwright | Unit → integration → E2E coverage; CI gate on every PR |
| Observability | Prometheus + Grafana + Loki + Sentry + OpenTelemetry | Full metrics/logs/traces/errors stack — deployed with the app, not after |

---

## 4. Principle 1 — Understand Before You Build

### What Was Mapped Before Development Started

Before a single line of code was written, the following were explicitly modelled:

**User Mental Models:**
- Brand managers think in *campaigns* (brief → match → activate → report), not API endpoints.
- Influencers think in *deals* (incoming → review → accept/decline → track earnings).
- Agencies think in *portfolios* (multiple brands, multiple campaigns, one unified view).

**Failure Paths:**
- Social API unavailability → fallback to cached verified metrics (24h TTL).
- LLM/embedding service timeout → return cached match results or degrade to keyword fallback.
- WebSocket disconnect → client auto-reconnects with exponential backoff; no notifications lost (Redis Pub/Sub buffers).
- Celery task failure → dead letter queue; idempotent retry is safe by design.

**Integration Realities:**
- Every third-party API (Instagram Graph API, YouTube Data API, Anthropic) is treated as a liability — circuit breakers and fallbacks exist before go-live.
- pgvector is an extension, not a separate service — it lives inside Postgres, reducing operational surface area.

**Growth Trajectory:**
- At 10x scale: stateless FastAPI behind a load balancer scales horizontally. Celery workers scale independently. Redis Cluster handles Pub/Sub fan-out. Postgres read replicas serve analytics queries.

---

## 5. Principle 2 — Performance Is a Feature

### Non-Negotiable Targets

| Metric | Target | How We Achieve It |
|---|---|---|
| API response (read endpoints) | < 200ms p95 | Redis cache layer first; async DB reads via SQLAlchemy 2.0 |
| Page load (LCP) | < 1.5s | Vite code splitting; TanStack Query prefetch; CDN via Vercel Edge |
| Database query | < 50ms p99 | Indexed columns; pgvector HNSW index for embedding search; CQRS read model |
| AI match response | < 800ms | Redis cache on brief hash (1h TTL); pgvector `<=>` cosine query with LIMIT 10 |
| WebSocket notification | < 100ms | Redis Pub/Sub → direct WebSocket push; no polling |

### Async-First Pattern

Every route handler is `async`. No synchronous DB calls inside async context. SQLAlchemy 2.0 async sessions are scoped per-request via FastAPI dependency injection.

```python
# Correct — async session, parallel fetch
async def get_campaign_with_analytics(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_db),
    cache: Redis = Depends(get_redis),
) -> CampaignDetailResponse:
    campaign, analytics = await asyncio.gather(
        campaign_service.get(db, campaign_id),
        analytics_service.get_summary(db, campaign_id),
    )
    return CampaignDetailResponse(campaign=campaign, analytics=analytics)
```

### Cache Strategy

| Data | TTL | Invalidation |
|---|---|---|
| AI match results (keyed by brief hash) | 1 hour | TTL expiry |
| Influencer verified metrics | 24 hours | On manual admin re-verification |
| Campaign analytics summary | 15 minutes | Celery Beat aggregation cycle |
| JWT refresh token blacklist | Token expiry duration | On logout |

---

## 6. Principle 3 — Design for Failure, Not Success

### Resilience Patterns

**Circuit Breaker (External APIs)**

```
Normal → 5 failures in 30s → OPEN (reject fast)
OPEN → 60s cooldown → HALF-OPEN (probe one request)
HALF-OPEN → success → CLOSED
HALF-OPEN → failure → OPEN again
```

Applied to: Anthropic API, Instagram Graph API, YouTube Data API.

**Retry Logic**
- Exponential backoff: 1s → 2s → 4s → 8s with randomised jitter (prevents thundering herd)
- Max 3 retries → dead letter queue for manual inspection
- Celery tasks retry on transient failures; idempotent by design (upsert, not insert)

**Graceful Degradation**

| Dependency Down | Behaviour |
|---|---|
| Anthropic API | Return cached match results; surface "results may be from cache" indicator |
| Instagram/YouTube API | Display last verified metrics with timestamp; disable real-time refresh |
| Redis cache | Fall through to direct DB read (slower, never broken) |
| Celery worker | Analytics writes queue; aggregation catches up on worker recovery |
| WebSocket server | Client degrades to polling (30s interval) until reconnection succeeds |

---

## 7. Principle 4 — Observability Before Launch

Observability is not a post-launch concern. The full stack is deployed on Day 1 of production.

### Stack

| Signal | Tool | Destination |
|---|---|---|
| Metrics | Prometheus | Grafana dashboards |
| Logs | structlog (structured JSON) | Loki → Grafana |
| Traces | OpenTelemetry | Jaeger (full request traces across services) |
| Errors | Sentry | Real-time alerts with full request context |
| Uptime | UptimeRobot | PagerDuty on-call escalation |

### Dashboards Shipped With the Application

**Business Dashboard**
- AI match requests per hour and cache hit ratio
- Lead conversion: proposals sent → campaigns activated
- Influencer onboarding rate (day-over-day)
- Campaign completion rate per city

**Technical Dashboard**
- P50 / P95 / P99 latency by endpoint
- Error rate by service and status code
- PostgreSQL connection pool utilisation
- Redis memory usage and cache eviction rate
- Celery task queue depth and failure rate
- WebSocket active connections per region

### Structured Logging Contract

Every log line emits structured JSON with a minimum set of fields:

```json
{
  "timestamp": "2026-03-11T10:00:00Z",
  "level": "info",
  "service": "nexusreach-api",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "...",
  "endpoint": "/api/v1/match",
  "duration_ms": 142,
  "status_code": 200
}
```

---

## 8. Principle 5 — Security Cannot Be Retrofitted

Security is embedded at the architecture level, not audited in after the fact.

### Authentication & Authorisation

- **OAuth2 Google** via `fastapi-users` — zero password storage.
- **JWT Bearer tokens** — short-lived access tokens (15 min), long-lived refresh tokens (7 days) stored in Redis.
- **Refresh token rotation** — each refresh issues a new token and blacklists the previous one.
- **Fine-grained RBAC** — roles: `influencer`, `brand`, `agency`, `admin`. Every route declares required role in dependency.

### Data Layer

- **Row Level Security (RLS)** — Postgres policies enforce that brands can only read their own campaigns; influencers can only read their own profiles via direct DB access.
- **PII field encryption** — phone numbers, email addresses encrypted at rest (application-layer AES-256 before persistence).
- **TLS everywhere** — all connections (app → Postgres, app → Redis, client → API) enforce TLS. No plaintext internal traffic.

### API Layer

- **Pydantic v2 validation** on every request schema — no raw `dict` pass-through, ever.
- **Rate limiting** — per-user, per-IP, per-agent-endpoint limits enforced at the FastAPI middleware layer.
- **Input sanitisation** — all string fields validated for length and character set at schema level.
- **No `Any` types** in Python or TypeScript — strict mode enforced in `pyproject.toml` and `tsconfig.json`.

### Infrastructure

- **Secrets in environment variables** — never in `.env` committed to Git, never hardcoded. Railway KeyVault for production.
- **Container scanning** — Docker images scanned pre-deploy in CI pipeline.
- **Network policies** — zero-trust between services on Railway private network.

---

## 9. Core Domain Models

```
User (fastapi-users base)
 ├── InfluencerProfile (1:1)
 │    ├── embedding vector(1536)    ← pgvector
 │    ├── niche_tags[]
 │    └── city, follower_count, engagement_rate
 ├── Brand (1:1)
 │    └── industry, website
 └── Notification (1:N)

Campaign
 ├── brand_id → Brand
 ├── status: proposed | active | completed | cancelled
 ├── CampaignInfluencer (M:N join with status)
 └── AnalyticsEvent (event sourcing — append-only)
      └── CampaignDailySummary (materialised aggregate)
```

**All models share:**
- UUID primary keys (no sequential integer IDs exposed externally)
- `created_at` / `updated_at` with server-side `now()` defaults
- Alembic migrations for every schema change — no `CREATE TABLE` in application code

---

## 10. AI Match Engine

### Design

The match engine uses LangChain with the Anthropic Embeddings API to generate 1536-dimensional vector representations of influencer bios. Brand campaign briefs are embedded at query time and matched via pgvector cosine similarity.

```
Brand Brief (text)
       │
       ▼
AnthropicEmbeddings.embed_query()
       │
       ▼
query_embedding vector(1536)
       │
       ▼
SELECT * FROM influencer_profiles
ORDER BY embedding <=> :query_embedding
LIMIT 10
       │
       ▼
Top-10 influencers + match_score (0.0–1.0)
       │
       ▼
Cache result in Redis (key = SHA256(brief), TTL = 1h)
```

### Performance

- pgvector HNSW index on `embedding` column for approximate nearest-neighbour search.
- Cache hit avoids re-embedding and re-querying — p95 cached response < 20ms.
- Cache miss (cold brief) — full pipeline < 800ms.

---

## 11. CQRS + Event Sourcing (Analytics)

The analytics layer follows strict Command Query Responsibility Segregation:

**Write side (Commands):**
Every state-changing operation emits an `AnalyticsEvent` row (append-only). Examples:
- Campaign status change → `campaign.status_changed`
- Influencer proposal accepted → `deal.accepted`
- Campaign completed → `campaign.completed`

**Read side (Queries):**
`analytics_service.py` reads exclusively from `CampaignDailySummary` — never from raw events or write models.

**Celery Beat Task (every 15 min):**
Aggregates `AnalyticsEvent` rows into `CampaignDailySummary` using upsert. Fully idempotent — safe to re-run without duplicate data.

**Why this matters at scale:**
- Read queries never block on write traffic.
- Historical event log enables full audit trail and future replay.
- Aggregation can be re-run from scratch at any point.

---

## 12. Real-time Notifications (WebSocket + Redis Pub/Sub)

```
Campaign status changes
        │
        ▼
  FastAPI service publishes to
  Redis channel: notifications:{user_id}
        │
        ▼
  WebSocket handler subscribes
  to Redis Pub/Sub channel
        │
        ▼
  JSON payload pushed to connected client
```

**Authentication:** Token passed as query param on WebSocket connect; validated against JWT on handshake. Connection rejected on invalid token.

**Client resilience (useWebSocket hook):**
- Auto-reconnect with exponential backoff (base 1s, max 30s, randomised jitter)
- Notifications dispatched into Zustand `notificationSlice` for global state access
- Missed notifications replayed from server on reconnect (last 50 stored in Redis list per user, TTL 24h)

---

## 13. Frontend Architecture

### State Management

| State Type | Solution |
|---|---|
| Server state (API data) | TanStack Query v5 — `useInfluencers()`, `useCampaign(id)`, `useMatchResults()` |
| Global client state | Zustand — `authSlice`, `notificationSlice`, `campaignSlice` |
| Form state | React Hook Form + Zod validation |

### Compound Component Pattern

Complex, stateful UI sections use compound components to avoid prop drilling:

```tsx
<Campaign.Card>
  <Campaign.Header />
  <Campaign.Status />
  <Campaign.Actions onAccept={handleAccept} />
</Campaign.Card>
```

### Performance

- `React.memo` on all list items and cards to prevent unnecessary re-renders.
- `useMemo` / `useCallback` on computed values and stable callback references.
- TanStack Query optimistic updates on campaign status changes — UI responds immediately, reconciles on server confirm.
- Error boundaries on every page-level component — one broken widget never crashes the application.

### Geo Heatmap

- `react-leaflet` with circle markers sized by follower count.
- Dynamic bounding box per selected city — defaults to India-wide view; zooms to city on filter selection.
- Marker clustering at zoom-out; individual influencer popups at zoom-in.

---

## 14. Infrastructure & Deployment

### Development (Docker Compose)

All services run locally via Docker Compose. Source code mounted as volumes — no image rebuild on file change. Postgres uses `pgvector/pgvector:pg16` image with extension pre-installed.

### Production

| Service | Platform | Notes |
|---|---|---|
| Frontend | Vercel | Auto-deploy on push to `main`; preview URLs on every PR |
| Backend API | Railway | FastAPI via uvicorn; private network to Postgres + Redis |
| PostgreSQL | Railway (managed) | pgvector plugin enabled; automated backups |
| Redis | Railway (managed) | Persistent AOF; Pub/Sub for notifications |
| Celery Worker | Railway (separate service) | Scales independently of API |
| Celery Beat | Railway (separate service) | Single instance scheduler |

### Deployment Strategy

- **Blue-green deployment** — zero downtime on every release.
- **Alembic migrations** run as pre-deploy step, never in application startup.
- **Health checks** on every service before traffic routing.
- **Rollback** — previous image tag re-deployed in < 2 minutes.

### CI/CD Pipeline (GitHub Actions)

```
PR opened → pytest (backend) + vitest (frontend) + ruff lint
PR merged to main → build images → deploy to Railway + Vercel
Post-deploy → Playwright E2E smoke tests on staging URL
```

---

## 15. Principle 6 — Documentation Is Code

Every deliverable includes living documentation that is accurate at time of delivery:

| Document | Location | Owner |
|---|---|---|
| This Architecture Document | `tech_docs/Technical_Architecture.md` | Lead Architect |
| Product Requirements | `product_docs/PRD.md` | Product Manager |
| API Reference (auto-generated) | `/docs` (Swagger UI) | FastAPI OpenAPI spec |
| Environment Variables | `.env.example` | DevOps |
| Database Schema | Alembic `versions/` + data dictionary | Backend Lead |
| Deployment Runbook | `tech_docs/runbooks/deploy.md` | DevOps |
| Onboarding Guide | `tech_docs/onboarding.md` | Lead Engineer |

Goal: a new engineer is productive within 2 working days using documentation alone.

---

## 16. Principle 7 — Build to Be Replaced

NexusReach is engineered for client independence from Day 1:

- **100% open-source stack** — FastAPI, PostgreSQL, Redis, React. No proprietary vendor lock-in.
- **Full Git history from commit 1** — complete context preserved; no orphaned branches.
- **Infrastructure as Code** — Docker Compose for dev; Railway config as declarative manifests. Rebuild from zero in under 2 hours.
- **Secrets rotation documented** — runbook covers credential rotation without tribal knowledge.
- **Architecture diagrams current at all times** — this document is updated on every architectural decision.
- **You own everything** — source code, database, infrastructure config, and all documentation transfer to the client at handoff.

---

## 17. Architecture Decision Records (ADRs)

| # | Decision | Rationale |
|---|---|---|
| ADR-001 | PostgreSQL + pgvector over separate vector DB (Pinecone, Weaviate) | Reduces operational surface area; ACID guarantees for transactional + vector data in one engine |
| ADR-002 | FastAPI over Django REST Framework | Native async; automatic OpenAPI generation; Pydantic v2 first-class support |
| ADR-003 | Cursor-based pagination over offset pagination | Stable under concurrent inserts; no duplicate/missing rows on page boundaries at scale |
| ADR-004 | CQRS for analytics over direct query | Decouples write and read load; enables event replay; analytics never blocks campaign writes |
| ADR-005 | Redis Pub/Sub for WebSocket fan-out over server-sent events | Works across multiple API instances; decouples notification dispatch from connection handling |
| ADR-006 | Celery Beat for analytics aggregation over cron jobs | Integrated with existing Celery worker pool; observable; retry-aware; idempotent by design |
| ADR-007 | Railway + Vercel over self-hosted VPS | Managed Postgres with pgvector plugin; zero-config Vite deploys; focus engineering time on product |
| ADR-008 | Anthropic Claude API for embeddings over OpenAI | Alignment with SingularRarity platform; consistent with client's existing Anthropic relationship |

---

*This document reflects the complete technical architecture of NexusReach as designed and built by SingularRarity Labs. It is a living document — updated on every architectural change, not at handoff.*

*SingularRarity Labs — where singular ideas become rare realities.*
