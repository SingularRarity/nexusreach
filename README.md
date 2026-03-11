# nexusreach

> AI-powered influencer-brand intelligence platform for geo-targeted campaign management across major cities in India.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-blue)](https://react.dev)
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/SingularRarity/nexusreach)

## Architecture Highlights
- **CQRS + Event Sourcing** for campaign state management
- **pgvector + LangChain** for semantic influencer-brand matching
- **Redis Pub/Sub WebSockets** for real-time deal notifications
- **Celery workers** for async analytics aggregation

## Local Development (Docker Only)

### Prerequisites
- Docker Desktop
- `.env` file (copy from `.env.example`)

### Start All Services
```bash
cp .env.example .env
docker compose up --build
```

| Service     | URL                        |
|-------------|----------------------------|
| Frontend    | http://localhost:5173      |
| Backend API | http://localhost:8000      |
| API Docs    | http://localhost:8000/docs |
| Redis       | localhost:6379             |
| Postgres    | localhost:5432             |

### Run Tests
```bash
# Backend
docker compose exec backend pytest

# Frontend
docker compose exec frontend npm run test
```

## One-Click Deploy

### Frontend → Vercel
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/SingularRarity/nexusreach&root=frontend)

### Backend → Railway
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/nexusreach)

> Set environment variables from `.env.example` on both platforms.

## Environment Variables

| Variable               | Description                    |
|------------------------|--------------------------------|
| `DATABASE_URL`         | PostgreSQL connection string   |
| `REDIS_URL`            | Redis connection string        |
| `CLAUDE_API_KEY`       | Anthropic Claude API key       |
| `JWT_SECRET`           | Random 32-char secret          |
| `GOOGLE_CLIENT_ID`     | OAuth2 Google client ID        |
| `GOOGLE_CLIENT_SECRET` | OAuth2 Google client secret    |

## Project Structure
```
nexusreach/
├── backend/
│   ├── app/
│   │   ├── api/           # Route handlers (v1/)
│   │   ├── core/          # Config, security, dependencies
│   │   ├── models/        # SQLAlchemy ORM models
│   │   ├── schemas/       # Pydantic v2 schemas
│   │   ├── services/      # Business logic layer
│   │   ├── workers/       # Celery tasks
│   │   └── ai/            # LangChain embedding & match engine
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/    # Reusable UI atoms/molecules
│   │   ├── pages/         # Route-level page components
│   │   ├── store/         # Zustand state slices
│   │   ├── hooks/         # Custom React hooks
│   │   ├── services/      # Axios API client layer
│   │   └── types/         # TypeScript interfaces
│   ├── Dockerfile
│   └── package.json
├── product_docs/
│   └── PRD.md
├── docker-compose.yml
├── docker-compose.prod.yml
├── vercel.json
└── README.md
```

## Contributing
PRs welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License
MIT © SingularRarity Labs
