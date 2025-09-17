"""
Dependency injection for JetTask WebUI Backend
"""
from typing import Optional, AsyncGenerator
from fastapi import Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis

from core.database import db_manager, DatabaseManager
from core.cache import cache_manager, CacheManager
from core.exceptions import NamespaceNotFoundError, DatabaseConnectionError
from namespace_data_access import get_namespace_data_access
import logging

logger = logging.getLogger(__name__)


# 依赖注入函数

async def get_database_manager() -> DatabaseManager:
    """获取数据库管理器"""
    return db_manager


async def get_cache_manager() -> CacheManager:
    """获取缓存管理器"""
    return cache_manager


async def get_namespace_from_path(namespace: str = "default") -> str:
    """从路径参数获取命名空间"""
    if not namespace:
        raise HTTPException(status_code=400, detail="Namespace is required")
    return namespace


async def get_namespace_from_header(
    x_namespace: Optional[str] = Header(None, alias="X-Namespace")
) -> str:
    """从请求头获取命名空间"""
    return x_namespace or "default"


async def get_current_namespace(
    path_namespace: str = Depends(get_namespace_from_path),
    header_namespace: str = Depends(get_namespace_from_header)
) -> str:
    """获取当前命名空间（优先使用路径参数）"""
    return path_namespace if path_namespace != "default" else header_namespace


async def validate_namespace(namespace: str) -> str:
    """验证命名空间是否存在"""
    try:
        namespace_data_access = get_namespace_data_access()
        # 尝试获取命名空间连接来验证其存在
        conn = await namespace_data_access.manager.get_connection(namespace)
        if not conn:
            raise NamespaceNotFoundError(namespace)
        return namespace
    except Exception as e:
        logger.error(f"命名空间验证失败 {namespace}: {e}")
        raise NamespaceNotFoundError(namespace)


async def get_validated_namespace(
    namespace: str = Depends(get_current_namespace)
) -> str:
    """获取并验证命名空间"""
    return await validate_namespace(namespace)


async def get_pg_connection(
    namespace: str = Depends(get_validated_namespace)
) -> AsyncGenerator[object, None]:
    """获取PostgreSQL连接"""
    try:
        namespace_data_access = get_namespace_data_access()
        conn = await namespace_data_access.manager.get_connection(namespace)
        
        if not conn.AsyncSessionLocal:
            raise DatabaseConnectionError("PostgreSQL not configured for this namespace")
            
        async with conn.AsyncSessionLocal() as session:
            yield session
            
    except DatabaseConnectionError:
        raise
    except Exception as e:
        logger.error(f"获取PostgreSQL连接失败: {e}")
        raise DatabaseConnectionError(f"PostgreSQL connection failed: {e}")


async def get_redis_client(
    namespace: str = Depends(get_validated_namespace)
) -> AsyncGenerator[redis.Redis, None]:
    """获取Redis客户端"""
    try:
        namespace_data_access = get_namespace_data_access()
        conn = await namespace_data_access.manager.get_connection(namespace)
        
        redis_client = await conn.get_redis_client(decode=False)
        
        try:
            yield redis_client
        finally:
            await redis_client.aclose()
            
    except Exception as e:
        logger.error(f"获取Redis客户端失败: {e}")
        raise DatabaseConnectionError(f"Redis connection failed: {e}")


async def get_namespace_connection(
    namespace: str = Depends(get_validated_namespace)
):
    """获取命名空间连接对象"""
    try:
        namespace_data_access = get_namespace_data_access()
        return await namespace_data_access.manager.get_connection(namespace)
    except Exception as e:
        logger.error(f"获取命名空间连接失败: {e}")
        raise DatabaseConnectionError(f"Namespace connection failed: {e}")


# 权限和认证相关依赖（预留）

async def get_current_user(
    authorization: Optional[str] = Header(None)
) -> Optional[dict]:
    """获取当前用户（预留接口）"""
    # 这里可以实现JWT令牌解析、用户认证等逻辑
    # 目前返回None表示匿名用户
    return None


async def require_auth(
    current_user: Optional[dict] = Depends(get_current_user)
) -> dict:
    """要求用户认证（预留接口）"""
    # 这里可以实现认证检查逻辑
    # 目前直接返回匿名用户
    return current_user or {"id": "anonymous", "role": "user"}


async def require_admin(
    current_user: dict = Depends(require_auth)
) -> dict:
    """要求管理员权限（预留接口）"""
    # 这里可以实现权限检查逻辑
    # 目前直接返回用户
    return current_user


# 请求验证相关依赖

def validate_page_params(page: int = 1, page_size: int = 20) -> tuple[int, int]:
    """验证分页参数"""
    if page < 1:
        raise HTTPException(status_code=400, detail="Page must be >= 1")
    if page_size < 1 or page_size > 100:
        raise HTTPException(status_code=400, detail="Page size must be between 1 and 100")
    return page, page_size


def validate_time_range(
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    time_range: Optional[str] = None
) -> dict:
    """验证时间范围参数"""
    from datetime import datetime, timedelta
    
    result = {}
    
    if time_range:
        # 预设时间范围
        time_map = {
            '15m': timedelta(minutes=15),
            '30m': timedelta(minutes=30),
            '1h': timedelta(hours=1),
            '3h': timedelta(hours=3),
            '6h': timedelta(hours=6),
            '12h': timedelta(hours=12),
            '24h': timedelta(hours=24),
            '3d': timedelta(days=3),
            '7d': timedelta(days=7),
            '30d': timedelta(days=30)
        }
        
        if time_range not in time_map:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid time_range: {time_range}"
            )
        
        now = datetime.now()
        result['end_time'] = now
        result['start_time'] = now - time_map[time_range]
        result['time_range'] = time_range
    
    elif start_time or end_time:
        # 自定义时间范围
        try:
            if start_time:
                result['start_time'] = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            if end_time:
                result['end_time'] = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            
            if result.get('start_time') and result.get('end_time'):
                if result['start_time'] >= result['end_time']:
                    raise HTTPException(
                        status_code=400,
                        detail="start_time must be before end_time"
                    )
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid datetime format: {e}"
            )
    
    else:
        # 默认最近1小时
        now = datetime.now()
        result['end_time'] = now
        result['start_time'] = now - timedelta(hours=1)
        result['time_range'] = '1h'
    
    return result


# 性能监控相关依赖

class RequestMetrics:
    """请求指标收集器"""
    
    def __init__(self):
        self.start_time = None
        self.namespace = None
        self.endpoint = None
    
    def start(self, namespace: str, endpoint: str):
        import time
        self.start_time = time.time()
        self.namespace = namespace
        self.endpoint = endpoint
    
    def finish(self):
        if self.start_time:
            import time
            duration = time.time() - self.start_time
            logger.info(
                f"API请求完成: {self.endpoint} "
                f"namespace={self.namespace} "
                f"duration={duration:.3f}s"
            )


async def get_request_metrics() -> RequestMetrics:
    """获取请求指标收集器"""
    return RequestMetrics()