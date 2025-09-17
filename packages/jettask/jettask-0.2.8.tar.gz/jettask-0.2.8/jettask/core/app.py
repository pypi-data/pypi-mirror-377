import os
import sys
import time
from datetime import datetime
from ..utils.serializer import dumps, loads, dumps_str, loads_str
import signal
import socket
import asyncio
import logging
import contextlib
import importlib
import multiprocessing
from typing import List
from collections import defaultdict, deque

import redis
from redis import asyncio as aioredis
from watchdog.observers import Observer

from .task import Task
from .event_pool import EventPool
from ..executors import AsyncioExecutor, MultiAsyncioExecutor
from ..monitoring import FileChangeHandler
from ..utils import gen_task_name
from ..exceptions import TaskTimeoutError, TaskExecutionError, TaskNotFoundError

logger = logging.getLogger('app')

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# 尝试导入性能优化库
try:
    import uvloop
    UVLOOP_AVAILABLE = True
    # 自动启用uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    logger.debug("Using uvloop for better performance")
except ImportError:
    UVLOOP_AVAILABLE = False

_on_app_finalizers = set()

# 全局连接池复用
_redis_pools = {}
_async_redis_pools = {}
# 专门用于二进制数据的连接池（用于Stream操作）
_binary_redis_pools = {}
_async_binary_redis_pools = {}

def get_redis_pool(redis_url: str, max_connections: int = 200):
    """获取或创建Redis连接池"""
    if redis_url not in _redis_pools:
        # 构建socket keepalive选项，仅在Linux上使用
        socket_keepalive_options = {}
        if hasattr(socket, 'TCP_KEEPIDLE'):
            socket_keepalive_options[socket.TCP_KEEPIDLE] = 1
        if hasattr(socket, 'TCP_KEEPINTVL'):
            socket_keepalive_options[socket.TCP_KEEPINTVL] = 3
        if hasattr(socket, 'TCP_KEEPCNT'):
            socket_keepalive_options[socket.TCP_KEEPCNT] = 5
        
        _redis_pools[redis_url] = redis.ConnectionPool.from_url(
            redis_url, 
            decode_responses=True,
            max_connections=max_connections,
            retry_on_timeout=True,
            retry_on_error=[ConnectionError, TimeoutError],
            socket_keepalive=True,
            socket_keepalive_options=socket_keepalive_options if socket_keepalive_options else None,
            health_check_interval=30,
            # 优化超时配置以处理高负载
            socket_connect_timeout=10,  # 增加连接超时时间
            socket_timeout=15,          # 增加读取超时时间，避免频繁超时
        )
    return _redis_pools[redis_url]

def get_async_redis_pool(redis_url: str, max_connections: int = 200):
    """获取或创建异步Redis连接池"""
    if redis_url not in _async_redis_pools:
        # 构建socket keepalive选项，仅在Linux上使用
        socket_keepalive_options = {}
        if hasattr(socket, 'TCP_KEEPIDLE'):
            socket_keepalive_options[socket.TCP_KEEPIDLE] = 1
        if hasattr(socket, 'TCP_KEEPINTVL'):
            socket_keepalive_options[socket.TCP_KEEPINTVL] = 3
        if hasattr(socket, 'TCP_KEEPCNT'):
            socket_keepalive_options[socket.TCP_KEEPCNT] = 5
        
        _async_redis_pools[redis_url] = aioredis.ConnectionPool.from_url(
            redis_url,
            decode_responses=True,
            max_connections=max_connections,
            retry_on_timeout=True,
            retry_on_error=[ConnectionError, TimeoutError],
            socket_keepalive=True,
            socket_keepalive_options=socket_keepalive_options if socket_keepalive_options else None,
            health_check_interval=30,
            # 优化超时配置以处理高负载
            socket_connect_timeout=10,  # 增加连接超时时间
            socket_timeout=15,          # 增加读取超时时间，避免频繁超时
        )
    return _async_redis_pools[redis_url]

def get_binary_redis_pool(redis_url: str, max_connections: int = 200):
    """获取或创建用于二进制数据的Redis连接池（Stream操作需要）"""
    if redis_url not in _binary_redis_pools:
        # 构建socket keepalive选项，仅在Linux上使用
        socket_keepalive_options = {}
        if hasattr(socket, 'TCP_KEEPIDLE'):
            socket_keepalive_options[socket.TCP_KEEPIDLE] = 1
        if hasattr(socket, 'TCP_KEEPINTVL'):
            socket_keepalive_options[socket.TCP_KEEPINTVL] = 3
        if hasattr(socket, 'TCP_KEEPCNT'):
            socket_keepalive_options[socket.TCP_KEEPCNT] = 5
        
        _binary_redis_pools[redis_url] = redis.ConnectionPool.from_url(
            redis_url, 
            decode_responses=False,  # 不解码，因为Stream数据是msgpack二进制
            max_connections=max_connections,
            retry_on_timeout=True,
            retry_on_error=[ConnectionError, TimeoutError],
            socket_keepalive=True,
            socket_keepalive_options=socket_keepalive_options if socket_keepalive_options else None,
            health_check_interval=30,
            # 优化超时配置以处理高负载
            socket_connect_timeout=10,  # 增加连接超时时间
            socket_timeout=15,          # 增加读取超时时间，避免频繁超时
        )
    return _binary_redis_pools[redis_url]

def get_async_binary_redis_pool(redis_url: str, max_connections: int = 200):
    """获取或创建用于二进制数据的异步Redis连接池（Stream操作需要）"""
    if redis_url not in _async_binary_redis_pools:
        # 构建socket keepalive选项，仅在Linux上使用
        socket_keepalive_options = {}
        if hasattr(socket, 'TCP_KEEPIDLE'):
            socket_keepalive_options[socket.TCP_KEEPIDLE] = 1
        if hasattr(socket, 'TCP_KEEPINTVL'):
            socket_keepalive_options[socket.TCP_KEEPINTVL] = 3
        if hasattr(socket, 'TCP_KEEPCNT'):
            socket_keepalive_options[socket.TCP_KEEPCNT] = 5
        
        _async_binary_redis_pools[redis_url] = aioredis.ConnectionPool.from_url(
            redis_url,
            decode_responses=False,  # 不解码，因为Stream数据是msgpack二进制
            max_connections=max_connections,
            retry_on_timeout=True,
            retry_on_error=[ConnectionError, TimeoutError],
            socket_keepalive=True,
            socket_keepalive_options=socket_keepalive_options if socket_keepalive_options else None,
            health_check_interval=30,
            # 优化超时配置以处理高负载
            socket_connect_timeout=10,  # 增加连接超时时间
            socket_timeout=15,          # 增加读取超时时间，避免频繁超时
        )
    return _async_binary_redis_pools[redis_url]


def connect_on_app_finalize(callback):
    """Connect callback to be called when any app is finalized."""
    _on_app_finalizers.add(callback)
    return callback


