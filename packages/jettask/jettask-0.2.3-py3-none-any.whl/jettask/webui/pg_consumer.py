#!/usr/bin/env python
"""简化版的 PostgreSQL Consumer - 只保留必要功能"""

import asyncio
import json
import logging
import msgpack
import os
import time
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timezone
from collections import defaultdict

import redis.asyncio as redis
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from jettask.webui.config import PostgreSQLConfig, RedisConfig
from jettask.core.consumer_manager import ConsumerManager, ConsumerStrategy
from jettask.core.offline_worker_recovery import OfflineWorkerRecovery
from jettask.constants import is_internal_consumer, TASK_STATUS_PRIORITY

logger = logging.getLogger(__name__)

# 注释掉调试文件写入，避免权限问题
# logger_f = open(f'./pg_consumer.txt', 'a+')

# 使用 constants.py 中定义的任务状态优先级
# STATUS_PRIORITY 已从 constants.py 导入为 TASK_STATUS_PRIORITY
class PostgreSQLConsumer:
    """PostgreSQL消费者，从Redis队列消费任务并持久化到PostgreSQL
    
    支持多租户（命名空间）隔离
    """
    
    def __init__(self, pg_config: PostgreSQLConfig, redis_config: RedisConfig, prefix: str = "jettask", 
                 node_id: str = None, consumer_strategy: ConsumerStrategy = ConsumerStrategy.HEARTBEAT,
                 namespace_id: str = None, namespace_name: str = None,
                 enable_backlog_monitor: bool = True, backlog_monitor_interval: int = 1):
        self.pg_config = pg_config
        self.redis_config = redis_config
        self.prefix = prefix
        
        # 命名空间支持
        self.namespace_id = namespace_id
        self.namespace_name = namespace_name or "default"
        self.redis_client: Optional[Redis] = None
        self.async_engine = None
        self.AsyncSessionLocal = None
        self.consumer_group = f"{prefix}_pg_consumer"
        
        # 节点标识
        import socket
        hostname = socket.gethostname()
        self.node_id = node_id or f"{hostname}_{os.getpid()}"
        
        # 使用 ConsumerManager 来管理 consumer_id
        self.consumer_strategy = consumer_strategy
        self.consumer_manager = None  # 将在 start() 中初始化
        self.consumer_id = None  # 将从 ConsumerManager 获取
        
        self._running = False
        self._tasks = []
        self._known_queues = set()
        self._consecutive_errors = defaultdict(int)
        
        # 内存中维护已处理的任务ID集合（用于优化查询）
        self._processed_task_ids = set()
        self._processed_ids_lock = asyncio.Lock()  # 保护并发访问
        # 定期清理过期的ID（防止内存无限增长）
        self._processed_ids_max_size = 100000  # 最多保存10万个ID
        self._processed_ids_cleanup_interval = 300  # 每5分钟清理一次
        
        # 待重试的任务更新（任务ID -> 更新信息）
        self._pending_updates = {}
        self._pending_updates_lock = asyncio.Lock()
        self._max_pending_updates = 10000  # 最多保存1万个待重试更新
        self._retry_interval = 5  # 每5秒重试一次
        
        # 动态批次大小
        self.batch_size = 2000
        self.min_batch_size = 500
        self.max_batch_size = 5000
        
        # Stream积压监控配置
        self.enable_backlog_monitor = enable_backlog_monitor  # 是否启用积压监控
        self.backlog_monitor_interval = backlog_monitor_interval  # 监控采集间隔（秒）
        self.backlog_monitor_lock_key = f"{prefix}:BACKLOG_MONITOR_LOCK"  # 分布式锁键
        self.backlog_monitor_lock_ttl = backlog_monitor_interval * 2  # 锁的TTL（秒），设为采集间隔的2倍
        
    async def start(self):
        """启动消费者"""
        logger.info(f"Starting PostgreSQL consumer (simplified) on node: {self.node_id}")
        
        # 连接Redis
        # 构建连接参数，只在密码非空时传递
        async_redis_params = {
            'host': self.redis_config.host,
            'port': self.redis_config.port,
            'db': self.redis_config.db,
            'decode_responses': False
        }
        if self.redis_config.password:
            async_redis_params['password'] = self.redis_config.password
        
        self.redis_client = await redis.Redis(**async_redis_params)
        
        # 初始化 ConsumerManager（需要同步的 Redis 客户端）
        import redis as sync_redis
        # 构建连接参数，只在密码非空时传递
        sync_redis_params = {
            'host': self.redis_config.host,
            'port': self.redis_config.port,
            'db': self.redis_config.db,
            'decode_responses': True  # 使用字符串模式，与其他组件保持一致
        }
        if self.redis_config.password:
            sync_redis_params['password'] = self.redis_config.password
        
        sync_redis_client = sync_redis.StrictRedis(**sync_redis_params)
        
        # 配置 ConsumerManager
        # 初始队列列表包含TASK_CHANGES，其他队列会动态添加
        initial_queues = ['TASK_CHANGES']  # TASK_CHANGES是固定的
        consumer_config = {
            'redis_prefix': self.prefix,
            'queues': initial_queues,
            'worker_prefix': 'PG_CONSUMER',  # 使用不同的前缀，与task worker区分开
        }
        
        self.consumer_manager = ConsumerManager(
            redis_client=sync_redis_client,
            strategy=self.consumer_strategy,
            config=consumer_config
        )
        
        # 获取稳定的 consumer_id（使用TASK_CHANGES作为基准队列）
        self.consumer_id = self.consumer_manager.get_consumer_name('TASK_CHANGES')
        logger.debug(f"Using consumer_id: {self.consumer_id} with strategy: {self.consumer_strategy.value}")
        
        # 创建SQLAlchemy异步引擎
        if self.pg_config.dsn.startswith('postgresql://'):
            dsn = self.pg_config.dsn.replace('postgresql://', 'postgresql+psycopg://', 1)
        else:
            dsn = self.pg_config.dsn
            
        self.async_engine = create_async_engine(
            dsn,
            pool_size=50,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=300,
            echo=False
        )
        
        # 预热连接池
        logger.debug("Pre-warming database connection pool...")
        async with self.async_engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        
        # 创建异步会话工厂
        self.AsyncSessionLocal = sessionmaker(
            self.async_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        
        self._running = True
        
        # 先进行一次队列发现，确保ConsumerManager有正确的队列列表
        await self._initial_queue_discovery()
        
        # 创建离线worker恢复器（用于恢复TASK_CHANGES stream的离线消息）
        self.offline_recovery = OfflineWorkerRecovery(
            async_redis_client=self.redis_client,
            redis_prefix=self.prefix,
            worker_prefix='PG_CONSUMER',  # 使用PG_CONSUMER前缀
            consumer_manager=self.consumer_manager
        )
        
        # 启动消费任务（简化版：只保留必要的任务）
        self._tasks = [
            asyncio.create_task(self._consume_queues()),           # 消费新任务
            asyncio.create_task(self._consume_task_changes()),     # 消费任务变更事件
            asyncio.create_task(self._database_maintenance()),     # 数据库维护
            asyncio.create_task(self._retry_pending_updates()),    # 重试待更新的任务
            asyncio.create_task(self._start_offline_recovery())    # 离线worker恢复服务
        ]
        
        # 如果启用了积压监控，添加监控任务
        if self.enable_backlog_monitor:
            self._tasks.append(
                asyncio.create_task(self._stream_backlog_monitor())  # Stream积压监控
            )
            logger.info(f"Stream backlog monitor enabled with {self.backlog_monitor_interval}s interval")
        
        # 如果使用 HEARTBEAT 策略，ConsumerManager 会自动管理心跳
        if self.consumer_strategy == ConsumerStrategy.HEARTBEAT and self.consumer_manager:
            # 启动心跳（ConsumerManager 内部会处理）
            logger.debug("Heartbeat is managed by ConsumerManager")
        
        logger.debug("PostgreSQL consumer started successfully")
        
    async def stop(self):
        """停止消费者"""
        logger.debug("Stopping PostgreSQL consumer...")
        self._running = False
        
        # 停止离线恢复服务
        if hasattr(self, 'offline_recovery'):
            self.offline_recovery.stop()  # stop() 不是异步方法
        
        # 取消所有任务
        for task in self._tasks:
            task.cancel()
        
        # 等待任务完成
        await asyncio.gather(*self._tasks, return_exceptions=True)
        
        # 清理 ConsumerManager
        if self.consumer_manager:
            try:
                self.consumer_manager.cleanup()
                logger.debug(f"Cleaned up ConsumerManager for consumer: {self.consumer_id}")
            except Exception as e:
                logger.error(f"Error cleaning up ConsumerManager: {e}")
        
        # 关闭连接
        if self.redis_client:
            await self.redis_client.close()
        
        if self.async_engine:
            await self.async_engine.dispose()
            
        logger.debug("PostgreSQL consumer stopped")
   
    async def _initial_queue_discovery(self):
        """初始队列发现，在启动时执行一次"""
        try:
            pattern = f"{self.prefix}:QUEUE:*"
            new_queues = set()
            logger.info(f"Starting initial queue discovery with pattern: {pattern}")
            
            async for key in self.redis_client.scan_iter(match=pattern, count=100):
                # 从key中提取队列名，格式可能是：
                # - prefix:QUEUE:queue_name (普通队列)
                # - prefix:QUEUE:queue_name:priority (优先级队列)
                key_str = key.decode('utf-8')
                parts = key_str.split(":")
                if len(parts) >= 3:
                    # 去掉前缀和QUEUE部分
                    queue_parts = parts[2:]  # 从第3部分开始是队列名
                    queue_name = ":".join(queue_parts)  # 重新组合，保留优先级部分
                    new_queues.add(queue_name)
                    logger.info(f"Found queue: {queue_name} from key: {key_str}")
            
            if new_queues:
                logger.info(f"Initial queue discovery found {len(new_queues)} queues: {new_queues}")
                # 合并所有队列：TASK_CHANGES + 动态发现的队列
                all_queues = list(new_queues) + ['TASK_CHANGES']
                
                # 更新ConsumerManager的配置
                if self.consumer_manager:
                    self.consumer_manager.config['queues'] = all_queues
                    
                    # 更新worker的队列信息
                    # 获取实际的consumer_id（从心跳策略中）
                    if self.consumer_strategy == ConsumerStrategy.HEARTBEAT and hasattr(self.consumer_manager, '_heartbeat_strategy'):
                        actual_consumer_id = self.consumer_manager._heartbeat_strategy.consumer_id
                    else:
                        # 从consumer_name中提取（格式：consumer_id-queue）
                        actual_consumer_id = self.consumer_id.rsplit('-', 1)[0] if '-' in self.consumer_id else self.consumer_id
                    
                    worker_key = f"{self.prefix}:{self.consumer_manager.config.get('worker_prefix', 'PG_CONSUMER')}:{actual_consumer_id}"
                    try:
                        # 使用同步Redis客户端更新
                        self.consumer_manager.redis_client.hset(
                            worker_key, 
                            'queues', 
                            ','.join(all_queues)
                        )
                        logger.debug(f"Initial queue discovery - found queues: {all_queues}")
                    except Exception as e:
                        logger.error(f"Error updating initial worker queues: {e}")
                
                self._known_queues = new_queues
                
        except Exception as e:
            logger.error(f"Error in initial queue discovery: {e}")
    
    async def _discover_queues(self):
        """定期发现新队列"""
        while self._running:
            try:
                pattern = f"{self.prefix}:QUEUE:*"
                new_queues = set()
                # logger.info(f'{pattern=}')
                async for key in self.redis_client.scan_iter(match=pattern, count=100):
                    # 从key中提取队列名，格式可能是：
                    # - prefix:QUEUE:queue_name (普通队列)
                    # - prefix:QUEUE:queue_name:priority (优先级队列)
                    key_str = key.decode('utf-8')
                    parts = key_str.split(":")
                    if len(parts) >= 3:
                        # 去掉前缀和QUEUE部分
                        queue_parts = parts[2:]  # 从第3部分开始是队列名
                        queue_name = ":".join(queue_parts)  # 重新组合，保留优先级部分
                        new_queues.add(queue_name)
                
                # 为新发现的队列创建消费者组
                for queue in new_queues - self._known_queues:
                    # 正确构建stream_key，保留优先级部分
                    stream_key = f"{self.prefix}:QUEUE:{queue}"
                    try:
                        await self.redis_client.xgroup_create(
                            stream_key, self.consumer_group, id='0', mkstream=True
                        )
                        logger.info(f"Created consumer group for new queue: {queue} with stream_key: {stream_key}")
                    except redis.ResponseError:
                        pass
                
                # 更新ConsumerManager的队列列表（同步操作）
                if new_queues != self._known_queues:
                    logger.info(f"Queue discovery: found {len(new_queues)} queues: {new_queues}")
                    # 合并所有队列：TASK_CHANGES + 动态发现的队列
                    all_queues = list(new_queues) + ['TASK_CHANGES']
                    
                    # 更新ConsumerManager的配置
                    if self.consumer_manager:
                        self.consumer_manager.config['queues'] = all_queues
                        
                        # 更新worker的队列信息
                        # 获取实际的consumer_id（从心跳策略中）
                        if self.consumer_strategy == ConsumerStrategy.HEARTBEAT and hasattr(self.consumer_manager, '_heartbeat_strategy'):
                            actual_consumer_id = self.consumer_manager._heartbeat_strategy.consumer_id
                        else:
                            # 从consumer_name中提取（格式：consumer_id-queue）
                            actual_consumer_id = self.consumer_id.rsplit('-', 1)[0] if '-' in self.consumer_id else self.consumer_id
                        
                        worker_key = f"{self.prefix}:{self.consumer_manager.config.get('worker_prefix', 'PG_CONSUMER')}:{actual_consumer_id}"
                        try:
                            # 使用同步Redis客户端更新
                            self.consumer_manager.redis_client.hset(
                                worker_key, 
                                'queues', 
                                ','.join(all_queues)
                            )
                            logger.debug(f"Updated ConsumerManager queues: {all_queues}")
                        except Exception as e:
                            logger.error(f"Error updating worker queues: {e}")
                
                self._known_queues = new_queues
                await asyncio.sleep(30)
                
            except Exception as e:
                import traceback
                traceback.print_exc()
                logger.error(f"Error discovering queues: {e}")
                await asyncio.sleep(10)
    
    async def _consume_queue(self, queue_name: str):
        """消费单个队列的任务（包括优先级队列）"""
        # logger.info(f"Starting to consume queue: {queue_name}")
        # 判断是否是优先级队列
        is_priority_queue = ':' in queue_name and queue_name.rsplit(':', 1)[-1].isdigit()
        
        if is_priority_queue:
            # 优先级队列格式：base_queue:priority (如 robust_bench2:2)
            base_queue = queue_name.rsplit(':', 1)[0]
            priority = queue_name.rsplit(':', 1)[1]
            stream_key = f"{self.prefix}:QUEUE:{base_queue}:{priority}"
        else:
            # 普通队列
            stream_key = f"{self.prefix}:QUEUE:{queue_name}"
        
        logger.debug(f"Consuming queue: {queue_name}, stream_key: {stream_key}, is_priority: {is_priority_queue}")
        
        check_backlog = True
        lastid = "0-0"
        
        # pg_consumer 应该使用统一的 consumer_id，而不是为每个队列创建新的
        # 因为 pg_consumer 的职责是消费所有队列的消息并写入数据库
        # 它不是真正的任务执行者，所以不需要为每个队列创建独立的 consumer
        consumer_name = self.consumer_id
        
        # ConsumerManager会自动处理离线worker的pending消息恢复
        # 不需要手动恢复
        
        while self._running and queue_name in self._known_queues:
            try:
                myid = lastid if check_backlog else ">"
                
                messages = await self.redis_client.xreadgroup(
                    self.consumer_group,
                    consumer_name,  # 使用ConsumerManager管理的consumer_name
                    {stream_key: myid},
                    count=10000,
                    block=1000 if not check_backlog else 0
                )
                if not messages or (messages and len(messages[0][1]) == 0):
                    check_backlog = False
                    continue
                
                if messages:
                    await self._process_messages(messages)
                    self._consecutive_errors[queue_name] = 0
                    
                    if messages[0] and messages[0][1]:
                        lastid = messages[0][1][-1][0].decode('utf-8') if isinstance(messages[0][1][-1][0], bytes) else messages[0][1][-1][0]
                        check_backlog = len(messages[0][1]) >= 2000
                    
            except redis.ResponseError as e:
                if "NOGROUP" in str(e):
                    try:
                        await self.redis_client.xgroup_create(
                            stream_key, self.consumer_group, id='0', mkstream=True
                        )
                        logger.debug(f"Recreated consumer group for queue: {queue_name}")
                        check_backlog = True
                        lastid = "0-0"
                    except:
                        pass
                else:
                    logger.error(f"Redis error for queue {queue_name}: {e}")
                    self._consecutive_errors[queue_name] += 1
                    
                if self._consecutive_errors[queue_name] > 10:
                    logger.debug(f"Too many errors for queue {queue_name}, will retry later")
                    await asyncio.sleep(30)
                    self._consecutive_errors[queue_name] = 0
                    
            except Exception as e:
                logger.error(f"Error consuming queue {queue_name}: {e}", exc_info=True)
                self._consecutive_errors[queue_name] += 1
                await asyncio.sleep(1)
    
    async def _consume_queues(self):
        """启动所有队列的消费任务"""
        discover_task = asyncio.create_task(self._discover_queues())
        queue_tasks = {}
        while self._running:
            try:
                for queue in self._known_queues:
                    if queue not in queue_tasks or queue_tasks[queue].done():
                        queue_tasks[queue] = asyncio.create_task(self._consume_queue(queue))
                        logger.debug(f"Started consumer task for queue: {queue}")
                
                for queue in list(queue_tasks.keys()):
                    if queue not in self._known_queues:
                        queue_tasks[queue].cancel()
                        del queue_tasks[queue]
                        logger.debug(f"Stopped consumer task for removed queue: {queue}")
                
                await asyncio.sleep(10)
                
            except Exception as e:
                logger.error(f"Error in consume_queues manager: {e}")
                await asyncio.sleep(5)
        
        discover_task.cancel()
        for task in queue_tasks.values():
            task.cancel()
        
        await asyncio.gather(discover_task, *queue_tasks.values(), return_exceptions=True)
                
    async def _process_messages(self, messages: List):
        """处理消息并保存到PostgreSQL"""
        tasks_to_insert = []
        ack_batch = []
        
        for stream_key, stream_messages in messages:
            if not stream_messages:
                continue
                
            stream_key_str = stream_key.decode('utf-8') if isinstance(stream_key, bytes) else stream_key
            msg_ids_to_ack = []
            
            for msg_id, data in stream_messages:
                try:
                    if not msg_id or not data:
                        continue
                    
                    msg_id_str = msg_id.decode('utf-8') if isinstance(msg_id, bytes) else str(msg_id)
                    
                    # 使用公共方法解析消息
                    task_info = self._parse_stream_message(msg_id_str, data)
                    if task_info:
                        tasks_to_insert.append(task_info)
                        msg_ids_to_ack.append(msg_id)
                    
                except Exception as e:
                    logger.error(f"Error processing message {msg_id}: {e}")
            
            if msg_ids_to_ack:
                ack_batch.append((stream_key, msg_ids_to_ack))
        
        if tasks_to_insert:
            await self._insert_tasks(tasks_to_insert)
            
            # 将成功插入的任务ID添加到内存集合中
            async with self._processed_ids_lock:
                for task in tasks_to_insert:
                    self._processed_task_ids.add(task['id'])
                
                # 如果集合过大，清理最早的一半
                if len(self._processed_task_ids) > self._processed_ids_max_size:
                    # 只保留最新的一半ID
                    ids_list = list(self._processed_task_ids)
                    keep_count = self._processed_ids_max_size // 2
                    self._processed_task_ids = set(ids_list[-keep_count:])
                    logger.debug(f"Cleaned processed IDs cache, kept {keep_count} most recent IDs")
            
            if ack_batch:
                pipeline = self.redis_client.pipeline()
                for stream_key, msg_ids in ack_batch:
                    pipeline.xack(stream_key, self.consumer_group, *msg_ids)
                
                try:
                    await pipeline.execute()
                    total_acked = sum(len(msg_ids) for _, msg_ids in ack_batch)
                    logger.debug(f"Successfully ACKed {total_acked} messages")
                except Exception as e:
                    logger.error(f"Error executing batch ACK: {e}")
            
    async def _insert_tasks(self, tasks: List[Dict[str, Any]]):
        """批量插入任务到PostgreSQL（只处理tasks表）"""
        if not tasks:
            return
            
        logger.info(f"Attempting to insert {len(tasks)} tasks to tasks table")
        try:
            async with self.AsyncSessionLocal() as session:
                # 插入tasks表 - 使用批量INSERT忽略冲突
                # 由于stream_id在实践中是唯一的，我们可以简单地忽略重复
                tasks_query = text("""
                    INSERT INTO tasks (stream_id, queue, namespace, scheduled_task_id, 
                                      payload, priority, created_at, source, metadata)
                    VALUES (:stream_id, :queue, :namespace, :scheduled_task_id, 
                           CAST(:payload AS jsonb), :priority, :created_at, :source, CAST(:metadata AS jsonb))
                    ON CONFLICT DO NOTHING
                    RETURNING stream_id;
                """)
                
                # 准备tasks表的数据
                tasks_data = []
                for task in tasks:
                    task_data = json.loads(task['task_data'])
                    
                    # 从task_data中获取scheduled_task_id
                    scheduled_task_id = task_data.get('scheduled_task_id') or task.get('scheduled_task_id')
                    
                    # 根据是否有scheduled_task_id来判断任务来源
                    if scheduled_task_id:
                        source = 'scheduler'  # 定时任务
                    else:
                        source = 'redis_stream'  # 普通任务
                    
                    tasks_data.append({
                        'stream_id': task['id'],  # Redis Stream ID作为stream_id
                        'queue': task['queue_name'],
                        'namespace': self.namespace_name,
                        'scheduled_task_id': str(scheduled_task_id) if scheduled_task_id else None,
                        'payload': task['task_data'],  # 完整的任务数据
                        'priority': task['priority'],
                        'created_at': task['created_at'],
                        'source': source,
                        'metadata': task.get('metadata', '{}')
                    })
                
                # 批量插入 - 使用executemany提高性能
                logger.debug(f"Executing batch insert with {len(tasks_data)} tasks")
                
                try:
                    # 使用executemany批量插入
                    result = await session.execute(tasks_query, tasks_data)
                    
                    # 获取实际插入的记录数
                    inserted_count = result.rowcount
                    
                    # if inserted_count > 0:
                    #     logger.info(f"Successfully inserted {inserted_count} new tasks to tasks table")
                    # else:
                    #     logger.info(f"No new tasks inserted (all may be duplicates)")
                    
                    await session.commit()
                    logger.debug("Tasks table batch insert transaction completed")
                    
                except Exception as e:
                    logger.error(f"Error in batch insert, trying fallback: {e}")
                    await session.rollback()
                    
                    # 如果批量插入失败，降级为小批量插入（每批10条）
                    batch_size = 10
                    total_inserted = 0
                    
                    for i in range(0, len(tasks_data), batch_size):
                        batch = tasks_data[i:i+batch_size]
                        try:
                            result = await session.execute(tasks_query, batch)
                            batch_inserted = result.rowcount
                            if batch_inserted > 0:
                                total_inserted += batch_inserted
                            await session.commit()
                        except Exception as batch_error:
                            logger.error(f"Batch {i//batch_size + 1} failed: {batch_error}")
                            await session.rollback()
                    
                    if total_inserted > 0:
                        logger.info(f"Fallback insert completed: {total_inserted} tasks inserted")
                    else:
                        logger.info(f"No new tasks inserted in fallback mode")
                
        except Exception as e:
            logger.error(f"Error inserting tasks to PostgreSQL: {e}")
    
    async def _consume_task_changes(self):
        """消费任务变更事件流 - 基于事件驱动的更新（支持pending消息恢复）"""
        change_stream_key = f"{self.prefix}:TASK_CHANGES"
        consumer_group = f"{self.prefix}_changes_consumer"
        
        # 使用 ConsumerManager 管理的 consumer name
        # 这样 ConsumerManager 才能正确跟踪和恢复这个流的待处理消息
        consumer_name = self.consumer_manager.get_consumer_name('TASK_CHANGES')
        
        # 创建消费者组
        try:
            await self.redis_client.xgroup_create(
                change_stream_key, consumer_group, id='0', mkstream=True
            )
            logger.debug(f"Created consumer group for task changes stream")
        except redis.ResponseError:
            pass
        
        # 模仿 listen_event_by_task 的写法：先处理pending消息，再处理新消息
        check_backlog = True
        lastid = "0-0"
        batch_size = 1000
        
        while self._running:
            try:
                # 决定读取位置：如果有backlog，从lastid开始；否则读取新消息
                if check_backlog:
                    myid = lastid
                else:
                    myid = ">"
                
                messages = await self.redis_client.xreadgroup(
                    consumer_group,
                    consumer_name,  # 使用 ConsumerManager 管理的 consumer name
                    {change_stream_key: myid},
                    count=batch_size,
                    block=1000 if not check_backlog else 0  # backlog时不阻塞
                )
                
                if not messages:
                    check_backlog = False
                    continue
                
                # 检查是否还有更多backlog消息
                if messages and len(messages[0][1]) > 0:
                    check_backlog = len(messages[0][1]) >= batch_size
                else:
                    check_backlog = False
                
                # 收集消息ID和对应的task_id
                msg_to_task = {}  # msg_id -> task_id 映射
                
                for _, stream_messages in messages:
                    for msg_id, data in stream_messages:
                        try:
                            # 更新lastid（无论消息是否处理成功）
                            if isinstance(msg_id, bytes):
                                lastid = msg_id.decode('utf-8')
                            else:
                                lastid = str(msg_id)
                            
                            task_key = data[b'id']
                            task_key = task_key.decode('utf-8') if isinstance(task_key, bytes) else str(task_key)
                            
                            # 从完整的task_key格式提取stream_id
                            # 格式: namespace:TASK:stream_id:queue_name
                            stream_id = None
                            if ':TASK:' in task_key:
                                parts = task_key.split(':TASK:')
                                if len(parts) == 2:
                                    # 再从右边部分提取stream_id
                                    right_parts = parts[1].split(':')
                                    if right_parts:
                                        stream_id = right_parts[0]  # 提取stream_id
                            
                            if stream_id:
                                # 存储元组: (stream_id, task_key)
                                msg_to_task[msg_id] = (stream_id, task_key)
                            else:
                                logger.warning(f"Cannot extract stream_id from task_key: {task_key}")
                        except Exception as e:
                            import traceback
                            traceback.print_exc()
                            logger.error(f"Error processing change event {msg_id}: {e} {data=}")
                            # 解析失败的消息也应该ACK，避免一直重试
                            await self.redis_client.xack(change_stream_key, consumer_group, msg_id)
                
                if msg_to_task:
                    # 批量更新任务，返回成功更新的task_id列表
                    # msg_to_task 的值现在是元组 (stream_id, task_key)
                    id_tuples = list(set(msg_to_task.values()))
                    logger.info(f"Processing {len(id_tuples)} task updates from change stream")
                    # logger_f.write(f'{id_tuples=} \n')
                    successful_tuples = await self._update_tasks_by_event(id_tuples)
                    
                    # 只ACK成功更新的消息
                    ack_ids = []
                    failed_count = 0
                    for msg_id, id_tuple in msg_to_task.items():
                        if successful_tuples and id_tuple in successful_tuples:
                            ack_ids.append(msg_id)
                        else:
                            failed_count += 1
                    
                    if ack_ids:
                        await self.redis_client.xack(change_stream_key, consumer_group, *ack_ids)
                        if len(ack_ids) > 0:
                            logger.info(f"Updated {len(ack_ids)} task statuses")
                    
                    if failed_count > 0:
                        logger.debug(f"Failed to update {failed_count} tasks, will retry")
                
            except redis.ResponseError as e:
                if "NOGROUP" in str(e):
                    # 如果消费者组不存在，重新创建
                    try:
                        await self.redis_client.xgroup_create(
                            change_stream_key, consumer_group, id='0', mkstream=True
                        )
                        logger.debug(f"Recreated consumer group for task changes stream")
                        check_backlog = True
                        lastid = "0-0"
                    except:
                        pass
                else:
                    logger.error(f"Redis error in consume_task_changes: {e}")
                    await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Error in consume_task_changes: {e}", exc_info=True)
                await asyncio.sleep(1)
    
    async def _update_tasks_by_event(self, id_tuples: List[tuple]) -> Set[tuple]:
        """基于事件ID批量更新任务状态
        
        Args:
            id_tuples: 元组列表，每个元组为 (stream_id, task_key)
        
        Returns:
            成功更新的元组集合
        """
        if not id_tuples:
            return set()
        
        successful_tuples = set()
        
        try:
            pipeline = self.redis_client.pipeline()
            for stream_id, task_key in id_tuples:
                pipeline.hgetall(task_key)
            
            redis_values = await pipeline.execute()
            updates = []
            valid_tuples = []  # 记录有效的元组
            if len(id_tuples) != len(redis_values):
                logger.error(f'Mismatch: {len(id_tuples)=} {len(redis_values)=}')
                # 不抛出异常，继续处理能处理的
            
            for i, (stream_id, task_key) in enumerate(id_tuples):
                if i >= len(redis_values):
                    logger.error(f'Missing redis value for task_key={task_key}')
                    continue
                    
                hash_data = redis_values[i]
                
                if not hash_data:
                    logger.debug(f'No hash data for task_key={task_key}')
                    continue
                
                try:
                    # 从task_key解析出consumer_group
                    # task_key格式: namespace:TASK:stream_id:group_name
                    # 其中group_name就是完整的consumer_group（格式: jettask:QUEUE:queue_name:task_name）
                    parts = task_key.split(':', 3)  # 最多分割成4部分
                    if len(parts) == 4:
                        # parts[0] = namespace (如 'default')
                        # parts[1] = 'TASK'
                        # parts[2] = stream_id
                        # parts[3] = group_name (consumer_group)
                        consumer_group = parts[3]  # 直接使用group_name作为consumer_group
                        logger.debug(f"Extracted consumer_group from task_key: {consumer_group}")
                    else:
                        logger.warning(f"Cannot parse consumer_group from task_key: {task_key}")
                        continue
                    
                    # 从consumer_group中提取task_name
                    # consumer_group格式: prefix:QUEUE:queue:task_name (如 jettask:QUEUE:robust_bench2:robust_benchmark.benchmark_task)
                    task_name = None
                    if consumer_group:
                        parts = consumer_group.split(':')
                        if len(parts) >= 4:
                            # 最后一部分是task_name
                            task_name = parts[-1]
                            logger.debug(f"Extracted task_name '{task_name}' from consumer_group '{consumer_group}'")
                    
                    # 使用stream_id作为任务ID
                    update_info = self._parse_task_hash(stream_id, hash_data)
                    if update_info:
                        # 添加consumer_group和task_name到更新信息中
                        update_info['consumer_group'] = consumer_group
                        update_info['task_name'] = task_name or 'unknown'  # 如果无法提取task_name，使用'unknown'
                        # consumer_name就是worker_id（执行任务的实际worker）
                        update_info['consumer_name'] = update_info.get('worker_id')
                        updates.append(update_info)
                        valid_tuples.append((stream_id, task_key))
                    else:
                        logger.debug(f'Failed to parse stream_id={stream_id} hash_data={hash_data}')
                except Exception as e:
                    logger.error(f'Error parsing task stream_id={stream_id}: {e}')
                    continue
            if updates:
                logger.info(f"Attempting to update {len(updates)} tasks, first few: {[u['id'] for u in updates[:3]]}")
                # logger_f.write(f'{updates=} \n')
                try:
                    # _update_tasks 现在返回成功更新的ID集合
                    batch_successful = await self._update_tasks(updates)
                    # 将成功的stream_id映射回元组
                    for stream_id in batch_successful:
                        for tuple_item in valid_tuples:
                            if tuple_item[0] == stream_id:  # stream_id匹配
                                successful_tuples.add(tuple_item)
                    if batch_successful:
                        logger.info(f"Successfully updated {len(batch_successful)} tasks from change events")
                    else:
                        logger.warning(f"No tasks were successfully updated")
                except Exception as e:
                    logger.error(f"Error in batch update: {e}")
                    # 批量更新失败，尝试逐个更新
                    for update, tuple_item in zip(updates, valid_tuples):
                        try:
                            single_successful = await self._update_tasks([update])
                            if update['id'] in single_successful:
                                successful_tuples.add(tuple_item)
                        except Exception as single_error:
                            logger.error(f"Failed to update task {tuple_item[0]}: {single_error}")
            
        except Exception as e:
            logger.error(f"Error updating tasks by event: {e}", exc_info=True)
        logger.debug(f'{successful_tuples=}')
        return successful_tuples
    
    def _parse_task_hash(self, task_id: str, hash_data: dict) -> Optional[dict]:
        """解析Redis Hash数据"""
        update_info = {
            'id': task_id,
            'status': None,
            'result': None,
            'error_message': None,
            'started_at': None,
            'completed_at': None,
            'worker_id': None,
            'execution_time': None,
            'duration': None
        }
        
        try:
            from jettask.utils.serializer import loads_str
            
            hash_dict = {}
            for k, v in hash_data.items():
                key = k.decode('utf-8') if isinstance(k, bytes) else k
                if isinstance(v, bytes):
                    try:
                        value = loads_str(v)
                        if isinstance(value, (dict, list)):
                            value = json.dumps(value, ensure_ascii=False)
                        else:
                            value = str(value)
                    except:
                        try:
                            value = v.decode('utf-8')
                        except:
                            value = str(v)
                else:
                    value = v
                hash_dict[key] = value
            
            update_info['status'] = hash_dict.get('status')
            update_info['error_message'] = hash_dict.get('error_msg') or hash_dict.get('exception')
            
            # 转换时间戳
            for time_field in ['started_at', 'completed_at']:
                if hash_dict.get(time_field):
                    try:
                        time_str = hash_dict[time_field]
                        if isinstance(time_str, str) and time_str.startswith("b'") and time_str.endswith("'"):
                            time_str = time_str[2:-1]
                        update_info[time_field] = datetime.fromtimestamp(float(time_str), tz=timezone.utc)
                    except:
                        pass
            
            update_info['worker_id'] = hash_dict.get('consumer') or hash_dict.get('worker_id')
            
            # 转换数值 - 直接存储原始秒数值
            for num_field in ['execution_time', 'duration']:
                if hash_dict.get(num_field):
                    try:
                        num_str = hash_dict[num_field]
                        # 直接存储浮点数秒值
                        update_info[num_field] = float(num_str)
                    except:
                        pass
            
            # 处理result
            if 'result' in hash_dict:
                result_str = hash_dict['result']
                if result_str == 'null':
                    update_info['result'] = None
                else:
                    update_info['result'] = result_str
            
            # 只返回有数据的更新
            if any(v is not None for k, v in update_info.items() if k != 'id'):
                return update_info
            
        except Exception as e:
            logger.error(f"Failed to parse hash data for task {task_id}: {e}")
        
        return None
    
    async def _update_tasks(self, updates: List[Dict[str, Any]]) -> Set[str]:
        """批量更新任务状态（使用UPSERT逻辑处理task_runs表）
        
        Returns:
            成功更新的stream_id集合
        """
        if not updates:
            return set()
            
        try:
            async with self.AsyncSessionLocal() as session:
                # V3结构：使用UPSERT逻辑处理task_runs表
                stream_ids = [u['id'] for u in updates]
                logger.info(f"Upserting {len(stream_ids)} task_runs records")
                
                # 对于分区表，我们需要使用不同的UPSERT策略
                # 先尝试UPDATE，如果没有更新到任何行，则INSERT
                upsert_query = text("""
                    WITH updated AS (
                        UPDATE task_runs SET
                            consumer_name = COALESCE(CAST(:consumer_name AS TEXT), consumer_name),
                            status = CASE 
                                WHEN CAST(:status AS TEXT) IS NULL THEN status
                                WHEN status = 'pending' THEN COALESCE(CAST(:status AS TEXT), status)
                                WHEN status = 'running' AND CAST(:status AS TEXT) IN ('success', 'failed', 'timeout', 'skipped') THEN CAST(:status AS TEXT)
                                WHEN status IN ('success', 'failed', 'timeout', 'skipped') THEN status
                                ELSE COALESCE(CAST(:status AS TEXT), status)
                            END,
                            result = CASE
                                WHEN status IN ('success', 'failed', 'timeout', 'skipped') AND CAST(:status AS TEXT) NOT IN ('success', 'failed', 'timeout', 'skipped') THEN result
                                ELSE COALESCE(CAST(:result AS jsonb), result)
                            END,
                            error_message = CASE
                                WHEN status IN ('success', 'failed', 'timeout', 'skipped') AND CAST(:status AS TEXT) NOT IN ('success', 'failed', 'timeout', 'skipped') THEN error_message
                                ELSE COALESCE(CAST(:error_message AS TEXT), error_message)
                            END,
                            start_time = COALESCE(CAST(:started_at AS TIMESTAMPTZ), start_time),
                            end_time = CASE
                                WHEN status IN ('success', 'failed', 'timeout', 'skipped') AND CAST(:status AS TEXT) NOT IN ('success', 'failed', 'timeout', 'skipped') THEN end_time
                                ELSE COALESCE(CAST(:completed_at AS TIMESTAMPTZ), end_time)
                            END,
                            worker_id = COALESCE(CAST(:worker_id AS TEXT), worker_id),
                            duration = COALESCE(CAST(:duration AS DOUBLE PRECISION), duration),
                            execution_time = COALESCE(CAST(:execution_time AS DOUBLE PRECISION), execution_time),
                            updated_at = CURRENT_TIMESTAMP
                        WHERE stream_id = :stream_id AND consumer_group = :consumer_group
                        RETURNING stream_id
                    )
                    INSERT INTO task_runs (
                        stream_id, task_name, consumer_group, consumer_name, status, result, error_message, 
                        start_time, end_time, worker_id, duration, execution_time,
                        created_at, updated_at
                    )
                    SELECT 
                        :stream_id, :task_name, :consumer_group, :consumer_name,
                        COALESCE(CAST(:status AS TEXT), 'pending'),
                        CAST(:result AS jsonb),
                        CAST(:error_message AS TEXT),
                        CAST(:started_at AS TIMESTAMPTZ),
                        CAST(:completed_at AS TIMESTAMPTZ),
                        CAST(:worker_id AS TEXT),
                        CAST(:duration AS DOUBLE PRECISION),
                        CAST(:execution_time AS DOUBLE PRECISION),
                        CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                    WHERE NOT EXISTS (SELECT 1 FROM updated)
                    RETURNING stream_id;
                """)
                
                # 为每个更新转换参数名称（从id改为stream_id）
                run_updates = []
                for update in updates:
                    run_update = update.copy()
                    run_update['stream_id'] = run_update.pop('id')  # 将id改为stream_id
                    # consumer_group 已经在 update_info 中了，不需要额外处理
                    run_updates.append(run_update)
                
                # 批量执行UPSERT - 使用事务批处理提高性能
                successful_count = 0
                batch_size = 20  # 每批处理20条记录
                
                for i in range(0, len(run_updates), batch_size):
                    batch = run_updates[i:i+batch_size]
                    
                    try:
                        # 在一个事务中处理整批
                        for run_update in batch:
                            result = await session.execute(upsert_query, run_update)
                            if result.rowcount > 0:
                                successful_count += 1
                        
                        # 批量提交
                        await session.commit()
                        logger.debug(f"Batch {i//batch_size + 1} committed: {len(batch)} records")
                        
                    except Exception as e:
                        logger.error(f"Batch {i//batch_size + 1} failed, trying individual records: {e}")
                        await session.rollback()
                        
                        # 如果批处理失败，回退到逐个处理这批记录
                        for run_update in batch:
                            try:
                                result = await session.execute(upsert_query, run_update)
                                await session.commit()
                                if result.rowcount > 0:
                                    successful_count += 1
                            except Exception as individual_error:
                                logger.error(f"Individual upsert failed for {run_update.get('stream_id')}: {individual_error}")
                                await session.rollback()
                
                # 记录成功更新的数量
                if successful_count > 0:
                    logger.info(f"Upserted {successful_count}/{len(run_updates)} task_runs records")
                
                # 检查哪些任务是完成状态，需要从Redis中删除
                completed_task_keys = []
                for update in updates:
                    status = update.get('status')
                    # 如果状态是完成状态（success, error, cancel等）
                    if status in ['success', 'error', 'failed', 'cancel', 'cancelled', 'timeout', 'skipped']:
                        # 构建task_key
                        # task_key格式: namespace:TASK:stream_id:group_name
                        stream_id = update['id']
                        consumer_group = update.get('consumer_group')
                        if consumer_group:
                            # 从consumer_group提取namespace
                            # consumer_group格式: prefix:QUEUE:queue:task_name
                            parts = consumer_group.split(':', 1)
                            namespace = parts[0] if parts else 'default'
                            task_key = f"{namespace}:TASK:{stream_id}:{consumer_group}"
                            completed_task_keys.append(task_key)
                            logger.info(f"Task {stream_id} with status {status} will be deleted from Redis: {task_key}")
                
                # 从Redis中删除已完成的任务
                if completed_task_keys:
                    try:
                        pipeline = self.redis_client.pipeline()
                        for task_key in completed_task_keys:
                            pipeline.delete(task_key)
                        deleted_results = await pipeline.execute()
                        deleted_count = sum(1 for r in deleted_results if r > 0)
                        if deleted_count > 0:
                            logger.info(f"Deleted {deleted_count} completed tasks from Redis")
                    except Exception as e:
                        logger.error(f"Error deleting completed tasks from Redis: {e}")
                
                # UPSERT 操作总是成功的，返回所有stream_id
                # 不需要复杂的错误处理，因为UPSERT保证了操作的原子性
                return set(stream_ids)
                
        except Exception as e:
            logger.error(f"Error upserting task statuses: {e}")
            return set()  # 出错时返回空集
    
    async def _retry_pending_updates(self):
        """定期重试待更新的任务"""
        while self._running:
            try:
                await asyncio.sleep(self._retry_interval)  # 等待一段时间
                
                # 获取待重试的更新
                async with self._pending_updates_lock:
                    if not self._pending_updates:
                        continue
                    
                    # 取出所有待重试的更新
                    pending_items = list(self._pending_updates.items())
                    self._pending_updates.clear()
                
                if pending_items:
                    
                    # 重新尝试更新
                    updates = [update_info for _, update_info in pending_items]
                    logger.debug(f"Retrying {len(pending_items)} pending task updates {[_ for _, update_info in pending_items]=}")
                    logger_f.write(f'{time.time()=} Retrying {len(pending_items)} pending task updates {[_ for _, update_info in pending_items]=}\n')
                    logger_f.flush()
                    await self._update_tasks(updates)
                    
            except Exception as e:
                logger.error(f"Error in retry pending updates: {e}")
                await asyncio.sleep(5)
    
    async def _start_offline_recovery(self):
        """启动离线worker恢复服务，恢复离线PG_CONSUMER的消息"""
        logger.debug("Starting offline worker recovery service for PG_CONSUMER")
        
        # 等待consumer manager初始化和队列发现
        # await asyncio.sleep(5)
        
        while self._running:
            try:
                total_recovered = 0
                
                # 1. 恢复普通队列的消息
                # for queue in self._known_queues:
                #     # logger.info(f'{queue=}')
                #     try:
                #         recovered = await self.offline_recovery.recover_offline_workers(
                #             queue=queue,
                #             current_consumer_name=self.consumer_id,
                #             process_message_callback=self._process_recovered_queue_message
                #         )
                        
                #         if recovered > 0:
                #             logger.info(f"Recovered {recovered} messages from queue {queue}")
                #             total_recovered += recovered
                            
                #     except Exception as e:
                #         logger.error(f"Error recovering queue {queue}: {e}")
                
                # 2. 恢复TASK_CHANGES stream的消息
                recovered = await self._recover_task_changes_offline_messages()
                if recovered > 0:
                    logger.debug(f"Recovered {recovered} TASK_CHANGES messages")
                    total_recovered += recovered
                
                if total_recovered > 0:
                    logger.debug(f"Total recovered {total_recovered} messages in this cycle")
                
                # 每30秒扫描一次
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error in offline recovery service: {e}")
                await asyncio.sleep(10)
    
    async def _recover_task_changes_offline_messages(self) -> int:
        """恢复TASK_CHANGES stream的离线消息"""
        # 使用 OfflineWorkerRecovery 的标准接口
        try:
            # 为TASK_CHANGES定义自定义的队列格式化器
            def task_changes_formatter(queue):
                # 对于TASK_CHANGES，直接返回stream key（不加QUEUE:前缀）
                if queue == 'TASK_CHANGES':
                    return f"{self.prefix}:TASK_CHANGES"
                else:
                    return f"{self.prefix}:QUEUE:{queue}"
            
            # 创建专门用于TASK_CHANGES的恢复器
            task_changes_recovery = OfflineWorkerRecovery(
                async_redis_client=self.redis_client,
                redis_prefix=self.prefix,
                worker_prefix='PG_CONSUMER',
                queue_formatter=task_changes_formatter
            )
            
            # 调用标准的恢复方法
            # TASK_CHANGES作为队列名传入，会被正确处理
            recovered = await task_changes_recovery.recover_offline_workers(
                queue='TASK_CHANGES',  # 这个队列名会用于查找离线worker
                current_consumer_name=self.consumer_id,
                process_message_callback=self._process_recovered_task_change_v2
            )
            
            return recovered
            
        except Exception as e:
            logger.error(f"Error in recover_task_changes_offline_messages: {e}")
            return 0
    
    async def _process_recovered_task_change_v2(self, msg_id, msg_data, queue, consumer_id):
        """处理恢复的TASK_CHANGES消息（符合OfflineWorkerRecovery的回调接口）"""
        try:
            logger.debug(f'处理恢复的TASK_CHANGES消息（符合OfflineWorkerRecovery的回调接口） {msg_data=}')
            # 解析消息 - 现在使用task_id而不是event_id
            if b'task_id' in msg_data:
                # 使用msgpack解压task_id
                compressed_task_id = msg_data[b'task_id']
                task_key = msgpack.unpackb(compressed_task_id)
                task_key = task_key.decode('utf-8') if isinstance(task_key, bytes) else str(task_key)
                
                # 从完整的task_key格式提取stream_id
                # 格式: namespace:TASK:stream_id:queue_name
                stream_id = None
                if ':TASK:' in task_key:
                    parts = task_key.split(':TASK:')
                    if len(parts) == 2:
                        # 再从右边部分提取stream_id
                        right_parts = parts[1].split(':')
                        if right_parts:
                            stream_id = right_parts[0]  # 提取stream_id
                
                if stream_id:
                    logger.debug(f"Processing recovered TASK_CHANGES message: {stream_id} from offline worker {consumer_id}")
                    # 更新任务状态 - 传入(stream_id, task_key)元组
                    await self._update_tasks_by_event([(stream_id, task_key)])
                else:
                    logger.warning(f"Cannot extract stream_id from task_key: {task_key}")
                
                # ACK消息
                change_stream_key = f"{self.prefix}:TASK_CHANGES"
                consumer_group = f"{self.prefix}_changes_consumer"
                await self.redis_client.xack(change_stream_key, consumer_group, msg_id)
                
        except Exception as e:
            logger.error(f"Error processing recovered task change {msg_id}: {e}")
    
    async def _database_maintenance(self):
        """定期执行数据库维护任务"""
        last_analyze_time = 0
        analyze_interval = 7200  # 每2小时执行一次ANALYZE
        
        while self._running:
            try:
                current_time = time.time()
                
                if current_time - last_analyze_time > analyze_interval:
                    async with self.AsyncSessionLocal() as session:
                        logger.debug("Running ANALYZE on tasks and task_runs tables...")
                        await session.execute(text("ANALYZE tasks"))
                        await session.execute(text("ANALYZE task_runs"))
                        await session.commit()
                        logger.debug("ANALYZE completed successfully for both tables")
                        last_analyze_time = current_time
                
                await asyncio.sleep(300)  # 每5分钟检查一次
                
            except Exception as e:
                logger.error(f"Error in database maintenance: {e}")
                await asyncio.sleep(60)
    
    async def _stream_backlog_monitor(self):
        """Stream积压监控任务 - 使用分布式锁确保只有一个实例采集"""
        # await asyncio.sleep(10)  # 启动后延迟10秒开始
        
        while self._running:
            try:
                # 尝试获取分布式锁
                lock_acquired = await self._try_acquire_monitor_lock()
                
                if lock_acquired:
                    try:
                        logger.debug(f"Acquired backlog monitor lock, collecting metrics...")
                        await self._collect_stream_backlog_metrics()
                        logger.debug("Stream backlog metrics collected successfully")
                    finally:
                        # 释放锁
                        await self._release_monitor_lock()
                else:
                    logger.debug("Another instance is collecting backlog metrics, skipping...")
                
                # 等待下一次采集
                await asyncio.sleep(self.backlog_monitor_interval)
                
            except Exception as e:
                logger.error(f"Error in stream backlog monitor: {e}")
                await asyncio.sleep(30)  # 出错后等待30秒
    
    async def _try_acquire_monitor_lock(self) -> bool:
        """尝试获取监控锁（使用Redis原生锁）"""
        try:
            # 使用SET NX EX命令实现分布式锁
            # NX: 只在键不存在时设置
            # EX: 设置过期时间（秒）
            result = await self.redis_client.set(
                self.backlog_monitor_lock_key.encode(),
                self.node_id.encode(),  # 锁的值为当前节点ID
                nx=True,  # 只在不存在时设置
                ex=self.backlog_monitor_lock_ttl  # 过期时间
            )
            return result is not None
        except Exception as e:
            logger.error(f"Error acquiring monitor lock: {e}")
            return False
    
    async def _release_monitor_lock(self):
        """释放监控锁（只释放自己持有的锁）"""
        try:
            # 使用Lua脚本确保只释放自己持有的锁
            lua_script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            else
                return 0
            end
            """
            await self.redis_client.eval(
                lua_script,
                1,
                self.backlog_monitor_lock_key.encode(),
                self.node_id.encode()
            )
        except Exception as e:
            logger.error(f"Error releasing monitor lock: {e}")
    
    async def _collect_stream_backlog_metrics(self):
        """采集Stream积压指标并保存到数据库（使用offset方式）"""
        try:
            # 获取所有队列的最新offset (QUEUE_OFFSETS)
            queue_offsets_key = f"{self.namespace_name}:QUEUE_OFFSETS"
            queue_offsets = {}
            try:
                # 使用decode_responses=False的客户端，手动解码
                raw_queue_offsets = await self.redis_client.hgetall(queue_offsets_key.encode())
                for k, v in raw_queue_offsets.items():
                    queue_name = k.decode() if isinstance(k, bytes) else k
                    offset_value = v.decode() if isinstance(v, bytes) else v
                    queue_offsets[queue_name] = int(offset_value)
            except Exception as e:
                logger.debug(f"No QUEUE_OFFSETS found for {queue_offsets_key}: {e}")
            
            # 获取所有任务组的消费offset (TASK_OFFSETS)
            task_offsets_key = f"{self.namespace_name}:TASK_OFFSETS"
            task_offsets = {}
            try:
                raw_task_offsets = await self.redis_client.hgetall(task_offsets_key.encode())
                for k, v in raw_task_offsets.items():
                    task_key = k.decode() if isinstance(k, bytes) else k
                    offset_value = v.decode() if isinstance(v, bytes) else v
                    task_offsets[task_key] = int(offset_value)
            except Exception as e:
                logger.debug(f"No TASK_OFFSETS found for {task_offsets_key}: {e}")
            
            # 使用SCAN命令扫描所有队列Stream（包括普通队列和优先级队列）
            stream_info_map = {}  # {queue_name: [(stream_key, priority), ...]}
            pattern = f"{self.prefix}:QUEUE:*".encode()
            cursor = 0
            
            # 使用SCAN命令，增大count参数以提高效率
            while True:
                cursor, keys = await self.redis_client.scan(cursor, match=pattern, count=10000)
                
                for key in keys:
                    key_str = key.decode()
                    # 移除前缀 "prefix:QUEUE:"
                    queue_part = key_str.replace(f"{self.prefix}:QUEUE:", "")
                    
                    # 检查是否是优先级队列（格式：queue_name:priority）
                    parts = queue_part.split(':')
                    if len(parts) == 2 and parts[1].isdigit():
                        # 优先级队列
                        queue_name = parts[0]
                        priority = int(parts[1])
                        if queue_name not in stream_info_map:
                            stream_info_map[queue_name] = []
                        stream_info_map[queue_name].append((key, priority))
                    elif ':' not in queue_part:
                        # 普通队列（不包含冒号）
                        queue_name = queue_part
                        if queue_name not in stream_info_map:
                            stream_info_map[queue_name] = []
                        stream_info_map[queue_name].append((key, 0))  # 普通队列优先级为0
                    # 忽略其他格式的键（如消费组等）
                
                if cursor == 0:
                    break
            
            if not stream_info_map:
                logger.debug("No streams found for backlog monitoring")
                return
            
            # 调试日志（使用debug级别避免刷屏）
            logger.debug(f"Found {len(stream_info_map)} queues for backlog monitoring")
            for queue_name, stream_list in stream_info_map.items():
                priorities = [p for _, p in stream_list]
                # 筛选出非0优先级（0表示普通队列）
                high_priorities = [p for p in priorities if p > 0]
                if high_priorities:
                    logger.debug(f"  - {queue_name}: {len(stream_list)} streams (includes priorities: {sorted(set(priorities))})")
                else:
                    logger.debug(f"  - {queue_name}: regular queue only (priority=0)")
            
            # 收集每个队列的指标（聚合所有优先级）
            metrics = []
            current_time = datetime.now(timezone.utc)
            
            for queue_name, stream_list in stream_info_map.items():
                # 分别处理每个优先级队列
                for stream_key, priority in stream_list:
                    try:
                        # 获取该队列的最新offset（考虑优先级队列）
                        if priority > 0:
                            # 优先级队列的key格式: queue_name:priority
                            queue_key = f"{queue_name}:{priority}"
                        else:
                            queue_key = queue_name
                        last_published_offset = queue_offsets.get(queue_key, 0)
                        
                        # 获取Stream信息
                        stream_info = await self.redis_client.xinfo_stream(stream_key)
                        stream_length = stream_info.get(b'length', 0)
                        
                        # 获取消费组信息
                        has_consumer_groups = False
                        try:
                            groups = await self.redis_client.xinfo_groups(stream_key)
                            
                            for group in groups:
                                # 处理group_name
                                raw_name = group.get('name', b'')
                                if isinstance(raw_name, bytes):
                                    group_name = raw_name.decode() if raw_name else ''
                                else:
                                    group_name = str(raw_name) if raw_name else ''
                                
                                if not group_name:
                                    group_name = 'unknown'
                                
                                # 过滤内部消费者组
                                if is_internal_consumer(group_name):
                                    # logger.info(f"Skipping internal consumer group: {group_name}")
                                    continue
                                
                                # 处理pending - 直接是int
                                pending_count = group.get('pending', 0)
                                
                                # 从TASK_OFFSETS获取该组的消费offset
                                # key格式: f"{queue_name}:{group_name}" (不包含优先级)
                                task_offset_key = f"{queue_name}:{group_name}"
                                last_acked_offset = task_offsets.get(task_offset_key, 0)
                                
                                # 计算各种积压指标
                                # 1. 总积压 = 队列最新offset - 消费组已确认的offset
                                total_backlog = max(0, last_published_offset - last_acked_offset)
                                
                                # 2. 未投递的积压 = 总积压 - pending数量
                                backlog_undelivered = max(0, total_backlog - pending_count)
                                
                                # 3. 已投递未确认 = pending数量
                                backlog_delivered_unacked = pending_count
                                
                                # 4. 已投递的offset = 已确认offset + pending数量
                                last_delivered_offset = last_acked_offset + pending_count
                                
                                # 为每个消费组创建一条记录
                                metrics.append({
                                    'namespace': self.namespace_name,
                                    'stream_name': queue_name,
                                    'priority': priority,  # 添加优先级字段
                                    'consumer_group': group_name,
                                    'last_published_offset': last_published_offset,
                                    'last_delivered_offset': last_delivered_offset,
                                    'last_acked_offset': last_acked_offset,
                                    'pending_count': pending_count,
                                    'backlog_undelivered': backlog_undelivered,
                                    'backlog_unprocessed': total_backlog,
                                    'created_at': current_time
                                })
                                has_consumer_groups = True
                                
                        except Exception as e:
                            # 这个队列没有消费组
                            logger.debug(f"No consumer groups for stream {stream_key.decode()}: {e}")
                        
                        # 如果没有消费组，保存Stream级别的指标
                        if not has_consumer_groups and last_published_offset > 0:
                            metrics.append({
                                'namespace': self.namespace_name,
                                'stream_name': queue_name,
                                'priority': priority,  # 添加优先级字段
                                'consumer_group': None,
                                'last_published_offset': last_published_offset,
                                'last_delivered_offset': 0,
                                'last_acked_offset': 0,
                                'pending_count': 0,
                                'backlog_undelivered': last_published_offset,
                                'backlog_unprocessed': last_published_offset,
                                'created_at': current_time
                            })
                            
                    except Exception as e:
                        logger.error(f"Error collecting metrics for stream {stream_key.decode()}: {e}")
                        continue
            
            # 保存指标到数据库
            if metrics:
                await self._save_backlog_metrics(metrics)
                # logger.info(f"Collected backlog metrics for {len(metrics)} stream/group combinations {time.time() }")
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            logger.error(f"Error collecting stream backlog metrics: {e}")
    
    async def _save_backlog_metrics(self, metrics: List[Dict]):
        """保存积压指标到数据库（仅保存发生变化的数据）"""
        if not metrics:
            return
            
        # logger.info(f"Processing {len(metrics)} metrics for deduplication")
        
        try:
            async with self.AsyncSessionLocal() as session:
                # 要保存的新记录
                metrics_to_save = []
                
                # 使用批量查询优化性能
                metric_keys = {}  # 用于快速查找
                
                for metric in metrics:
                    # 构建唯一键：namespace + stream_name + consumer_group + priority
                    unique_key = f"{metric['namespace']}:{metric['stream_name']}:{metric['consumer_group']}:{metric['priority']}"
                    metric_keys[unique_key] = metric
                
                # logger.info(f"Checking {len(metric_keys)} unique metric combinations")
                
                # 批量查询最新记录 - 分批查询以避免SQL过长
                last_records = {}
                metric_list = list(metric_keys.values())
                batch_size = 50  # 每批查询50个
                
                for i in range(0, len(metric_list), batch_size):
                    batch = metric_list[i:i + batch_size]
                    
                    # 构建参数化查询
                    conditions = []
                    params = {}
                    for idx, metric in enumerate(batch):
                        param_prefix = f"p{i + idx}"
                        conditions.append(f"""
                            (namespace = :{param_prefix}_ns 
                             AND stream_name = :{param_prefix}_sn
                             AND consumer_group = :{param_prefix}_cg
                             AND priority = :{param_prefix}_pr)
                        """)
                        params[f"{param_prefix}_ns"] = metric['namespace']
                        params[f"{param_prefix}_sn"] = metric['stream_name']
                        params[f"{param_prefix}_cg"] = metric['consumer_group']
                        params[f"{param_prefix}_pr"] = metric['priority']
                    
                    if conditions:
                        # 使用窗口函数获取每个组合的最新记录
                        query_sql = text(f"""
                            WITH latest_records AS (
                                SELECT 
                                    namespace,
                                    stream_name,
                                    consumer_group,
                                    priority,
                                    last_published_offset,
                                    last_delivered_offset,
                                    last_acked_offset,
                                    pending_count,
                                    backlog_undelivered,
                                    backlog_unprocessed,
                                    ROW_NUMBER() OVER (
                                        PARTITION BY namespace, stream_name, consumer_group, priority 
                                        ORDER BY created_at DESC
                                    ) as rn
                                FROM stream_backlog_monitor
                                WHERE ({' OR '.join(conditions)})
                            )
                            SELECT 
                                namespace,
                                stream_name,
                                consumer_group,
                                priority,
                                last_published_offset,
                                last_delivered_offset,
                                last_acked_offset,
                                pending_count,
                                backlog_undelivered,
                                backlog_unprocessed
                            FROM latest_records
                            WHERE rn = 1
                        """)
                        
                        result = await session.execute(query_sql, params)
                        for row in result:
                            key = f"{row.namespace}:{row.stream_name}:{row.consumer_group}:{row.priority}"
                            last_records[key] = row
                            logger.debug(f"Found last record for {key}: published={row.last_published_offset}")
                
                # 对每个指标进行去重检查
                for unique_key, metric in metric_keys.items():
                    should_save = False
                    
                    if unique_key not in last_records:
                        # 没有历史记录，需要保存
                        should_save = True
                        # logger.info(f"New metric for {unique_key}, will save")
                    else:
                        # 比较关键指标是否发生变化
                        last_record = last_records[unique_key]
                        
                        # 详细的调试日志
                        changes = []
                        logger.debug(f"Comparing for {unique_key}:")
                        logger.debug(f"  DB record: published={last_record.last_published_offset} (type={type(last_record.last_published_offset)}), "
                                   f"delivered={last_record.last_delivered_offset} (type={type(last_record.last_delivered_offset)}), "
                                   f"acked={last_record.last_acked_offset}, pending={last_record.pending_count}, "
                                   f"undelivered={last_record.backlog_undelivered}, unprocessed={last_record.backlog_unprocessed}")
                        logger.debug(f"  New metric: published={metric['last_published_offset']} (type={type(metric['last_published_offset'])}), "
                                   f"delivered={metric['last_delivered_offset']} (type={type(metric['last_delivered_offset'])}), "
                                   f"acked={metric['last_acked_offset']}, pending={metric['pending_count']}, "
                                   f"undelivered={metric['backlog_undelivered']}, unprocessed={metric['backlog_unprocessed']}")
                        
                        # 确保类型一致的比较（全部转为int进行比较）
                        db_published = int(last_record.last_published_offset) if last_record.last_published_offset is not None else 0
                        new_published = int(metric['last_published_offset']) if metric['last_published_offset'] is not None else 0
                        
                        db_delivered = int(last_record.last_delivered_offset) if last_record.last_delivered_offset is not None else 0
                        new_delivered = int(metric['last_delivered_offset']) if metric['last_delivered_offset'] is not None else 0
                        
                        db_acked = int(last_record.last_acked_offset) if last_record.last_acked_offset is not None else 0
                        new_acked = int(metric['last_acked_offset']) if metric['last_acked_offset'] is not None else 0
                        
                        db_pending = int(last_record.pending_count) if last_record.pending_count is not None else 0
                        new_pending = int(metric['pending_count']) if metric['pending_count'] is not None else 0
                        
                        db_undelivered = int(last_record.backlog_undelivered) if last_record.backlog_undelivered is not None else 0
                        new_undelivered = int(metric['backlog_undelivered']) if metric['backlog_undelivered'] is not None else 0
                        
                        db_unprocessed = int(last_record.backlog_unprocessed) if last_record.backlog_unprocessed is not None else 0
                        new_unprocessed = int(metric['backlog_unprocessed']) if metric['backlog_unprocessed'] is not None else 0
                        
                        if db_published != new_published:
                            changes.append(f"published: {db_published} -> {new_published}")
                        if db_delivered != new_delivered:
                            changes.append(f"delivered: {db_delivered} -> {new_delivered}")
                        if db_acked != new_acked:
                            changes.append(f"acked: {db_acked} -> {new_acked}")
                        if db_pending != new_pending:
                            changes.append(f"pending: {db_pending} -> {new_pending}")
                        if db_undelivered != new_undelivered:
                            changes.append(f"undelivered: {db_undelivered} -> {new_undelivered}")
                        if db_unprocessed != new_unprocessed:
                            changes.append(f"unprocessed: {db_unprocessed} -> {new_unprocessed}")
                        
                        if changes:
                            should_save = True
                            # logger.info(f"Metric changed for {unique_key}: {', '.join(changes)}")
                        else:
                            logger.debug(f"Metric unchanged for {unique_key}, skipping")
                    
                    if should_save:
                        metrics_to_save.append(metric)
                
                # 批量插入发生变化的监控数据
                if metrics_to_save:
                    insert_sql = text("""
                        INSERT INTO stream_backlog_monitor 
                        (namespace, stream_name, priority, consumer_group, last_published_offset, 
                         last_delivered_offset, last_acked_offset, pending_count,
                         backlog_undelivered, backlog_unprocessed, created_at)
                        VALUES 
                        (:namespace, :stream_name, :priority, :consumer_group, :last_published_offset,
                         :last_delivered_offset, :last_acked_offset, :pending_count,
                         :backlog_undelivered, :backlog_unprocessed, :created_at)
                    """)
                    
                    # 逐条插入（SQLAlchemy的execute不支持批量插入参数列表）
                    for metric_data in metrics_to_save:
                        await session.execute(insert_sql, metric_data)
                    
                    await session.commit()
                    # logger.info(f"Saved {len(metrics_to_save)} changed metrics out of {len(metrics)} total")
                else:
                    logger.debug(f"No metrics changed, skipped saving all {len(metrics)} records")
                
        except Exception as e:
            logger.error(f"Error saving backlog metrics to database: {e}")
    
    def _parse_stream_message(self, task_id: str, data: dict) -> Optional[dict]:
        """解析Stream消息为任务信息（返回完整的字段）"""
        try:
            from jettask.utils.serializer import loads_str
            if b'data' in data:
                task_data = loads_str(data[b'data'])
            else:
                task_data = {}
                for k, v in data.items():
                    key = k.decode('utf-8') if isinstance(k, bytes) else k
                    if isinstance(v, bytes):
                        try:
                            value = loads_str(v)
                        except:
                            value = str(v)
                    else:
                        value = v
                    task_data[key] = value
            # 如果配置了命名空间，检查消息是否属于该命名空间
            # if self.namespace_id:
            #     msg_namespace_id = task_data.get('__namespace_id')
            #     # 如果消息没有namespace_id且当前不是默认命名空间，跳过
            #     if msg_namespace_id != self.namespace_id:
            #         if not (msg_namespace_id is None and self.namespace_id == 'default'):
            #             logger.debug(f"Skipping message from different namespace: {msg_namespace_id} != {self.namespace_id}")
            #             return None
            queue_name = task_data['queue']
            task_name = task_data.get('name', task_data.get('task', 'unknown'))
            created_at = None
            if 'trigger_time' in task_data:
                try:
                    timestamp = float(task_data['trigger_time'])
                    created_at = datetime.fromtimestamp(timestamp, tz=timezone.utc)
                except:
                    pass
            # 返回完整的字段，包括所有可能为None的字段
            return {
                'id': task_id,
                'queue_name': queue_name,
                'task_name': task_name,
                'task_data': json.dumps(task_data),
                'priority': int(task_data.get('priority', 0)),
                'retry_count': int(task_data.get('retry', 0)),
                'max_retry': int(task_data.get('max_retry', 3)),
                'status': 'pending',
                'result': None,  # 新任务没有结果
                'error_message': None,  # 新任务没有错误信息
                'created_at': created_at,
                'started_at': None,  # 新任务还未开始
                'completed_at': None,  # 新任务还未完成
                'scheduled_task_id': task_data.get('scheduled_task_id'),  # 调度任务ID
                'metadata': json.dumps(task_data.get('metadata', {})),
                'worker_id': None,  # 新任务还未分配worker
                'execution_time': None,  # 新任务还没有执行时间
                'duration': None,  # 新任务还没有持续时间
                'namespace_id': self.namespace_id  # 添加命名空间ID
            }
        except Exception as e:
            import traceback 
            traceback.print_exc()
            logger.error(f"Error parsing stream message for task {task_id}: {e}")
            return None
    


async def run_pg_consumer(pg_config: PostgreSQLConfig, redis_config: RedisConfig, 
                         consumer_strategy: ConsumerStrategy = ConsumerStrategy.HEARTBEAT):
    """运行PostgreSQL消费者"""
    # 从环境变量读取监控配置
    enable_backlog_monitor = os.getenv('JETTASK_ENABLE_BACKLOG_MONITOR', 'true').lower() == 'true'
    backlog_monitor_interval = int(os.getenv('JETTASK_BACKLOG_MONITOR_INTERVAL', '60'))
    
    logger.info(f"Backlog monitor config: enabled={enable_backlog_monitor}, interval={backlog_monitor_interval}s")
    
    consumer = PostgreSQLConsumer(
        pg_config, 
        redis_config, 
        consumer_strategy=consumer_strategy,
        enable_backlog_monitor=enable_backlog_monitor,
        backlog_monitor_interval=backlog_monitor_interval
    )
    
    try:
        await consumer.start()
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.debug("Received interrupt signal")
    finally:
        await consumer.stop()


def main():
    """主入口函数"""
    from dotenv import load_dotenv
    
    load_dotenv()
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    pg_config = PostgreSQLConfig(
        host=os.getenv('JETTASK_PG_HOST', 'localhost'),
        port=int(os.getenv('JETTASK_PG_PORT', '5432')),
        database=os.getenv('JETTASK_PG_DB', 'jettask'),
        user=os.getenv('JETTASK_PG_USER', 'jettask'),
        password=os.getenv('JETTASK_PG_PASSWORD', '123456'),
    )
    
    redis_config = RedisConfig(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', '6379')),
        db=int(os.getenv('REDIS_DB', '0')),
        password=os.getenv('REDIS_PASSWORD'),
    )
    
    # 从环境变量获取消费者策略，默认使用 HEARTBEAT
    strategy_name = os.getenv('JETTASK_CONSUMER_STRATEGY', 'HEARTBEAT').upper()
    consumer_strategy = ConsumerStrategy.HEARTBEAT  # 默认
    
    if strategy_name == 'FIXED':
        consumer_strategy = ConsumerStrategy.FIXED
    elif strategy_name == 'POD':
        consumer_strategy = ConsumerStrategy.POD
    elif strategy_name == 'HEARTBEAT':
        consumer_strategy = ConsumerStrategy.HEARTBEAT
    else:
        logger.debug(f"Unknown consumer strategy: {strategy_name}, using HEARTBEAT")
    
    logger.debug(f"Using consumer strategy: {consumer_strategy.value}")
    
    asyncio.run(run_pg_consumer(pg_config, redis_config, consumer_strategy))


if __name__ == '__main__':
    main()