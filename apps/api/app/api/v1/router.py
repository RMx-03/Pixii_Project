"""API v1 router registration."""

from fastapi import APIRouter

from app.api.v1.routes import diagnostics

api_router = APIRouter()
api_router.include_router(diagnostics.router, prefix="/diagnostics", tags=["diagnostics"])

