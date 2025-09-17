"""
Database connection management and utilities
"""
import asyncio
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any, AsyncGenerator
import asyncpg
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
import logging

from .exceptions import DatabaseConnectionError

logger = logging.getLogger(__name__)


class DatabaseManager:
    """数据库连接管理器"""
    
    def __init__(self):
        self._pg_pools: Dict[str, asyncpg.Pool] = {}
        self._redis_pools: Dict[str, redis.ConnectionPool] = {}
        self._sqlalchemy_engines: Dict[str, Any] = {}
        self._session_makers: Dict[str, async_sessionmaker] = {}
    
    async def get_pg_pool(self, connection_string: str, pool_name: str = "default") -> asyncpg.Pool:
        """获取PostgreSQL连接池"""
        if pool_name not in self._pg_pools:
            try:
                # 解析连接字符串
                if connection_string.startswith('postgresql://'):
                    connection_string = connection_string.replace('postgresql://', '')
                elif connection_string.startswith('postgresql+asyncpg://'):
                    connection_string = connection_string.replace('postgresql+asyncpg://', '')
                
                # 分离认证和主机信息
                auth, host_info = connection_string.split('@')
                user, password = auth.split(':')
                host_port, database = host_info.split('/')
                host, port = host_port.split(':')
                
                pool = await asyncpg.create_pool(
                    host=host,
                    port=int(port),
                    user=user,
                    password=password,
                    database=database,
                    min_size=2,
                    max_size=10,
                    command_timeout=30
                )
                
                self._pg_pools[pool_name] = pool
                logger.info(f"PostgreSQL连接池已创建: {pool_name}")
                
            except Exception as e:
                logger.error(f"创建PostgreSQL连接池失败: {e}")
                raise DatabaseConnectionError(f"PostgreSQL connection failed: {e}")
        
        return self._pg_pools[pool_name]
    
    async def get_redis_client(self, connection_string: str, pool_name: str = "default") -> redis.Redis:
        """获取Redis客户端"""
        if pool_name not in self._redis_pools:
            try:
                pool = redis.ConnectionPool.from_url(
                    connection_string,
                    max_connections=20,
                    decode_responses=False  # 保持原始字节格式
                )
                self._redis_pools[pool_name] = pool
                logger.info(f"Redis连接池已创建: {pool_name}")
                
            except Exception as e:
                logger.error(f"创建Redis连接池失败: {e}")
                raise DatabaseConnectionError(f"Redis connection failed: {e}")
        
        return redis.Redis(connection_pool=self._redis_pools[pool_name])
    
    def get_sqlalchemy_session_maker(
        self, 
        connection_string: str, 
        pool_name: str = "default"
    ) -> async_sessionmaker[AsyncSession]:
        """获取SQLAlchemy会话工厂"""
        if pool_name not in self._session_makers:
            try:
                # 确保使用asyncpg驱动
                if connection_string.startswith('postgresql://'):
                    connection_string = connection_string.replace('postgresql://', 'postgresql+asyncpg://')
                
                engine = create_async_engine(
                    connection_string,
                    pool_size=5,
                    max_overflow=10,
                    pool_timeout=30,
                    pool_recycle=3600,
                    echo=False  # 生产环境关闭SQL日志
                )
                
                session_maker = async_sessionmaker(
                    engine,
                    class_=AsyncSession,
                    expire_on_commit=False
                )
                
                self._sqlalchemy_engines[pool_name] = engine
                self._session_makers[pool_name] = session_maker
                logger.info(f"SQLAlchemy会话工厂已创建: {pool_name}")
                
            except Exception as e:
                logger.error(f"创建SQLAlchemy会话工厂失败: {e}")
                raise DatabaseConnectionError(f"SQLAlchemy connection failed: {e}")
        
        return self._session_makers[pool_name]
    
    @asynccontextmanager
    async def get_pg_connection(self, pool_name: str = "default") -> AsyncGenerator[asyncpg.Connection, None]:
        """获取PostgreSQL连接上下文管理器"""
        if pool_name not in self._pg_pools:
            raise DatabaseConnectionError(f"PostgreSQL pool '{pool_name}' not found")
        
        pool = self._pg_pools[pool_name]
        async with pool.acquire() as conn:
            yield conn
    
    @asynccontextmanager
    async def get_sqlalchemy_session(self, pool_name: str = "default") -> AsyncGenerator[AsyncSession, None]:
        """获取SQLAlchemy会话上下文管理器"""
        if pool_name not in self._session_makers:
            raise DatabaseConnectionError(f"SQLAlchemy session maker '{pool_name}' not found")
        
        session_maker = self._session_makers[pool_name]
        async with session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def close_all(self):
        """关闭所有连接"""
        # 关闭PostgreSQL连接池
        for name, pool in self._pg_pools.items():
            try:
                await pool.close()
                logger.info(f"PostgreSQL连接池已关闭: {name}")
            except Exception as e:
                logger.error(f"关闭PostgreSQL连接池失败 {name}: {e}")
        
        # 关闭Redis连接池
        for name, pool in self._redis_pools.items():
            try:
                await pool.disconnect()
                logger.info(f"Redis连接池已关闭: {name}")
            except Exception as e:
                logger.error(f"关闭Redis连接池失败 {name}: {e}")
        
        # 关闭SQLAlchemy引擎
        for name, engine in self._sqlalchemy_engines.items():
            try:
                await engine.dispose()
                logger.info(f"SQLAlchemy引擎已关闭: {name}")
            except Exception as e:
                logger.error(f"关闭SQLAlchemy引擎失败 {name}: {e}")
        
        # 清空缓存
        self._pg_pools.clear()
        self._redis_pools.clear()
        self._sqlalchemy_engines.clear()
        self._session_makers.clear()


# 全局数据库管理器实例
db_manager = DatabaseManager()


# 数据库模型基类
class Base(DeclarativeBase):
    pass


# 便捷函数
async def get_pg_pool(connection_string: str, pool_name: str = "default") -> asyncpg.Pool:
    """便捷函数：获取PostgreSQL连接池"""
    return await db_manager.get_pg_pool(connection_string, pool_name)


async def get_redis_client(connection_string: str, pool_name: str = "default") -> redis.Redis:
    """便捷函数：获取Redis客户端"""
    return await db_manager.get_redis_client(connection_string, pool_name)


def get_session_maker(connection_string: str, pool_name: str = "default") -> async_sessionmaker[AsyncSession]:
    """便捷函数：获取SQLAlchemy会话工厂"""
    return db_manager.get_sqlalchemy_session_maker(connection_string, pool_name)