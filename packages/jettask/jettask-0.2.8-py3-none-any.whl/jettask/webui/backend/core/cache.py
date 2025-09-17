"""
Caching utilities for JetTask WebUI Backend
"""
import json
import hashlib
from typing import Any, Optional, Dict, Callable, TypeVar, Union
from functools import wraps
import asyncio
import time
import logging

import redis.asyncio as redis

logger = logging.getLogger(__name__)

T = TypeVar('T')


class CacheManager:
    """缓存管理器"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client
        self.local_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0
        }
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """生成缓存键"""
        key_data = f"{prefix}:{args}:{sorted(kwargs.items())}"
        return f"jettask:cache:{hashlib.md5(key_data.encode()).hexdigest()}"
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        try:
            # 先检查本地缓存
            if key in self.local_cache:
                local_data = self.local_cache[key]
                if local_data['expires'] > time.time():
                    self.cache_stats['hits'] += 1
                    return local_data['value']
                else:
                    del self.local_cache[key]
            
            # 检查Redis缓存
            if self.redis_client:
                value = await self.redis_client.get(key)
                if value:
                    self.cache_stats['hits'] += 1
                    return json.loads(value)
            
            self.cache_stats['misses'] += 1
            return None
            
        except Exception as e:
            logger.warning(f"缓存获取失败: {e}")
            self.cache_stats['misses'] += 1
            return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: int = 300,
        local_only: bool = False
    ) -> bool:
        """设置缓存值"""
        try:
            # 设置本地缓存
            if ttl <= 60 or local_only:  # 短期缓存或仅本地缓存
                self.local_cache[key] = {
                    'value': value,
                    'expires': time.time() + ttl
                }
            
            # 设置Redis缓存
            if self.redis_client and not local_only:
                await self.redis_client.setex(
                    key, 
                    ttl, 
                    json.dumps(value, default=str)
                )
            
            self.cache_stats['sets'] += 1
            return True
            
        except Exception as e:
            logger.warning(f"缓存设置失败: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """删除缓存"""
        try:
            # 删除本地缓存
            if key in self.local_cache:
                del self.local_cache[key]
            
            # 删除Redis缓存
            if self.redis_client:
                await self.redis_client.delete(key)
            
            self.cache_stats['deletes'] += 1
            return True
            
        except Exception as e:
            logger.warning(f"缓存删除失败: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """根据模式删除缓存"""
        try:
            deleted = 0
            
            # 清理本地缓存
            keys_to_delete = [k for k in self.local_cache.keys() if pattern in k]
            for key in keys_to_delete:
                del self.local_cache[key]
                deleted += 1
            
            # 清理Redis缓存
            if self.redis_client:
                keys = await self.redis_client.keys(f"*{pattern}*")
                if keys:
                    await self.redis_client.delete(*keys)
                    deleted += len(keys)
            
            self.cache_stats['deletes'] += deleted
            return deleted
            
        except Exception as e:
            logger.warning(f"批量删除缓存失败: {e}")
            return 0
    
    def cleanup_expired(self):
        """清理过期的本地缓存"""
        current_time = time.time()
        expired_keys = [
            key for key, data in self.local_cache.items()
            if data['expires'] <= current_time
        ]
        for key in expired_keys:
            del self.local_cache[key]
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        hit_rate = (
            self.cache_stats['hits'] / 
            (self.cache_stats['hits'] + self.cache_stats['misses'])
            if (self.cache_stats['hits'] + self.cache_stats['misses']) > 0
            else 0
        )
        
        return {
            **self.cache_stats,
            'hit_rate': hit_rate,
            'local_cache_size': len(self.local_cache)
        }


# 全局缓存管理器
cache_manager = CacheManager()


def cache_result(
    ttl: int = 300,
    key_prefix: str = "default",
    local_only: bool = False
):
    """缓存装饰器"""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            # 生成缓存键
            cache_key = cache_manager._generate_key(
                f"{key_prefix}:{func.__name__}",
                *args,
                **kwargs
            )
            
            # 尝试从缓存获取
            cached_result = await cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 执行函数
            result = await func(*args, **kwargs)
            
            # 缓存结果
            await cache_manager.set(cache_key, result, ttl, local_only)
            
            return result
        
        return wrapper
    return decorator


def invalidate_cache(pattern: str):
    """缓存失效装饰器"""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            result = await func(*args, **kwargs)
            # 执行后清理相关缓存
            await cache_manager.clear_pattern(pattern)
            return result
        
        return wrapper
    return decorator


# 预定义的缓存配置
CACHE_CONFIGS = {
    'queue_stats': {'ttl': 300, 'key_prefix': 'queue_stats'},  # 5分钟
    'task_details': {'ttl': 60, 'key_prefix': 'task_details'},  # 1分钟  
    'namespace_config': {'ttl': 1800, 'key_prefix': 'namespace_config'},  # 30分钟
    'monitoring_data': {'ttl': 30, 'key_prefix': 'monitoring_data', 'local_only': True},  # 30秒，仅本地
}