"""
API 模块
"""
from fastapi import APIRouter
from .projects import router as projects_router
from .tasks import router as tasks_router
from .agents import router as agents_router
from .ai_bridge import router as ai_bridge_router

api_router = APIRouter()

api_router.include_router(projects_router)
api_router.include_router(tasks_router)
api_router.include_router(agents_router)
api_router.include_router(ai_bridge_router)
