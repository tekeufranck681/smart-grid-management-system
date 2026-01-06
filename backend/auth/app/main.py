import logging
from contextlib import asynccontextmanager
from typing import Dict

import sentry_sdk
from app.cache.redis_client import close_redis, init_redis
from app.core.config import settings
from app.database.connection import test_async_connection
from app.routes.auth import router as auth_router
from app.routes.verify import router as verify_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import PrometheusFastApiInstrumentator

logger = logging.getLogger("main_app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Server starting")
    logger.info("Testing database connection")

    try:
        await test_async_connection()
        logger.info("Database connection OK")
    except Exception:
        logger.exception("Database connection failed")
        raise

    logger.info("Initializing Redis connection")

    try:
        await init_redis()
        logger.info("Redis connection initialized")
    except Exception:
        logger.exception("Redis initialization failed")
        raise

    logger.info("Startup complete")

    yield

    logger.info("Closing Redis connection")
    await close_redis()
    logger.info("Server shutdown complete")


sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
    # Enable sending logs to Sentry
    enable_logs=True,
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for tracing.
    traces_sample_rate=1.0,
    # Set profile_session_sample_rate to 1.0 to profile 100%
    # of profile sessions.
    profile_session_sample_rate=1.0,
    # Set profile_lifecycle to "trace" to automatically
    # run the profiler on when there is an active transaction
    profile_lifecycle="trace",
)


app = FastAPI(title="SGMS Auth Microservice API", version="1.0.0", lifespan=lifespan)


# Prometheus configuration
PrometheusFastApiInstrumentator(
    should_group_status_codes=False,  # Track exact HTTP status codes
    should_ignore_untemplated=True,  # Ignore 404s or unknown paths
    should_group_untemplated=False,  # Keep each dynamic path separate
    excluded_handlers=[
        "/metrics",
        "/admin",
    ],  # Don't count metrics scraping or admin routes
).instrument(app).expose(app, "/metrics", include_in_schema=False)


# Prometheus metrics
# REQUEST_COUNT = Counter("app_requests_total", "Total number of requests to app", ["method", "endpoint", "http_status"])
# RANDOM_NUMBER_GAUGE = Gauge("app_random_number", "current value of random number")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def welcome() -> Dict:
    """Welcome message endpoint."""
    return {"message": "Welcome to the FastAPI application!"}


# Include routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(verify_router, prefix="/api/v1")
