"""Agregador de todos los routers de la versión 1."""

from fastapi import APIRouter

from app.api.v1.routers import activities, projects

api_v1_router = APIRouter()
api_v1_router.include_router(projects.router)
api_v1_router.include_router(activities.router)
