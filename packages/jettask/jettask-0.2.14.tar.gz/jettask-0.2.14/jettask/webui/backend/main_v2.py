"""
JetTask WebUI Backend v2 - Refactored and Optimized

重构后的主要改进：
1. 模块化架构，职责分离清晰
2. 统一的错误处理和响应格式
3. 缓存系统优化性能
4. 依赖注入提升可测试性
5. 监控和日志系统完善
"""
import sys
import os
import asyncio
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
import logging

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入核心模块
from core.database import db_manager
from core.cache import cache_manager
from core.exceptions import JetTaskAPIException

# 导入API路由
from api.v1 import v1_router

# 导入原有路由（向后兼容）
from namespace_api import router as namespace_router_old
from queue_backlog_api import router as backlog_router_old

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 应用启动时间
APP_START_TIME = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    startup_start = time.time()
    
    try:
        logger.info("=" * 60)
        logger.info("JetTask WebUI Backend v2 启动中...")
        
        # 1. 初始化缓存管理器
        if os.getenv('REDIS_URL'):
            from core.database import get_redis_client
            redis_client = await get_redis_client(os.getenv('REDIS_URL'), "cache")
            cache_manager.redis_client = redis_client
            logger.info("缓存管理器已初始化 (Redis)")
        else:
            logger.info("缓存管理器已初始化 (本地缓存)")
        
        # 2. 初始化数据库连接池
        pg_url = os.getenv('JETTASK_PG_URL', 'postgresql://jettask:123456@localhost:5432/jettask')
        await db_manager.get_pg_pool(pg_url, "default")
        logger.info(f"数据库连接池已初始化: {pg_url.split('@')[1] if '@' in pg_url else pg_url}")
        
        # 3. 初始化命名空间数据访问
        from namespace_data_access import get_namespace_data_access
        namespace_data_access = get_namespace_data_access()
        logger.info("命名空间数据访问已初始化")
        
        startup_duration = time.time() - startup_start
        logger.info(f"系统启动完成，耗时: {startup_duration:.2f}s")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"启动失败: {e}")
        raise
    
    yield
    
    # 关闭时清理资源
    try:
        logger.info("正在关闭系统...")
        
        # 清理数据库连接
        await db_manager.close_all()
        
        # 清理缓存
        cache_stats = cache_manager.get_stats()
        logger.info(f"缓存统计: {cache_stats}")
        
        logger.info("系统关闭完成")
        
    except Exception as e:
        logger.error(f"关闭时出错: {e}")


# 创建FastAPI应用
app = FastAPI(
    title="JetTask WebUI Backend",
    version="2.0.0",
    description="重构优化的JetTask监控后端API",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# 添加中间件
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应配置具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 请求计时中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # 记录请求开始
    logger.debug(f"开始处理请求: {request.method} {request.url}")
    
    response = await call_next(request)
    
    # 记录请求完成
    duration = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} - "
        f"状态码: {response.status_code} - "
        f"耗时: {duration:.3f}s"
    )
    
    # 添加响应头
    response.headers["X-Response-Time"] = f"{duration:.3f}s"
    response.headers["X-API-Version"] = "2.0.0"
    
    return response


# 全局异常处理器
@app.exception_handler(JetTaskAPIException)
async def jettask_exception_handler(request: Request, exc: JetTaskAPIException):
    """处理自定义API异常"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error_code": exc.error_code,
            "message": exc.detail,
            "details": exc.extra_data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "path": str(request.url)
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """处理请求验证异常"""
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "message": "请求参数验证失败",
            "details": {
                "errors": exc.errors(),
                "body": exc.body
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "path": str(request.url)
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """处理HTTP异常"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error_code": f"HTTP_{exc.status_code}",
            "message": exc.detail,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "path": str(request.url)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """处理未知异常"""
    logger.exception(f"未处理的异常: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "内部服务器错误",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "path": str(request.url)
        }
    )