class Jettask(object):
    # Lua脚本定义为类常量，避免重复定义
    _LUA_SCRIPT_DELAYED_TASKS = """
    local prefix = ARGV[1]
    local current_time = tonumber(ARGV[2])
    local results = {}
    
    -- 从ARGV[3]开始，每5个参数为一组任务信息
    -- [stream_key, stream_data, execute_at, delay_seconds, queue]
    for i = 3, #ARGV, 5 do
        local stream_key = ARGV[i]
        local stream_data = ARGV[i+1]
        local execute_at = tonumber(ARGV[i+2])
        local delay_seconds = tonumber(ARGV[i+3])
        local queue = ARGV[i+4]
        
        -- 使用Hash存储所有队列的offset
        local offsets_hash = prefix .. ':QUEUE_OFFSETS'
        -- 使用HINCRBY原子递增offset
        local offset = redis.call('HINCRBY', offsets_hash, queue, 1)
        
        -- 1. 添加消息到Stream（包含offset字段）
        local stream_id = redis.call('XADD', stream_key, '*', 
            'data', stream_data,
            'offset', offset)
        
        -- 2. 添加到延迟队列ZSET
        local delayed_queue_key = prefix .. ':DELAYED_QUEUE:' .. queue
        redis.call('ZADD', delayed_queue_key, execute_at, stream_id)
        
        -- 3. 设置任务状态Hash（只存储status，其他信息从Stream获取）
        local task_key = prefix .. ':TASK:' .. stream_id
        redis.call('HSET', task_key, 'status', 'delayed')
        
        -- 4. 设置过期时间
        local expire_seconds = math.max(1, math.floor(delay_seconds + 3600))
        redis.call('EXPIRE', task_key, expire_seconds)
        
        -- 保存stream_id到结果
        table.insert(results, stream_id)
    end
    
    return results
    """
    
    _LUA_SCRIPT_NORMAL_TASKS = """
    local prefix = ARGV[1]
    local current_time = ARGV[2]
    local results = {}
    
    -- 从ARGV[3]开始，每2个参数为一组任务信息
    -- [stream_key, stream_data]
    for i = 3, #ARGV, 2 do
        local stream_key = ARGV[i]
        local stream_data = ARGV[i+1]
        
        -- 从stream_key中提取队列名（格式: prefix:STREAM:queue_name）
        local queue_name = string.match(stream_key, prefix .. ':STREAM:(.*)')
        
        -- 获取并递增offset
        local offset_key = prefix .. ':STREAM:' .. queue_name .. ':next_offset'
        local offset = redis.call('INCR', offset_key)
        
        -- 1. 添加消息到Stream（包含offset字段）
        local stream_id = redis.call('XADD', stream_key, '*', 
            'data', stream_data,
            'offset', offset)
        
        -- 2. 设置任务状态Hash（只存储status）
        local task_key = prefix .. ':TASK:' .. stream_id
        redis.call('HSET', task_key, 'status', 'pending')
        
        -- 3. 设置过期时间（1小时）
        redis.call('EXPIRE', task_key, 3600)
        
        -- 保存stream_id到结果
        table.insert(results, stream_id)
    end
    
    return results
    """

    def __init__(self, redis_url: str = None, include: list = None, max_connections: int = 200, 
                 consumer_strategy: str = None, consumer_config: dict = None, tasks=None,
                 redis_prefix: str = None, scheduler_config: dict = None, pg_url: str = None,
                 task_center=None) -> None:
        self._tasks = tasks or {}
        self._queue_tasks = {}  # 记录每个队列对应的任务列表
        self.asyncio = False
        self.include = include or []
        
        # 任务中心相关属性
        self.task_center = None  # 将通过mount_task_center方法挂载或初始化时指定
        self._task_center_config = None
        self._original_redis_url = redis_url
        self._original_pg_url = pg_url
        
        self.redis_url = redis_url
        self.pg_url = pg_url  # 存储PostgreSQL URL
        self.max_connections = max_connections
        self.consumer_strategy = consumer_strategy
        self.consumer_config = consumer_config or {}
        self.scheduler_config = scheduler_config or {}
        
        # Redis prefix configuration
        self.redis_prefix = redis_prefix or "jettask"
        
        # 如果初始化时提供了task_center，直接挂载
        if task_center:
            self.mount_task_center(task_center)
        
        # Update prefixes with the configured prefix using colon namespace
        self.STATUS_PREFIX = f"{self.redis_prefix}:STATUS:"
        self.RESULT_PREFIX = f"{self.redis_prefix}:RESULT:"
        
        # 预编译常用操作，减少运行时开销
        self._loads = loads
        self._dumps = dumps
        
        # 调度器相关
        self.scheduler = None
        self.scheduler_manager = None
        
        self._status_prefix = self.STATUS_PREFIX
        self._result_prefix = self.RESULT_PREFIX
        
        # 初始化清理状态，但不注册处理器
        self._cleanup_done = False
        self._should_exit = False
        self._worker_started = False
        self._handlers_registered = False
    
    async def _load_config_from_task_center_async(self):
        """异步加载任务中心配置"""
        try:
            if not self.task_center:
                return False
            
            # 连接并获取配置
            connected = await self.task_center.connect()
            if not connected:
                return False
            
            config = {
                'redis_config': self.task_center.redis_config,
                'pg_config': self.task_center.pg_config,
                'namespace_name': self.task_center.namespace_name,
                'version': self.task_center.version
            }
            
            if config['redis_config']:
                # 任务中心配置优先级高于手动配置
                redis_config = config.get('redis_config', {})
                pg_config = config.get('pg_config', {})
                # 构建Redis URL
                if redis_config:
                    redis_host = redis_config.get('host', 'localhost')
                    redis_port = redis_config.get('port', 6379)
                    redis_password = redis_config.get('password')
                    redis_db = redis_config.get('db', 0)
                    
                    if redis_password:
                        self.redis_url = f"redis://:{redis_password}@{redis_host}:{redis_port}/{redis_db}"
                    else:
                        self.redis_url = f"redis://{redis_host}:{redis_port}/{redis_db}"
                    
                    logger.info(f"从任务中心加载Redis配置: {redis_host}:{redis_port}/{redis_db}")
                
                # 构建PostgreSQL URL
                if pg_config:
                    pg_host = pg_config.get('host', 'localhost')
                    pg_port = pg_config.get('port', 5432)
                    pg_user = pg_config.get('user', 'postgres')
                    pg_password = pg_config.get('password', '')
                    pg_database = pg_config.get('database', 'jettask')
                    
                    self.pg_url = f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_database}"
                    logger.info(f"从任务中心加载PostgreSQL配置: {pg_host}:{pg_port}/{pg_database}")
                
                # 保存配置供后续使用
                self._task_center_config = config
                
                # 更新Redis前缀为命名空间名称
                if self.task_center and self.task_center.redis_prefix != "jettask":
                    self.redis_prefix = self.task_center.redis_prefix
                    # 更新相关前缀
                    self.STATUS_PREFIX = f"{self.redis_prefix}:STATUS:"
                    self.RESULT_PREFIX = f"{self.redis_prefix}:RESULT:"
                
                # 清理已缓存的Redis连接，强制重新创建
                if hasattr(self, '_redis'):
                    delattr(self, '_redis')
                if hasattr(self, '_async_redis'):
                    delattr(self, '_async_redis')
                if hasattr(self, '_ep'):
                    delattr(self, '_ep')
                    
                return True
        except Exception as e:
            logger.warning(f"从任务中心加载配置失败: {e}")
            return False
    
    def _load_config_from_task_center(self):
        """从任务中心加载配置"""
        try:
            import asyncio
            # 检查是否已经在事件循环中
            try:
                loop = asyncio.get_running_loop()
                # 已在事件循环中，无法同步加载
                return False
            except RuntimeError:
                # 不在事件循环中，可以创建新的
                loop = asyncio.new_event_loop()
                if self.task_center:
                    # 如果已经初始化，直接获取配置
                    if self.task_center._initialized:
                        config = self.task_center._config
                    else:
                        # 使用异步模式连接
                        success = loop.run_until_complete(self.task_center.connect(asyncio=True))
                        if success:
                            config = self.task_center._config
                        else:
                            config = None
                else:
                    config = None
                loop.close()
            
            if config:
                # 任务中心配置优先级高于手动配置
                redis_config = config.get('redis_config', {})
                pg_config = config.get('pg_config', {})
                # 构建Redis URL
                if redis_config:
                    redis_host = redis_config.get('host', 'localhost')
                    redis_port = redis_config.get('port', 6379)
                    redis_password = redis_config.get('password')
                    redis_db = redis_config.get('db', 0)
                    
                    if redis_password:
                        self.redis_url = f"redis://:{redis_password}@{redis_host}:{redis_port}/{redis_db}"
                    else:
                        self.redis_url = f"redis://{redis_host}:{redis_port}/{redis_db}"
                    
                    logger.info(f"从任务中心加载Redis配置: {redis_host}:{redis_port}/{redis_db}")
                
                # 构建PostgreSQL URL
                if pg_config:
                    pg_host = pg_config.get('host', 'localhost')
                    pg_port = pg_config.get('port', 5432)
                    pg_user = pg_config.get('user', 'postgres')
                    pg_password = pg_config.get('password', '')
                    pg_database = pg_config.get('database', 'jettask')
                    
                    self.pg_url = f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_database}"
                    logger.info(f"从任务中心加载PostgreSQL配置: {pg_host}:{pg_port}/{pg_database}")
                
                # 保存配置供后续使用
                self._task_center_config = config
                
                # 更新Redis前缀为命名空间名称
                if self.task_center and self.task_center.redis_prefix != "jettask":
                    self.redis_prefix = self.task_center.redis_prefix
                    # 更新相关前缀
                    self.STATUS_PREFIX = f"{self.redis_prefix}:STATUS:"
                    self.RESULT_PREFIX = f"{self.redis_prefix}:RESULT:"
                
                # 清理已缓存的Redis连接，强制重新创建
                if hasattr(self, '_redis'):
                    delattr(self, '_redis')
                if hasattr(self, '_async_redis'):
                    delattr(self, '_async_redis')
                if hasattr(self, '_ep'):
                    delattr(self, '_ep')
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            logger.warning(f"从任务中心加载配置失败，使用手动配置: {e}")
            # 恢复原始配置
            self.redis_url = self._original_redis_url
            self.pg_url = self._original_pg_url
    
    def mount_task_center(self, task_center):
        """
        挂载任务中心到Jettask应用
        
        如果task_center已经连接，会自动应用配置到当前app。
        
        Args:
            task_center: TaskCenter实例
            
        使用示例：
            from jettask.webui.task_center import TaskCenter
            
            # 创建任务中心客户端（可复用）
            task_center = TaskCenter("http://localhost:8001/api/namespaces/demo")
            await task_center.connect()  # 只需连接一次
            
            # 创建多个app实例，共享同一个task_center
            app1 = Jettask()
            app1.mount_task_center(task_center)  # 自动应用配置
            
            app2 = Jettask()
            app2.mount_task_center(task_center)  # 复用配置
        """
        self.task_center = task_center
        
        # 如果任务中心已连接，立即应用所有配置
        if task_center and task_center._initialized:
            # 应用Redis配置
            if task_center.redis_config:
                redis_url = task_center.get_redis_url()
                if redis_url:
                    self.redis_url = redis_url
                    
            # 应用PostgreSQL配置
            if task_center.pg_config:
                pg_url = task_center.get_pg_url()
                if pg_url:
                    self.pg_url = pg_url
            
            # 更新Redis前缀
            self.redis_prefix = task_center.redis_prefix
            # 更新相关前缀
            self.STATUS_PREFIX = f"{self.redis_prefix}:STATUS:"
            self.RESULT_PREFIX = f"{self.redis_prefix}:RESULT:"
            self.QUEUE_PREFIX = f"{self.redis_prefix}:QUEUE:"
            self.DELAYED_QUEUE_PREFIX = f"{self.redis_prefix}:DELAYED_QUEUE:"
            self.STREAM_PREFIX = f"{self.redis_prefix}:STREAM:"
            self.TASK_PREFIX = f"{self.redis_prefix}:TASK:"
            self.SCHEDULER_PREFIX = f"{self.redis_prefix}:SCHEDULED:"
            self.LOCK_PREFIX = f"{self.redis_prefix}:LOCK:"
            
            # 标记配置已加载
            self._task_center_config = {
                'redis_config': task_center.redis_config,
                'pg_config': task_center.pg_config,
                'namespace_name': task_center.namespace_name,
                'version': task_center.version
            }
    
    async def init_from_task_center(self):
        """
        从任务中心初始化配置（异步方法）
        
        在异步环境中发送任务前调用此方法，确保配置已加载
        
        使用示例：
            from jettask.webui.task_center import TaskCenter
            
            task_center = TaskCenter("http://localhost:8001/api/namespaces/demo")
            app = Jettask()
            app.mount_task_center(task_center)
            await app.init_from_task_center()  # 会自动连接task_center
            await task.apply_async(...)
        """
        if self.task_center and self.task_center.is_enabled and not self._task_center_config:
            return await self._load_config_from_task_center_async()
        return True
    
    def _setup_cleanup_handlers(self):
        """设置清理处理器"""
        # 避免重复注册
        if self._handlers_registered:
            return
        
        self._handlers_registered = True
        
        def signal_cleanup_handler(signum=None, frame=None):
            """信号处理器"""
            if self._cleanup_done:
                return
            # 只有启动过worker才需要打印清理信息
            if self._worker_started:
                logger.info("Received shutdown signal, cleaning up...")
            self.cleanup()
            if signum:
                # 设置标记表示需要退出
                self._should_exit = True
                # 对于多进程环境，不直接操作事件循环
                # 让执行器自己检测退出标志并优雅关闭
        
        def atexit_cleanup_handler():
            """atexit处理器"""
            if self._cleanup_done:
                return
            # atexit时不重复打印日志，静默清理
            self.cleanup()
        
        # 注册信号处理器
        if hasattr(signal, 'SIGTERM'):
            signal.signal(signal.SIGTERM, signal_cleanup_handler)
        if hasattr(signal, 'SIGINT'):
            signal.signal(signal.SIGINT, signal_cleanup_handler)
        
        # 注册atexit处理器
        import atexit
        atexit.register(atexit_cleanup_handler)
    
    def cleanup(self):
        """清理应用资源"""
        if self._cleanup_done:
            return
        
        self._cleanup_done = True
        
        # 只有真正启动过worker才打印日志
        if self._worker_started:
            logger.info("Cleaning up Jettask resources...")
            
            # 清理EventPool
            if hasattr(self, 'ep') and self.ep:
                self.ep.cleanup()
            
            logger.info("Jettask cleanup completed")
        else:
            # 如果只是实例化但没有启动，静默清理
            if hasattr(self, 'ep') and self.ep:
                self.ep.cleanup()
            logger.debug("Jettask instance cleanup (no worker started)")
    
    @property
    def consumer_manager(self):
        """获取消费者管理器"""
        return self.ep.consumer_manager if hasattr(self.ep, 'consumer_manager') else None

    @property
    def async_redis(self):
        """优化：复用连接池"""
        name = "_async_redis"
        if hasattr(self, name):
            return getattr(self, name)
        
        # 如果配置了任务中心且还未加载配置，先加载配置
        if self.task_center and self.task_center.is_enabled and not self._task_center_config:
            self._load_config_from_task_center()
        
        pool = get_async_redis_pool(self.redis_url, self.max_connections)
        async_redis = aioredis.StrictRedis(connection_pool=pool)
        setattr(self, name, async_redis)
        return async_redis

    @property
    def redis(self):
        """优化：复用连接池"""
        name = "_redis"
        if hasattr(self, name):
            return getattr(self, name)
        
        # 如果配置了任务中心且还未加载配置，先加载配置
        if self.task_center and self.task_center.is_enabled and not self._task_center_config:
            self._load_config_from_task_center()
        
        pool = get_redis_pool(self.redis_url, self.max_connections)
        redis_cli = redis.StrictRedis(connection_pool=pool)
        setattr(self, name, redis_cli)
        return redis_cli

    @property
    def ep(self):
        name = "_ep"
        if hasattr(self, name):
            ep = getattr(self, name)
        else:
            # 传递redis_prefix到consumer_config
            consumer_config = self.consumer_config.copy() if self.consumer_config else {}
            consumer_config['redis_prefix'] = self.redis_prefix
            
            ep = EventPool(
                self.redis, 
                self.async_redis, 
                redis_url=self.redis_url,
                consumer_strategy=self.consumer_strategy,
                consumer_config=consumer_config,
                redis_prefix=self.redis_prefix,
                app=self
            )
            setattr(self, name, ep)
        return ep

    def clear(self):
        if hasattr(self, "process"):
            delattr(self, "process")
        if hasattr(self, "_ep"):
            delattr(self, "_ep")

    def get_task_by_name(self, name: str) -> Task:
        # 1. 直接查找完整名称
        task = self._tasks.get(name)
        if task:
            return task
        
        # 2. 如果是简单名称（不含.），尝试匹配所有以该名称结尾的任务
        if '.' not in name:
            for task_key, task_obj in self._tasks.items():
                # 匹配 "module.function_name" 形式，提取函数名部分
                if '.' in task_key:
                    _, func_name = task_key.rsplit('.', 1)
                    if func_name == name:
                        return task_obj
                elif task_key == name:
                    # 完全匹配（可能没有模块前缀）
                    return task_obj
        
        return None

    def include_module(self, modules: list):
        self.include += modules

    def _task_from_fun(
        self, fun, name=None, base=None, queue=None, bind=False, retry_config=None, **options
    ) -> Task:
        name = name or gen_task_name(fun.__name__, fun.__module__)
        base = base or Task
        
        # 不再限制队列模式，因为每个task都有独立的consumer group
        
        if name not in self._tasks:
            run = staticmethod(fun)
            task: Task = type(
                fun.__name__,
                (base,),
                dict(
                    {
                        "app": self,
                        "name": name,
                        "run": run,
                        "queue": queue,
                        "retry_config": retry_config,  # 存储重试配置
                        "_decorated": True,
                        "__doc__": fun.__doc__,
                        "__module__": fun.__module__,
                        "__annotations__": fun.__annotations__,
                        "__wrapped__": run,
                    },
                    **options,
                ),
            )()
            task.bind_app(self)
            with contextlib.suppress(AttributeError):
                task.__qualname__ = fun.__qualname__
            self._tasks[task.name] = task
            
            # 记录队列和任务的映射（用于查找）
            if queue:
                if queue not in self._queue_tasks:
                    self._queue_tasks[queue] = []
                self._queue_tasks[queue].append(name)
        else:
            task = self._tasks[name]
        return task
    
    def task(
        self,
        name: str = None,
        queue: str = None,
        base: Task = None,
        # 重试相关参数
        max_retries: int = 0,
        retry_backoff: bool = True,  # 是否使用指数退避
        retry_backoff_max: float = 60,  # 最大退避时间（秒）
        retry_on_exceptions: tuple = None,  # 可重试的异常类型
        *args,
        **kwargs,
    ):
        def _create_task_cls(fun):
            # 将重试配置传递给_task_from_fun
            retry_config = None
            if max_retries > 0:
                retry_config = {
                    'max_retries': max_retries,
                    'retry_backoff': retry_backoff,
                    'retry_backoff_max': retry_backoff_max,
                }
                # 将异常类转换为类名字符串，以便序列化
                if retry_on_exceptions:
                    retry_config['retry_on_exceptions'] = [
                        exc if isinstance(exc, str) else exc.__name__ 
                        for exc in retry_on_exceptions
                    ]
            return self._task_from_fun(fun, name, base, queue, retry_config=retry_config, *args, **kwargs)

        return _create_task_cls
    
    async def send_tasks(self, messages: list):
        """
        统一的任务发送接口 - 只有这一个发送方法
        
        Args:
            messages: TaskMessage对象列表（或字典列表）
            
        Returns:
            List[str]: 任务ID列表
            
        使用示例:
            from jettask.core.message import TaskMessage
            
            # 发送单个任务（也是用列表）
            msg = TaskMessage(
                queue="order_processing",
                args=(12345,),
                kwargs={"customer_id": "C001", "amount": 99.99}
            )
            task_ids = await app.send_tasks([msg])
            
            # 批量发送
            messages = [
                TaskMessage(queue="email", kwargs={"to": "user1@example.com"}),
                TaskMessage(queue="email", kwargs={"to": "user2@example.com"}),
                TaskMessage(queue="sms", kwargs={"phone": "123456789"}),
            ]
            task_ids = await app.send_tasks(messages)
            
            # 跨项目发送（不需要task定义）
            messages = [
                TaskMessage(queue="remote_queue", kwargs={"data": "value"})
            ]
            task_ids = await app.send_tasks(messages)
        """
        if not messages:
            return []
        
        # 导入TaskMessage
        from .message import TaskMessage
        
        results = []
        
        # 按队列分组消息，以便批量处理
        queue_messages = {}
        for msg in messages:
            # 支持TaskMessage对象或字典
            if isinstance(msg, dict):
                msg = TaskMessage.from_dict(msg)
            elif not isinstance(msg, TaskMessage):
                raise ValueError(f"Invalid message type: {type(msg)}. Expected TaskMessage or dict")
            
            # 验证消息
            msg.validate()
            
            # 确定实际的队列名（考虑优先级）
            actual_queue = msg.queue
            if msg.priority is not None:
                # 将优先级拼接到队列名后面
                actual_queue = f"{msg.queue}:{msg.priority}"
                # 更新消息体中的queue字段，确保与实际发送的stream key一致
                msg.queue = actual_queue
            
            # 按队列分组
            if actual_queue not in queue_messages:
                queue_messages[actual_queue] = []
            queue_messages[actual_queue].append(msg)
        
        # 处理每个队列的消息
        for queue, queue_msgs in queue_messages.items():
            # 统一使用批量发送，无论是否广播模式
            # 广播/单播由消费端的consumer group name决定
            batch_results = await self._send_batch_messages(queue, queue_msgs)
            results.extend(batch_results)
        
        return results
    
    async def _send_batch_messages(self, queue: str, messages: list) -> list:
        """批量发送single模式消息（内部方法）"""
        from ..utils.serializer import dumps_str
        
        # 分离普通任务和延迟任务
        normal_messages = []
        delayed_messages = []
        
        for msg in messages:
            msg_dict = msg.to_dict()
            
            # 处理延迟任务
            if msg.delay and msg.delay > 0:
                # 添加延迟执行标记
                current_time = time.time()
                msg_dict['execute_at'] = current_time + msg.delay
                msg_dict['is_delayed'] = 1
                delayed_messages.append((msg_dict, msg.delay))
            else:
                normal_messages.append(msg_dict)
        
        results = []
        
        # 发送普通任务（统一使用批量发送）
        if normal_messages:
            batch_results = await self.ep._batch_send_event(
                self.ep.get_prefixed_queue_name(queue),
                [{'data': dumps_str(msg)} for msg in normal_messages],
                self.ep.get_redis_client(asyncio=True, binary=True).pipeline()
            )
            results.extend(batch_results)
        
        # 发送延迟任务（需要同时添加到DELAYED_QUEUE）
        if delayed_messages:
            delayed_results = await self._send_delayed_tasks(queue, delayed_messages)
            results.extend(delayed_results)
        
        return results
    
    async def _send_delayed_tasks(self, queue: str, delayed_messages: list) -> list:
        """发送延迟任务到Stream并添加到延迟队列"""
        from ..utils.serializer import dumps_str
        
        # 使用Lua脚本原子性地处理延迟任务
        lua_script = """
        local prefix = ARGV[1]
        local results = {}
        
        -- 从ARGV[2]开始，每4个参数为一组任务信息
        -- [stream_key, stream_data, execute_at, queue]
        for i = 2, #ARGV, 4 do
            local stream_key = ARGV[i]
            local stream_data = ARGV[i+1]
            local execute_at = tonumber(ARGV[i+2])
            local queue_name = ARGV[i+3]
            
            -- 使用Hash存储所有队列的offset
            local offsets_hash = prefix .. ':QUEUE_OFFSETS'
            
            -- 从stream_key中提取队列名
            local queue_name = string.gsub(stream_key, '^' .. prefix .. ':QUEUE:', '')
            
            -- 使用HINCRBY原子递增offset
            local current_offset = redis.call('HINCRBY', offsets_hash, queue_name, 1)
            
            -- 1. 添加消息到Stream（包含offset字段）
            local stream_id = redis.call('XADD', stream_key, '*', 
                'data', stream_data,
                'offset', current_offset)
            
            -- 2. 添加到延迟队列ZSET
            local delayed_queue_key = prefix .. ':DELAYED_QUEUE:' .. queue_name
            redis.call('ZADD', delayed_queue_key, execute_at, stream_id)
            
            -- 3. 设置任务状态Hash
            local task_key = prefix .. ':TASK:' .. stream_id
            redis.call('HSET', task_key, 'status', 'delayed')
            redis.call('EXPIRE', task_key, 3600)
            
            -- 保存stream_id到结果
            table.insert(results, stream_id)
        end
        
        return results
        """
        
        # 准备Lua脚本参数
        lua_args = [self.redis_prefix]
        prefixed_queue = self.ep.get_prefixed_queue_name(queue)
        
        for msg_dict, delay_seconds in delayed_messages:
            stream_data = dumps_str(msg_dict)
            execute_at = msg_dict['execute_at']
            
            lua_args.extend([
                prefixed_queue,
                stream_data,
                str(execute_at),
                queue
            ])
        
        # 执行Lua脚本
        client = self.ep.get_redis_client(asyncio=True, binary=True)
        
        # 注册Lua脚本
        if not hasattr(self, '_delayed_task_script'):
            self._delayed_task_script = client.register_script(lua_script)
        
        # 执行脚本
        results = await self._delayed_task_script(keys=[], args=lua_args)
        
        # 解码结果
        return [r.decode('utf-8') if isinstance(r, bytes) else r for r in results]
    
    def register_router(self, router, prefix: str = None):
        """
        注册任务路由器
        
        Args:
            router: TaskRouter实例
            prefix: 额外的前缀（可选）
        
        使用示例：
            from jettask import Jettask, TaskRouter
            
            # 创建路由器
            email_router = TaskRouter(prefix="email", queue="emails")
            
            @email_router.task()
            async def send_email(to: str):
                pass
            
            # 注册到主应用
            app = Jettask(redis_url="redis://localhost:6379/0")
            app.register_router(email_router)
        """
        from ..router import TaskRouter
        
        if not isinstance(router, TaskRouter):
            raise TypeError("router must be a TaskRouter instance")
        
        # 注册所有任务
        for task_name, task_config in router.get_tasks().items():
            # 如果指定了额外前缀，添加到任务名
            if prefix:
                if task_config.get('name'):
                    task_config['name'] = f"{prefix}.{task_config['name']}"
                task_name = f"{prefix}.{task_name}"
            
            # 获取任务函数
            func = task_config.pop('func')
            name = task_config.pop('name', task_name)
            queue = task_config.pop('queue', None)
            
            # 注册任务
            task = self._task_from_fun(func, name, None, queue, **task_config)
            logger.info(f"Registered task: {name} (queue: {queue or self.redis_prefix})")
        
        return self

    def _mount_module(self):
        for module in self.include:
            module = importlib.import_module(module)
            for attr_name in dir(module):
                obj = getattr(module, attr_name)
                if hasattr(obj, "app"):
                    self._tasks.update(getattr(obj, "app")._tasks)

    def _validate_tasks_for_executor(self, execute_type: str, queues: List[str]):
        """验证任务类型是否与执行器兼容"""
        if execute_type in ["asyncio", "multi_asyncio"]:
            return  # AsyncIO和MultiAsyncio可以处理异步任务
        
        # 只有Thread执行器不能处理异步任务
        incompatible_tasks = []
        for task_name, task in self._tasks.items():
            # 检查任务是否属于指定队列
            if task.queue not in queues:
                continue
                
            # 检查是否是异步任务
            if asyncio.iscoroutinefunction(task.run):
                incompatible_tasks.append({
                    'name': task_name,
                    'queue': task.queue,
                    'type': 'async'
                })
        
        if incompatible_tasks:
            error_msg = f"\n错误：{execute_type} 执行器不能处理异步任务！\n"
            error_msg += "发现以下异步任务：\n"
            for task in incompatible_tasks:
                error_msg += f"  - {task['name']} (队列: {task['queue']})\n"
            error_msg += f"\n解决方案：\n"
            error_msg += f"1. 使用 asyncio 或 process 执行器\n"
            error_msg += f"2. 或者将这些任务改为同步函数（去掉 async/await）\n"
            error_msg += f"3. 或者将这些任务的队列从监听列表中移除\n"
            raise ValueError(error_msg)
    
    def _start(
        self,
        execute_type: str = "asyncio",
        queues: List[str] = None,
        concurrency: int = 1,
        prefetch_multiplier: int = 1,
        **kwargs
    ):
        # 设置默认队列
        if not queues:
            queues = [self.redis_prefix]
        
        self.ep.queues = queues
        self.ep.init_routing()
        self._mount_module()
        # 验证任务兼容性 
        self._validate_tasks_for_executor(execute_type, queues)
        
        # 收集每个队列上的所有任务（用于广播支持）
        self._tasks_by_queue = {}
        for task_name, task in self._tasks.items():
            task_queue = task.queue or self.redis_prefix
            if task_queue in queues:
                if task_queue not in self._tasks_by_queue:
                    self._tasks_by_queue[task_queue] = []
                self._tasks_by_queue[task_queue].append(task_name)
                logger.debug(f"Task {task_name} listening on queue {task_queue}")
        
        event_queue = deque()
        
        # 创建消费者组
        try:
            self.ep.create_group()
        except Exception as e:
            logger.warning(f"创建消费者组时出错: {e}")
            # 继续执行，listening_event会自动处理
        
        # 根据执行器类型创建对应的执行器
        if execute_type == "asyncio":
            # 对于asyncio执行器，使用asyncio.Queue
            async_event_queue = asyncio.Queue()
            
            async def run_asyncio_executor():
                # 启动异步事件监听
                asyncio.create_task(self.ep.listening_event(async_event_queue, prefetch_multiplier))
                # 创建并运行执行器
                executor = AsyncioExecutor(async_event_queue, self, concurrency)
                await executor.loop()
            
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # 如果事件循环已经在运行，创建一个新的
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
            except RuntimeError:
                # 如果当前线程没有事件循环，创建一个新的
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            try:
                loop.run_until_complete(run_asyncio_executor())
            except RuntimeError as e:
                if "Event loop stopped" in str(e):
                    logger.info("Event loop stopped, shutting down gracefully")
                else:
                    raise
        elif execute_type == "multi_asyncio":
            # multi_asyncio在每个子进程中会启动自己的监听器
            executor = MultiAsyncioExecutor(event_queue, self, concurrency)
            executor.prefetch_multiplier = prefetch_multiplier
            
            # 设置信号处理器以正确响应Ctrl+C
            def multi_asyncio_signal_handler(signum, _frame):
                logger.info(f"Multi-asyncio mode received signal {signum}")
                executor._main_received_signal = True
                executor.shutdown_event.set()
                # 强制退出主循环
                raise KeyboardInterrupt()
            
            signal.signal(signal.SIGINT, multi_asyncio_signal_handler)
            signal.signal(signal.SIGTERM, multi_asyncio_signal_handler)
            
            try:
                executor.loop()
            except KeyboardInterrupt:
                logger.info("Multi-asyncio mode interrupted")
            finally:
                executor.shutdown()
        else:
            raise ValueError(f"不支持的执行器类型：{execute_type}，仅支持 'asyncio' 和 'multi_asyncio'")

    def _run_subprocess(self, *args, **kwargs):
        # logger.info("Started Worker Process")
        process = multiprocessing.Process(target=self._start, args=args, kwargs=kwargs)
        process.start()
        return process

    def start(
        self,
        execute_type: str = "asyncio",
        queues: List[str] = None,
        concurrency: int = 1,
        prefetch_multiplier: int = 1,
        reload: bool = False,
    ):
        # 标记worker已启动
        self._worker_started = True
        
        # 如果配置了任务中心，从任务中心获取配置
        if self.task_center and self.task_center.is_enabled:
            self._load_config_from_task_center()
        
        # 注册清理处理器（只在启动worker时注册）
        self._setup_cleanup_handlers()
        
        if execute_type == "multi_asyncio" and self.consumer_strategy == "pod":
            raise ValueError("multi_asyncio模式下无法使用pod策略")
        self.process = self._run_subprocess(
            execute_type=execute_type,
            queues=queues,
            concurrency=concurrency,
            prefetch_multiplier=prefetch_multiplier,
        )
        if reload:
            event_handler = FileChangeHandler(
                self,
                execute_type=execute_type,
                queues=queues,
                concurrency=concurrency,
                prefetch_multiplier=prefetch_multiplier,
            )
            observer = Observer()
            observer.schedule(event_handler, ".", recursive=True)
            observer.start()
        # 使用事件来等待，而不是无限循环
        try:
            while not self._should_exit:
                time.sleep(0.1)  # 短暂睡眠，快速响应退出信号
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
            self.cleanup()
            if self.process and self.process.is_alive():
                self.process.terminate()
                self.process.join(timeout=2)
                if self.process.is_alive():
                    logger.warning("Process did not terminate, killing...")
                    self.process.kill()


    def get_task_info(self, event_id: str, asyncio: bool = False):
        """获取任务信息（从TASK:hash）"""
        client = self.get_redis_client(asyncio)
        key = f"{self.redis_prefix}:TASK:{event_id}"
        if asyncio:
            return client.hgetall(key)
        else:
            return client.hgetall(key)
    
    def get_task_status(self, event_id: str, asyncio: bool = False):
        """获取任务状态（从TASK:hash的status字段）"""
        if asyncio:
            return self._get_task_status_async(event_id)
        else:
            client = self.redis
            key = f"{self.redis_prefix}:TASK:{event_id}"
            return client.hget(key, "status")

    async def _get_task_status_async(self, event_id: str):
        """异步获取任务状态"""
        key = f"{self.redis_prefix}:TASK:{event_id}"
        return await self.async_redis.hget(key, "status")

    def set_task_status(self, event_id: str, status: str, asyncio: bool = False):
        """设置任务状态（写入TASK:hash的status字段）"""
        if asyncio:
            return self._set_task_status_async(event_id, status)
        else:
            client = self.redis
            key = f"{self.redis_prefix}:TASK:{event_id}"
            return client.hset(key, "status", status)
    
    async def _set_task_status_async(self, event_id: str, status: str):
        """异步设置任务状态"""
        key = f"{self.redis_prefix}:TASK:{event_id}"
        return await self.async_redis.hset(key, "status", status)

    def set_task_status_by_batch(self, mapping: dict, asyncio: bool = False):
        """批量设置任务状态（写入TASK:hash）"""
        if asyncio:
            return self._set_task_status_by_batch_async(mapping)
        else:
            pipeline = self.redis.pipeline()
            for event_id, status in mapping.items():
                key = f"{self.redis_prefix}:TASK:{event_id}"
                pipeline.hset(key, "status", status)
            return pipeline.execute()
    
    async def _set_task_status_by_batch_async(self, mapping: dict):
        """异步批量设置任务状态"""
        pipeline = self.async_redis.pipeline()
        for event_id, status in mapping.items():
            key = f"{self.redis_prefix}:TASK:{event_id}"
            pipeline.hset(key, "status", status)
        return await pipeline.execute()

    def del_task_status(self, event_id: str, asyncio: bool = False):
        """删除任务状态（删除整个TASK:hash）"""
        client = self.get_redis_client(asyncio)
        key = f"{self.redis_prefix}:TASK:{event_id}"
        return client.delete(key)

    def get_redis_client(self, asyncio: bool = False):
        return self.async_redis if asyncio else self.redis

    def set_data(
        self, event_id: str, result: str, ex: int = 3600, asyncio: bool = False
    ):
        """设置任务结果（写入TASK:hash的result字段）"""
        client = self.get_redis_client(asyncio)
        key = f"{self.redis_prefix}:TASK:{event_id}"
        if asyncio:
            return self._set_data_async(key, result, ex)
        else:
            client.hset(key, "result", result)
            return client.expire(key, ex)
    
    async def _set_data_async(self, key: str, result: str, ex: int):
        """异步设置任务结果"""
        await self.async_redis.hset(key, "result", result)
        return await self.async_redis.expire(key, ex)
    
    async def get_and_delayed_deletion(self, key: str, ex: int):
        """获取结果并延迟删除（从hash中）"""
        result = await self.async_redis.hget(key, "result")
        await self.async_redis.expire(key, ex)
        return result
    
    async def _get_result_async(self, key: str, delete: bool, delayed_deletion_ex: int):
        """异步获取任务结果"""
        client = self.async_redis
        if delayed_deletion_ex is not None:
            result = await client.hget(key, "result")
            await client.expire(key, delayed_deletion_ex)
            return result
        elif delete:
            # 获取结果并删除整个hash
            result = await client.hget(key, "result")
            await client.delete(key)
            return result
        else:
            return await client.hget(key, "result")
    
    def get_result(self, event_id: str, delete: bool = False, asyncio: bool = False, 
                   delayed_deletion_ex: int = None, wait: bool = False, timeout: int = 300,
                   poll_interval: float = 0.5):
        """获取任务结果（从TASK:hash的result字段）
        
        Args:
            event_id: 任务ID
            delete: 是否删除结果
            asyncio: 是否使用异步模式
            delayed_deletion_ex: 延迟删除时间（秒）
            wait: 是否阻塞等待直到任务完成
            timeout: 等待超时时间（秒），默认300秒
            poll_interval: 轮询间隔（秒），默认0.5秒
            suppress_traceback: 是否抑制框架层堆栈（直接打印错误并退出）
        
        Returns:
            任务结果字符串
            
        Raises:
            TaskTimeoutError: 等待超时
            TaskExecutionError: 任务执行失败
            TaskNotFoundError: 任务不存在
        """
        if asyncio:
            key = f"{self.redis_prefix}:TASK:{event_id}"
            if wait:
                return self._get_result_async_wait(event_id, key, delete, delayed_deletion_ex, timeout, poll_interval)
            else:
                return self._get_result_async(key, delete, delayed_deletion_ex)
        else:
            # 同步模式
            if wait:
                return self._get_result_sync_wait(event_id, delete, delayed_deletion_ex, timeout, poll_interval)
            else:
                client = self.redis
                key = f"{self.redis_prefix}:TASK:{event_id}"
                if delayed_deletion_ex is not None:
                    result = client.hget(key, "result")
                    client.expire(key, delayed_deletion_ex)
                    return result
                elif delete:
                    # 如果配置了任务中心，不删除消息，等任务中心同步后删除
                    if self.task_center and self.task_center.is_enabled:
                        result = client.hget(key, "result")
                        # 仅标记为待删除，不实际删除
                        client.hset(key, "__pending_delete", "1")
                        return result
                    else:
                        # 获取结果并删除整个hash
                        result = client.hget(key, "result")
                        client.delete(key)
                        return result
                else:
                    # 先尝试从Redis获取
                    result = client.hget(key, "result")
                    # 如果Redis中没有且配置了任务中心，从任务中心获取
                    if result is None and self.task_center_client.is_enabled:
                        import asyncio
                        loop = asyncio.new_event_loop()
                        try:
                            task_data = loop.run_until_complete(
                                self.task_center_client.get_task_result(event_id)
                            )
                            if task_data:
                                result = task_data.get('result')
                        finally:
                            loop.close()
                    return result
    
    def _get_result_sync_wait(self, event_id: str, delete: bool, delayed_deletion_ex: int, 
                              timeout: int, poll_interval: float):
        """同步模式下阻塞等待任务结果"""
        start_time = time.time()
        
        while True:
            # 检查超时
            if time.time() - start_time > timeout:
                raise TaskTimeoutError(f"Task {event_id} timed out after {timeout} seconds")
            
            # 获取任务状态
            status = self.get_task_status(event_id)
            
            if status is None:
                raise TaskNotFoundError(f"Task {event_id} not found")
            
            if status == 'success':
                # 任务成功，获取结果
                key = f"{self.redis_prefix}:TASK:{event_id}"
                if delayed_deletion_ex is not None:
                    result = self.redis.hget(key, "result")
                    self.redis.expire(key, delayed_deletion_ex)
                    return result
                elif delete:
                    result = self.redis.hget(key, "result")
                    self.redis.delete(key)
                    return result
                else:
                    return self.redis.hget(key, "result")
            
            elif status == 'error':
                # 任务失败，获取错误信息并抛出异常
                key = f"{self.redis_prefix}:TASK:{event_id}"
                # 从 exception 字段获取错误信息
                error_msg = self.redis.hget(key, "exception") or "Task execution failed"
                # 抛出自定义异常
                raise TaskExecutionError(event_id, error_msg)
            
            # 任务还在执行中，继续等待
            time.sleep(poll_interval)
    
    async def _get_result_async_wait(self, event_id: str, key: str, delete: bool, 
                                     delayed_deletion_ex: int, timeout: int, poll_interval: float):
        """异步模式下等待任务结果"""
        start_time = time.time()
        
        while True:
            # 检查超时
            if time.time() - start_time > timeout:
                raise TaskTimeoutError(f"Task {event_id} timed out after {timeout} seconds")
            
            # 获取任务状态
            status = await self._get_task_status_async(event_id)
            
            if status is None:
                raise TaskNotFoundError(f"Task {event_id} not found")
            
            if status == 'success':
                # 任务成功，获取结果
                if delayed_deletion_ex is not None:
                    result = await self.async_redis.hget(key, "result")
                    await self.async_redis.expire(key, delayed_deletion_ex)
                    return result
                elif delete:
                    result = await self.async_redis.hget(key, "result")
                    await self.async_redis.delete(key)
                    return result
                else:
                    return await self.async_redis.hget(key, "result")
            
            elif status == 'error':
                # 任务失败，获取错误信息并抛出异常
                # 从 exception 字段获取错误信息
                error_msg = await self.async_redis.hget(key, "exception") or "Task execution failed"
                # 抛出自定义异常
                raise TaskExecutionError(event_id, error_msg)
            
            # 任务还在执行中，继续等待
            await asyncio.sleep(poll_interval)
    
    # ==================== 定时任务调度相关 ====================
    
    async def _ensure_scheduler_initialized(self, db_url: str = None):
        """确保调度器已初始化（内部方法）"""
        if not self.scheduler_manager:
            logger.info("Auto-initializing scheduler...")
            # 优先使用传入的db_url，然后是实例化时的pg_url，最后是环境变量
            if not db_url:
                db_url = self.pg_url or os.environ.get('JETTASK_PG_URL')
            if not db_url:
                raise ValueError(
                    "Database URL not provided. Please provide pg_url when initializing Jettask, "
                    "or set JETTASK_PG_URL environment variable\n"
                    "Example: app = Jettask(redis_url='...', pg_url='postgresql://...')\n"
                    "Or: export JETTASK_PG_URL='postgresql://user:password@localhost:5432/jettask'"
                )
            
            from ..scheduler import TaskScheduler, ScheduledTaskManager
            
            # 创建数据库管理器
            self.scheduler_manager = ScheduledTaskManager(db_url)
            await self.scheduler_manager.connect()
            await self.scheduler_manager.init_schema()
            
            # 创建调度器
            scheduler_config = self.scheduler_config.copy()
            scheduler_config.setdefault('scan_interval', 0.1)
            scheduler_config.setdefault('batch_size', 100)
            scheduler_config.setdefault('leader_ttl', 10)
            
            self.scheduler = TaskScheduler(
                app=self,
                db_manager=self.scheduler_manager,
                **scheduler_config
            )
            
            await self.scheduler.connect()
            logger.info("Scheduler initialized")
    
    async def start_scheduler(self):
        """启动定时任务调度器（自动初始化）"""
        # 自动初始化调度器
        await self._ensure_scheduler_initialized()
        
        try:
            await self.scheduler.run()
        except Exception as e:
            logger.error(f"Scheduler error: {e}", exc_info=True)
            raise
    
    def stop_scheduler(self):
        """停止定时任务调度器"""
        if self.scheduler:
            self.scheduler.stop()
            logger.info("Scheduler stopped")
    
    async def add_scheduled_task(
        self,
        task_name: str,
        scheduler_id: str,  # 必填参数
        queue_name: str = None,
        task_type: str = "interval",
        interval_seconds: float = None,
        cron_expression: str = None,
        task_args: list = None,
        task_kwargs: dict = None,
        next_run_time: datetime = None,
        skip_if_exists: bool = True,
        at_once: bool = True,  # 是否立即保存到数据库
        **extra_params
    ):
        """
        添加定时任务
        
        Args:
            task_name: 要执行的函数名（必须对应已经通过@app.task注册的任务）
            scheduler_id: 任务的唯一标识符（必填，用于去重）
            queue_name: 目标队列名（可选，从task_name对应的任务自动获取）
            task_type: 任务类型 ('once', 'interval', 'cron')
            interval_seconds: 间隔秒数 (task_type='interval'时使用)
            cron_expression: Cron表达式 (task_type='cron'时使用)
            task_args: 任务参数列表
            task_kwargs: 任务关键字参数
            next_run_time: 首次执行时间 (task_type='once'时使用)
            skip_if_exists: 如果任务已存在是否跳过（默认True）
            at_once: 是否立即保存到数据库（默认True），如果False则返回任务对象用于批量写入
            **extra_params: 其他参数 (如 max_retries, timeout, description 等)
        """
        # 自动初始化
        await self._ensure_scheduler_initialized()
        
        from ..scheduler.models import ScheduledTask, TaskType
        
        # 尝试从已注册的任务中获取信息
        registered_task = None
        
        # 1. 直接匹配
        registered_task = self._tasks.get(task_name)
        
        # 2. 如果没找到，尝试查找以task_name结尾的任务（如 "module.task_name"）
        if not registered_task:
            for task_key, task_obj in self._tasks.items():
                if task_key.endswith(f".{task_name}") or task_key == task_name:
                    registered_task = task_obj
                    break
        
        if not registered_task:
            # 任务必须已注册
            available_tasks = list(self._tasks.keys())
            error_msg = f"Task '{task_name}' not found in registered tasks.\n"
            error_msg += "All scheduled tasks must be registered with @app.task decorator.\n"
            if available_tasks:
                error_msg += f"Available tasks: {', '.join(available_tasks)}"
            raise ValueError(error_msg)
        
        # 自动填充信息
        if not queue_name:
            queue_name = registered_task.queue or self.redis_prefix
        
        # 使用注册时的完整任务名称（包含模块前缀）
        # 查找任务的完整注册名称
        full_task_name = None
        for task_key, task_obj in self._tasks.items():
            if task_obj == registered_task:
                full_task_name = task_key
                break
        
        if not full_task_name:
            # 如果没找到，使用用户提供的名称
            full_task_name = task_name
        
        # 处理 next_run_time（主要用于 once 类型）
        if task_type == "once" and extra_params.get("next_run_time"):
            # 如果在 extra_params 中，移到正确位置
            next_run_time = extra_params.pop("next_run_time", None)
        
        # 移除不属于ScheduledTask的参数
        extra_params.pop("skip_if_exists", None)
        
        # scheduler_id是必填参数，必须由用户提供
        if not scheduler_id:
            raise ValueError("scheduler_id is required and must be provided")
        
        # 获取当前命名空间
        namespace = 'default'
        if self.task_center and hasattr(self.task_center, 'namespace_name'):
            namespace = self.task_center.namespace_name
        elif self.redis_prefix and self.redis_prefix != 'jettask':
            # 如果没有task_center，使用redis_prefix作为命名空间
            namespace = self.redis_prefix
        
        # 创建任务对象
        task = ScheduledTask(
            scheduler_id=scheduler_id,
            task_name=full_task_name,  # 使用完整的任务名称（包含模块前缀）
            task_type=TaskType(task_type),
            queue_name=queue_name,
            namespace=namespace,  # 设置命名空间
            task_args=task_args or [],
            task_kwargs=task_kwargs or {},
            interval_seconds=interval_seconds,
            cron_expression=cron_expression,
            next_run_time=next_run_time,
            **extra_params
        )
        
        # 如果不立即保存，返回任务对象供批量写入
        if not at_once:
            # 设置skip_if_exists标记供批量写入时使用
            task._skip_if_exists = skip_if_exists
            return task
        
        # 保存到数据库（支持去重）
        task, created = await self.scheduler_manager.create_or_get_task(task, skip_if_exists=skip_if_exists)
        
        if created:
            logger.info(f"Scheduled task {task.id} created for function {task_name}")
        else:
            logger.info(f"Scheduled task {task.id} already exists for function {task_name}")
        
        return task
    
    async def remove_scheduled_task(self, scheduler_id: str):
        """移除定时任务"""
        # 自动初始化
        await self._ensure_scheduler_initialized()
        
        # 先获取任务
        task = await self.scheduler_manager.get_task_by_scheduler_id(scheduler_id)
        if not task:
            return False
        
        success = await self.scheduler_manager.delete_task(task.id)
        
        if success and self.scheduler:
            # 从Redis中也移除
            await self.scheduler.loader.remove_task(task.id)
        
        return success
    
    async def batch_add_scheduled_tasks(
        self,
        tasks: list,
        skip_existing: bool = True
    ):
        """
        批量添加定时任务
        
        Args:
            tasks: 任务配置列表，每个元素是一个字典，包含add_scheduled_task的参数
            skip_existing: 是否跳过已存在的任务
            
        Returns:
            成功创建的任务列表
        """
        # 自动初始化
        await self._ensure_scheduler_initialized()
        
        from ..scheduler.models import ScheduledTask, TaskType
        
        task_objects = []
        for task_config in tasks:
            # 获取任务名称
            task_name = task_config.get('task_name')
            if not task_name:
                logger.warning("Task config missing task_name, skipping")
                continue
            
            # 查找注册的任务
            registered_task = self._tasks.get(task_name)
            if not registered_task:
                for task_key, task_obj in self._tasks.items():
                    if task_key.endswith(f".{task_name}") or task_key == task_name:
                        registered_task = task_obj
                        task_name = task_key  # 使用完整名称
                        break
            
            if not registered_task:
                logger.warning(f"Task '{task_name}' not found in registered tasks, skipping")
                continue
            
            # 准备任务参数
            queue_name = task_config.get('queue_name') or registered_task.queue or self.redis_prefix
            task_type = task_config.get('task_type', 'interval')
            
            # 处理next_run_time
            next_run_time = task_config.get('next_run_time')
            if task_type == 'once' and not next_run_time:
                next_run_time = datetime.now()
            
            # scheduler_id是必填参数
            scheduler_id = task_config.get('scheduler_id')
            if not scheduler_id:
                raise ValueError(f"Task config for '{task_name}' missing required scheduler_id")
            
            # 获取当前命名空间
            namespace = 'default'
            if self.task_center and hasattr(self.task_center, 'namespace_name'):
                namespace = self.task_center.namespace_name
            elif self.redis_prefix and self.redis_prefix != 'jettask':
                # 如果没有task_center，使用redis_prefix作为命名空间
                namespace = self.redis_prefix
            
            # 创建任务对象
            task_obj = ScheduledTask(
                scheduler_id=scheduler_id,
                task_name=task_name,
                task_type=TaskType(task_type),
                queue_name=queue_name,
                namespace=namespace,  # 设置命名空间
                task_args=task_config.get('task_args', []),
                task_kwargs=task_config.get('task_kwargs', {}),
                interval_seconds=task_config.get('interval_seconds'),
                cron_expression=task_config.get('cron_expression'),
                next_run_time=next_run_time,
                enabled=task_config.get('enabled', True),
                max_retries=task_config.get('max_retries', 3),
                retry_delay=task_config.get('retry_delay', 60),
                timeout=task_config.get('timeout', 300),
                description=task_config.get('description'),
                tags=task_config.get('tags', []),
                metadata=task_config.get('metadata', {})
            )
            task_objects.append(task_obj)
        
        # 批量创建
        created_tasks = await self.scheduler_manager.batch_create_tasks(task_objects, skip_existing)
        
        logger.info(f"Batch created {len(created_tasks)} scheduled tasks")
        return created_tasks
    
    async def bulk_write_scheduled_tasks(self, tasks: list):
        """
        批量写入定时任务（配合at_once=False使用）
        
        使用示例：
            # 收集任务对象
            tasks = []
            for i in range(100):
                task = await app.add_scheduled_task(
                    task_name="my_task",
                    scheduler_id=f"task_{i}",
                    task_type="interval",
                    interval_seconds=30,
                    at_once=False  # 不立即保存
                )
                tasks.append(task)
            
            # 批量写入
            created_tasks = await app.bulk_write_scheduled_tasks(tasks)
        
        Args:
            tasks: 通过add_scheduled_task(at_once=False)创建的任务对象列表
        
        Returns:
            成功创建的任务列表
        """
        # 自动初始化
        await self._ensure_scheduler_initialized()
        
        if not tasks:
            return []
        
        # 准备批量创建的任务列表
        task_objects = []
        for task in tasks:
            if not hasattr(task, 'scheduler_id'):
                logger.warning("Invalid task object, skipping")
                continue
            
            
            task_objects.append(task)
        
        # 批量创建（使用第一个任务的skip_if_exists设置）
        skip_existing = getattr(tasks[0], '_skip_if_exists', True) if tasks else True
        created_tasks = await self.scheduler_manager.batch_create_tasks(task_objects, skip_existing)
        
        logger.info(f"Bulk wrote {len(created_tasks)} scheduled tasks")
        return created_tasks
    
    async def list_scheduled_tasks(self, **filters):
        """列出定时任务"""
        # 自动初始化
        await self._ensure_scheduler_initialized()
        
        return await self.scheduler_manager.list_tasks(**filters)
    
    async def get_scheduled_task(self, scheduler_id: str):
        """获取定时任务详情"""
        # 自动初始化
        await self._ensure_scheduler_initialized()
        
        return await self.scheduler_manager.get_task_by_scheduler_id(scheduler_id)
    
    async def pause_scheduled_task(self, scheduler_id: str):
        """暂停/禁用定时任务"""
        # 自动初始化
        await self._ensure_scheduler_initialized()
        
        # 通过scheduler_id获取任务
        task = await self.scheduler_manager.get_task_by_scheduler_id(scheduler_id)
            
        if task:
            task.enabled = False
            await self.scheduler_manager.update_task(task)
            
            # 从Redis中移除
            if self.scheduler:
                await self.scheduler.loader.remove_task(task.id)
            
            logger.info(f"Task {task.id} (scheduler_id: {task.scheduler_id}) disabled")
            return True
        return False
    
    async def resume_scheduled_task(self, scheduler_id: str):
        """恢复/启用定时任务"""
        # 自动初始化
        await self._ensure_scheduler_initialized()
        
        # 通过scheduler_id获取任务
        task = await self.scheduler_manager.get_task_by_scheduler_id(scheduler_id)
            
        if task:
            task.enabled = True
            task.next_run_time = task.calculate_next_run_time()
            await self.scheduler_manager.update_task(task)
            
            # 触发重新加载
            if self.scheduler:
                await self.scheduler.loader.load_tasks()
            
            logger.info(f"Task {task.id} (scheduler_id: {task.scheduler_id}) enabled")
            return True
        return False
    
    # 别名，更直观
    async def disable_scheduled_task(self, scheduler_id: str):
        """禁用定时任务"""
        return await self.pause_scheduled_task(scheduler_id=scheduler_id)
    
    async def enable_scheduled_task(self, scheduler_id: str):
        """启用定时任务"""
        return await self.resume_scheduled_task(scheduler_id=scheduler_id)
    
