"""
CodeShieldAI FastAPI application entrypoint.
"""

import asyncio
import logging
import sys

# Playwright requires subprocess support on Windows.
# WindowsSelectorEventLoopPolicy does not support asyncio subprocesses,
# while ProactorEventLoopPolicy does.
if sys.platform == "win32":
    asyncio.set_event_loop_policy(
        asyncio.WindowsProactorEventLoopPolicy()
    )

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging


configure_logging()
logger = logging.getLogger(__name__)

settings = get_settings()


app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Evidence-driven AI-assisted security analysis platform. "
        "Phase 1: foundation (projects, scans, findings data model, "
        "Groq integration test)."
    ),
    version="0.1.0-phase1",
    debug=settings.DEBUG,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    api_router,
    prefix=settings.API_V1_PREFIX,
)


@app.on_event("startup")
def on_startup() -> None:
    logger.info(
        "%s starting up (env=%s)",
        settings.APP_NAME,
        settings.APP_ENV,
    )


@app.get("/")
def root() -> dict:
    return {
        "service": settings.APP_NAME,
        "phase": "Phase final - FULLY FUNCTIONAL",
        "docs": "/docs",
        "api": settings.API_V1_PREFIX,
    }