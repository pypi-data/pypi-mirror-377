"""
任务中心客户端 - JetTask App使用的客户端库
"""
import os
import aiohttp
import asyncio
from typing import Optional, Dict, Any
from .models.namespace import TaskCenterConfig
import logging

logger = logging.getLogger(__name__)


class TaskCenterClient:
    """任务中心客户端"""
    
    def __init__(self, task_center_url: Optional[str] = None):
        """
        初始化任务中心客户端
        
        Args:
            task_center_url: 任务中心配置URL，支持两种格式:
                - HTTP格式: http://localhost:8001/api/namespaces/{namespace_id}
                - 旧格式: taskcenter://namespace/{namespace_id} (向后兼容)
        """
        self.task_center_url = task_center_url
        self._session: Optional[aiohttp.ClientSession] = None
        self._cached_config: Optional[Dict[str, Any]] = None
        self._namespace_id: Optional[str] = None
        self._namespace_name: Optional[str] = None  # 添加命名空间名称
        
        # 解析URL
        self._config_url = task_center_url  # 用于获取配置的URL
        if task_center_url:
            if task_center_url.startswith("http://") or task_center_url.startswith("https://"):
                # HTTP格式，支持新格式: http://localhost:8001/api/namespaces/{name}
                import re
                # 匹配新格式：使用名称而非ID
                match = re.search(r'/namespaces/([^/]+)$', task_center_url)
                if match:
                    self._namespace_name = match.group(1)
                    # 新格式直接使用URL，不需要添加/config
            elif task_center_url.startswith("taskcenter://"):
                # 旧格式，转换为HTTP格式
                parts = task_center_url.replace("taskcenter://", "").split("/")
                if len(parts) >= 2 and parts[0] == "namespace":
                    # 旧格式使用的是ID，转换为按名称查找
                    self._namespace_name = parts[1]  # 假设传入的也是名称
                    base_url = os.getenv("TASK_CENTER_BASE_URL", "http://localhost:8001")
                    self._config_url = f"{base_url}/api/namespaces/{self._namespace_name}"
        
    @property
    def is_enabled(self) -> bool:
        """是否启用任务中心"""
        return self.task_center_url is not None
    
    @property
    def namespace_id(self) -> Optional[str]:
        """获取命名空间ID"""
        return self._namespace_id
    
    @property
    def namespace_prefix(self) -> str:
        """获取Redis key前缀"""
        # 优先使用namespace_name，不再添加tc:前缀
        if self._namespace_name:
            return self._namespace_name
        # 如果配置已加载，使用其中的名称
        elif self._cached_config and self._cached_config.get('namespace_name'):
            return self._cached_config['namespace_name']
        # 默认前缀
        return "jettask"
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """获取HTTP会话"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def get_config(self) -> Optional[Dict[str, Any]]:
        """
        从任务中心获取配置
        
        Returns:
            包含redis_config和pg_config的字典
        """
        if not self.is_enabled:
            return None
        
        # 如果已缓存，直接返回
        if self._cached_config:
            return self._cached_config
            
        try:
            session = await self._get_session()
            # 使用配置URL（可能带有/config后缀）
            async with session.get(self._config_url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    self._namespace_name = data.get('name')  # 保存命名空间名称
                    self._cached_config = {
                        'redis_config': data.get('redis_config'),
                        'pg_config': data.get('pg_config'),
                        'namespace_name': data.get('name'),
                        'namespace_id': self._namespace_id,
                        'version': data.get('version', 1)  # 添加版本号
                    }
                    return self._cached_config
                else:
                    logger.error(f"Failed to get config from task center: {resp.status}")
                    return None
        except Exception as e:
            logger.error(f"Error getting config from task center: {e}")
            return None
    
    async def get_task_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        从任务中心获取任务结果（当Redis中不存在时）
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务结果字典
        """
        if not self.is_enabled or not self._namespace_id:
            return None
            
        try:
            session = await self._get_session()
            # 从配置URL推导出任务结果URL
            base_url = self.task_center_url.replace(f"/namespace/{self._namespace_id}/config", "")
            url = f"{base_url}/namespace/{self._namespace_id}/task/{task_id}/result"
            async with session.get(url) as resp:
                if resp.status == 200:
                    return await resp.json()
                elif resp.status == 404:
                    return None
                else:
                    logger.error(f"Failed to get task result from task center: {resp.status}")
                    return None
        except Exception as e:
            logger.error(f"Error getting task result from task center: {e}")
            return None
    
    
    async def close(self):
        """关闭客户端"""
        if self._session:
            await self._session.close()