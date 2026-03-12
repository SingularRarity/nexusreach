from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.redis import close_redis, init_redis


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    setup_logging()
    await init_redis()
    yield
    await close_redis()


app = FastAPI(
    title="NexusReach API",
    description="AI-powered influencer-brand intelligence platform",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api_router)


@app.get("/health", tags=["system"])
async def health_check() -> dict[str, str]:
    """Health check endpoint for load balancers and monitoring."""
    return {"status": "ok"}