# 根路由
@app.get("/")
async def root():
    """API根路径"""
    uptime = time.time() - APP_START_TIME
    
    return {
        "name": "JetTask WebUI Backend",
        "version": "2.0.0",
        "status": "healthy",
        "uptime_seconds": round(uptime, 2),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "features": [
            "模块化架构",
            "统一错误处理",
            "智能缓存",
            "性能监控",
            "向后兼容"
        ],
        "endpoints": {
            "v1_api": "/api/v1",
            "v2_docs": "/docs",
            "health": "/health",
            "metrics": "/metrics"
        }
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    uptime = time.time() - APP_START_TIME
    
    # 检查各组件状态
    components = {"api": "healthy"}
    
    # 检查数据库连接
    try:
        if "default" in db_manager._pg_pools:
            components["postgresql"] = "healthy"
        else:
            components["postgresql"] = "not_configured"
    except Exception as e:
        components["postgresql"] = f"unhealthy: {str(e)}"
    
    # 检查缓存
    try:
        cache_stats = cache_manager.get_stats()
        components["cache"] = f"healthy (hit_rate: {cache_stats['hit_rate']:.2%})"
    except Exception as e:
        components["cache"] = f"unhealthy: {str(e)}"
    
    # 确定总体状态
    overall_status = "healthy" if all("healthy" in status for status in components.values()) else "degraded"
    
    return {
        "status": overall_status,
        "version": "2.0.0",
        "uptime_seconds": round(uptime, 2),
        "components": components,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/metrics")
async def get_metrics():
    """获取应用指标"""
    uptime = time.time() - APP_START_TIME
    
    # 缓存统计
    cache_stats = cache_manager.get_stats()
    
    # 系统指标
    metrics = {
        "uptime_seconds": round(uptime, 2),
        "cache_stats": cache_stats,
        "database_pools": {
            "postgresql_pools": len(db_manager._pg_pools),
            "redis_pools": len(db_manager._redis_pools),
            "sqlalchemy_engines": len(db_manager._sqlalchemy_engines)
        }
    }
    
    # 添加系统资源指标（如果psutil可用）
    try:
        import psutil
        metrics["system"] = {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "process_count": len(psutil.pids())
        }
    except ImportError:
        metrics["system"] = {"note": "psutil not available"}
    
    return {
        "success": True,
        "data": metrics,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


# 注册API路由

# v1 API路由
app.include_router(v1_router, prefix="/api")

# 向后兼容的旧路由
app.include_router(namespace_router_old, prefix="/api")
app.include_router(backlog_router_old, prefix="/api")

# 简化的队列API路由（兼容性）
@app.get("/api/queues/{namespace}")
async def get_queues_legacy(namespace: str):
    """获取队列列表（兼容旧版本）"""
    try:
        from api.v1.queues import list_queues
        from dependencies import get_validated_namespace, get_redis_client, get_pg_connection, get_namespace_connection, get_request_metrics
        
        # 模拟依赖注入
        validated_namespace = namespace
        
        # 这里需要实际的依赖注入逻辑
        # 暂时返回简化响应
        return {
            "success": True,
            "data": []  # 返回空列表，实际应该调用新的API
        }
    except Exception as e:
        logger.error(f"获取队列列表失败（兼容接口）: {e}")
        return {"success": False, "error": str(e)}


# 开发工具路由
if os.getenv("DEBUG", "false").lower() == "true":
    @app.get("/debug/cache")
    async def debug_cache():
        """调试缓存状态"""
        return {
            "stats": cache_manager.get_stats(),
            "local_cache_keys": list(cache_manager.local_cache.keys())[:20],  # 只显示前20个
            "redis_connected": cache_manager.redis_client is not None
        }
    
    @app.post("/debug/cache/clear")
    async def debug_clear_cache():
        """清空缓存"""
        cleared = await cache_manager.clear_pattern("")
        return {"cleared_items": cleared}


def run_server():
    """运行开发服务器"""
    import uvicorn
    
    port = int(os.getenv("PORT", "8002"))
    host = os.getenv("HOST", "0.0.0.0")
    reload = os.getenv("DEBUG", "false").lower() == "true"
    
    logger.info(f"启动服务器: http://{host}:{port}")
    logger.info(f"API文档: http://{host}:{port}/docs")
    logger.info(f"调试模式: {reload}")
    
    uvicorn.run(
        "main_v2:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    run_server()