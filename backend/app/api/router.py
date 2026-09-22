"""
Aggregates all route modules under a single APIRouter, mounted
in main.py under the configured API prefix.
"""
from fastapi import APIRouter

from app.api.routes import ai, auth, findings, health, knowledge, projects, reports, scans, source

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(projects.router)
api_router.include_router(source.router)
api_router.include_router(scans.router)
api_router.include_router(findings.router)
api_router.include_router(reports.router)
api_router.include_router(ai.router)
api_router.include_router(knowledge.router)
