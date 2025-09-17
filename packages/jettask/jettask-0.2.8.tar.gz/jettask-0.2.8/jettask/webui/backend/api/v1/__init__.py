"""
API v1 routes
"""
from fastapi import APIRouter
from .queues import router as queues_router
from .tasks import router as tasks_router
from .monitoring import router as monitoring_router
from .namespaces import router as namespaces_router

# 创建v1路由器
v1_router = APIRouter(prefix="/v1")

# 注册子路由
v1_router.include_router(queues_router, prefix="/queues", tags=["queues"])
v1_router.include_router(tasks_router, prefix="/tasks", tags=["tasks"])
v1_router.include_router(monitoring_router, prefix="/monitoring", tags=["monitoring"])
v1_router.include_router(namespaces_router, prefix="/namespaces", tags=["namespaces"])