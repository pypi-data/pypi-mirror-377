"""
简化的离线worker消息恢复模块
"""
import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from redis.asyncio.lock import Lock as AsyncLock

import msgpack

logger = logging.getLogger(__name__)


class OfflineWorkerRecovery:
    """离线worker消息恢复处理器"""
    
    def __init__(self, async_redis_client, consumer_manager=None, redis_prefix='jettask', worker_prefix='WORKER', queue_formatter=None):
        self.async_redis_client = async_redis_client
        self.consumer_manager = consumer_manager
        self.redis_prefix = redis_prefix
        self.worker_prefix = worker_prefix
        self._stop_recovery = False
        # 队列格式化函数，默认使用 prefix:QUEUE:queue_name 格式
        self.queue_formatter = queue_formatter or (lambda q: f"{self.redis_prefix}:QUEUE:{q}")
        
    async def recover_offline_workers(self,
                                     queue: str,
                                     current_consumer_name: str = None,
                                     event_queue: Optional[asyncio.Queue] = None,
                                     process_message_callback: Optional[callable] = None,
                                     consumer_group_suffix: Optional[str] = None) -> int:
        """
        恢复指定队列的离线worker的pending消息
        """
        total_recovered = 0
        logger.debug(f'恢复指定队列的离线worker的pending消息')
        try:
            # 获取当前consumer名称
            if not current_consumer_name and self.consumer_manager:
                # 对于优先级队列，使用基础队列名来获取consumer
                base_queue = queue
                if ':' in queue and queue.rsplit(':', 1)[-1].isdigit():
                    base_queue = queue.rsplit(':', 1)[0]
                
                current_consumer_name = self.consumer_manager.get_consumer_name(base_queue)
                
                # 对于优先级队列，consumer名称需要添加队列后缀
                if current_consumer_name and base_queue != queue:
                    priority_suffix = queue.rsplit(':', 1)[-1]
                    current_consumer_name = f"{current_consumer_name}:{priority_suffix}"
            
            if not current_consumer_name:
                logger.error(f"Cannot get current consumer name for queue {queue}")
                return 0
                
            logger.debug(f"Starting recovery for queue {queue} with consumer {current_consumer_name}")
            
            # 获取所有离线worker
            offline_workers = await self._find_offline_workers(queue)
            if not offline_workers:
                logger.debug(f"No offline workers found for queue {queue}")
                return 0
                
            logger.debug(f"Found {len(offline_workers)} offline workers for queue {queue}")
            
            # 处理每个离线worker
            for worker_key, worker_data in offline_workers:
                if self._stop_recovery:
                    logger.debug("Stopping recovery due to shutdown signal")
                    break
                
                # logger.debug(f'恢复指定队列的离线worker的pending消息 {offline_workers=}')
                # logger.info(f"Processing offline worker: {worker_key} {worker_data=} {queue=}")
                recovered = await self._recover_worker_messages(
                    queue=queue,
                    worker_key=worker_key,
                    worker_data=worker_data,
                    current_consumer_name=current_consumer_name,
                    event_queue=event_queue,
                    process_message_callback=process_message_callback,
                    consumer_group_suffix=consumer_group_suffix
                )
                
                total_recovered += recovered
                
        except Exception as e:
            logger.error(f"Error recovering offline workers for queue {queue}: {e}")
            
        return total_recovered
        
    async def _find_offline_workers(self, queue: str) -> List[Tuple[str, Dict]]:
        """查找指定队列的离线worker"""
        offline_workers = []
        
        try:
            # 扫描所有worker
            pattern = f"{self.redis_prefix}:{self.worker_prefix}:*"
            cursor = 0
            while True:
                cursor, keys = await self.async_redis_client.scan(
                    cursor=cursor,
                    match=pattern,
                    count=100
                )
                
                for worker_key in keys:
                    if isinstance(worker_key, bytes):
                        worker_key = worker_key.decode('utf-8')
                    
                    # 跳过非worker键
                    if any(x in worker_key for x in [':HISTORY:', ':REUSE:LOCK', ':REUSING']):
                        continue
                    
                    try:
                        worker_data = await self.async_redis_client.hgetall(worker_key)
                        if not worker_data:
                            continue
                        
                        # 解码二进制数据
                        decoded_worker_data = {}
                        for k, v in worker_data.items():
                            key = k.decode('utf-8') if isinstance(k, bytes) else k
                            value = v.decode('utf-8') if isinstance(v, bytes) else v
                            decoded_worker_data[key] = value
                        
                        # logger.debug(f'{worker_key=} {decoded_worker_data=}')
                        # logger.debug(f'{decoded_worker_data=}')
                        # 检查worker是否离线且消息未转移
                        is_alive = decoded_worker_data.get('is_alive', 'false').lower() == 'true'
                        messages_transferred = decoded_worker_data.get('messages_transferred', 'false').lower() == 'true'
                        # logger.debug(f'{worker_key=} {is_alive=} {messages_transferred=} {not is_alive and not messages_transferred}')
                        # 找到离线且消息未转移的worker
                        if not is_alive and not messages_transferred:
                            queues_str = decoded_worker_data.get('queues', '')
                            worker_queues = queues_str.split(',') if queues_str else []
                            
                            # logger.debug(f'{worker_queues=} {queue=}')
                            # 检查这个worker是否负责当前队列
                            # 支持优先级队列：如果queue是"base:priority"格式，检查worker是否负责base队列
                            queue_matched = False
                            if ':' in queue and queue.rsplit(':', 1)[-1].isdigit():
                                # 这是优先级队列，提取基础队列名
                                base_queue = queue.rsplit(':', 1)[0]
                                queue_matched = base_queue in worker_queues
                            else:
                                # 普通队列
                                queue_matched = queue in worker_queues
                            if queue_matched:
                                offline_workers.append((worker_key, decoded_worker_data))
                                
                    except Exception as e:
                        logger.error(f"Error processing worker key {worker_key}: {e}")
                        continue
                
                # 当cursor返回0时，表示扫描完成
                if cursor == 0:
                    break
                    
        except Exception as e:
            logger.error(f"Error finding offline workers: {e}")
            
        return offline_workers
        
    async def _recover_worker_messages(self,
                                      queue: str,
                                      worker_key: str,
                                      worker_data: Dict,
                                      current_consumer_name: str,
                                      event_queue: Optional[asyncio.Queue] = None,
                                      process_message_callback: Optional[callable] = None,
                                      consumer_group_suffix: Optional[str] = None) -> int:
        """
        恢复单个worker的pending消息
        
        从worker_data中获取所有的group_info字段，恢复对应的pending消息
        """
        total_claimed = 0
        
        try:
            # worker_data 现在已经是解码后的字典
            consumer_id = worker_data.get('consumer_id')
            
            # 从worker_data中提取group_info字段
            group_infos = []
            import json
            for key, value in worker_data.items():
                if key.startswith('group_info:'):
                    try:
                        group_info = json.loads(value)
                        # 只处理属于当前队列的group
                        if group_info.get('queue') == queue:
                            group_infos.append(group_info)
                            logger.info(f"Found group info for queue {queue}: {group_info}")
                    except Exception as e:
                        logger.error(f"Error parsing group_info: {e}")
            
            if not group_infos:
                logger.debug(f"No group_info found for queue {queue} in worker {worker_key}")
                # 即使没有group_info，也要标记为已处理，避免重复扫描
                await self.async_redis_client.hset(worker_key, 'messages_transferred', 'true')
                return 0
            
            # 在处理任何group之前，先标记该worker的消息已开始转移
            # 避免其他进程重复处理
            await self.async_redis_client.hset(worker_key, 'messages_transferred', 'true')
            logger.info(f"Marked worker {worker_key} as messages_transferred=true")
            
            # 处理每个group_info
            for group_info in group_infos:
                    stream_key = group_info.get('stream_key')
                    group_name = group_info.get('group_name')
                    offline_consumer_name = group_info.get('consumer_name')
                    task_name = group_info.get('task_name')
                    
                    if not all([stream_key, group_name, offline_consumer_name]):
                        logger.warning(f"Incomplete group_info: {group_info}")
                        continue
                    
                    logger.info(f"Recovering task {task_name}: stream={stream_key}, group={group_name}, consumer={offline_consumer_name}")
                    
                    # 跳过自己的consumer
                    if current_consumer_name == offline_consumer_name:
                        logger.debug(f"Skipping own consumer: {offline_consumer_name}")
                        continue
                    
                    # 使用分布式锁
                    lock_key = f"{self.redis_prefix}:CLAIM:LOCK:{offline_consumer_name}:{group_name}"
                    lock = AsyncLock(
                        self.async_redis_client,
                        lock_key,
                        timeout=30,
                        blocking=False
                    )
                    
                    if not await lock.acquire():
                        logger.debug(f"Lock busy for {offline_consumer_name}:{group_name}")
                        continue
                    
                    try:
                        # 获取pending消息数量
                        pending_info = await self.async_redis_client.xpending(
                            stream_key, group_name
                        )
                        
                        if pending_info and pending_info.get('pending', 0) > 0:
                            # 获取具体的pending消息信息
                            detailed_pending = await self.async_redis_client.xpending_range(
                                stream_key, group_name,
                                min='-', max='+', count=100,
                                consumername=offline_consumer_name
                            )
                            
                            if detailed_pending:
                                logger.info(f"Found {len(detailed_pending)} pending messages for {task_name}")
                                
                                # 批量认领消息
                                message_ids = [msg['message_id'] for msg in detailed_pending]
                                claimed_messages = await self.async_redis_client.xclaim(
                                    stream_key, group_name,
                                    current_consumer_name,
                                    min_idle_time=0,
                                    message_ids=message_ids
                                )
                                
                                if claimed_messages:
                                    logger.info(f"Claimed {len(claimed_messages)} messages for task {task_name}")
                                    total_claimed += len(claimed_messages)
                                    
                                    # 如果提供了event_queue，将消息放入队列
                                    if event_queue:
                                        for msg_id, msg_data in claimed_messages:
                                            if isinstance(msg_id, bytes):
                                                msg_id = msg_id.decode('utf-8')
                                            
                                            # 解析消息数据
                                            data_field = msg_data.get(b'data') or msg_data.get('data')
                                            if data_field:
                                                try:
                                                    import msgpack
                                                    parsed_data = msgpack.unpackb(data_field, raw=False)
                                                    # 添加必要的元数据
                                                    parsed_data['_task_name'] = task_name
                                                    parsed_data['queue'] = queue
                                                    
                                                    # 构建任务项
                                                    task_item = {
                                                        'queue': queue,
                                                        'event_id': msg_id,
                                                        'event_data': parsed_data,
                                                        'consumer': current_consumer_name,
                                                        'group_name': group_name
                                                    }
                                                    
                                                    await event_queue.put(task_item)
                                                except Exception as e:
                                                    logger.error(f"Error processing claimed message: {e}")
                    finally:
                        await lock.release()
            
        except Exception as e:
            logger.error(f"Error recovering messages: {e}")
            
        return total_claimed
        
    async def _get_consumer_groups(self, stream_key: str, suffix: Optional[str] = None) -> List[str]:
        """获取Stream的consumer groups"""
        groups = []
        try:
            # 确保stream_key是字符串类型（如果是bytes会出问题）
            if isinstance(stream_key, bytes):
                stream_key = stream_key.decode('utf-8')
            
            all_groups = await self.async_redis_client.xinfo_groups(stream_key)
            logger.debug(f"Raw groups info for {stream_key}: {all_groups}")
            
            for group_info in all_groups:
                # 二进制Redis客户端返回的字典键是字符串，值是bytes
                group_name = group_info.get('name', b'')
                logger.debug(f"Processing group: {group_info}, group_name type: {type(group_name)}")
                
                # 解码group名称
                if isinstance(group_name, bytes):
                    group_name = group_name.decode('utf-8')
                
                # 过滤空的group名称
                if group_name:
                    if suffix:
                        if group_name.endswith(suffix):
                            groups.append(group_name)
                    else:
                        groups.append(group_name)
                        logger.debug(f"Added group: {group_name}")
        except Exception as e:
            logger.error(f"Error getting consumer groups for {stream_key}: {e}")
        return groups
        
    async def _claim_messages(self, stream_key: str, group_name: str, 
                             old_consumer: str, new_consumer: str) -> List[Tuple[bytes, Dict]]:
        """转移pending消息"""
        all_claimed = []
        last_id = '-'
        
        try:
            # 确保参数是bytes类型
            if isinstance(stream_key, str):
                stream_key = stream_key.encode('utf-8')
            if isinstance(group_name, str):
                group_name = group_name.encode('utf-8')
            
            logger.debug(f"_claim_messages: stream_key={stream_key}, group_name={group_name}, old_consumer={old_consumer}, new_consumer={new_consumer}")
                
            while True:
                # 获取pending消息
                pending_batch = await self.async_redis_client.xpending_range(
                    stream_key, group_name,
                    min=last_id, max='+',
                    count=100
                )
                
                logger.debug(f"Got {len(pending_batch) if pending_batch else 0} pending messages")
                
                if not pending_batch:
                    break
                
                # 过滤出属于旧consumer的消息
                message_ids = []
                for msg in pending_batch:
                    msg_consumer = msg.get('consumer') or msg.get(b'consumer')
                    if isinstance(msg_consumer, bytes):
                        msg_consumer = msg_consumer.decode('utf-8')
                    
                    if msg_consumer == old_consumer:
                        msg_id = msg.get('message_id') or msg.get(b'message_id')
                        message_ids.append(msg_id)
                
                if message_ids:
                    # 使用XCLAIM转移消息
                    logger.debug(f"Claiming {len(message_ids)} messages from {old_consumer} to {new_consumer}")
                    
                    claimed = await self.async_redis_client.xclaim(
                        stream_key, group_name,
                        new_consumer,
                        min_idle_time=0,
                        message_ids=message_ids,
                        force=True
                    )
                    
                    if claimed:
                        all_claimed.extend(claimed)
                
                # 更新游标
                if pending_batch:
                    last_msg_id = pending_batch[-1].get('message_id') or pending_batch[-1].get(b'message_id')
                    if isinstance(last_msg_id, bytes):
                        last_msg_id = last_msg_id.decode('utf-8')
                    # 增加ID以获取下一批
                    parts = last_msg_id.split('-')
                    if len(parts) == 2:
                        last_id = f"{parts[0]}-{int(parts[1]) + 1}"
                    else:
                        break
                else:
                    break
                    
        except Exception as e:
            logger.error(f"Error claiming messages: {e}")
            
        return all_claimed
        
    async def _put_to_event_queue(self, msg_id, msg_data, queue, event_queue, 
                                 consumer, group_name, old_consumer):
        """将转移的消息放入event_queue"""
        try:
            # 解析消息数据
            if b'data' in msg_data:
                event_data = msgpack.unpackb(msg_data[b'data'], raw=False)
            else:
                event_data = msg_data
            
            # 从 group_name 中提取 task_name
            # group_name 的格式是: "jettask:QUEUE:{queue}:{task_name}"
            task_name = None
            if group_name and ':' in group_name:
                parts = group_name.split(':')
                # 查找最后一个非数字部分作为task_name
                for i in range(len(parts) - 1, -1, -1):
                    part = parts[i]
                    # 跳过优先级数字
                    if not part.isdigit() and part not in ['jettask', 'QUEUE', queue]:
                        task_name = part
                        logger.debug(f"Extracted task_name '{task_name}' from group_name '{group_name}'")
                        break
            
            # 如果从group_name提取失败，尝试从consumer名称提取
            if not task_name and ':' in consumer and ':' in group_name:
                # consumer格式可能是: "{consumer_id}:{task_name}" 
                consumer_parts = consumer.split(':')
                if len(consumer_parts) > 1:
                    potential_task = consumer_parts[-1]
                    # 确保不是优先级数字
                    if not potential_task.isdigit():
                        task_name = potential_task
                        logger.debug(f"Extracted task_name '{task_name}' from consumer '{consumer}'")
            
            # 如果还是没有task_name，检查event_data中是否已有
            if not task_name and '_task_name' in event_data:
                task_name = event_data['_task_name']
                logger.debug(f"Using existing _task_name from event_data: '{task_name}'")
            
            # 确保event_data中有_task_name字段
            if task_name:
                event_data['_task_name'] = task_name
                logger.debug(f"Added _task_name '{task_name}' to recovered message")
            else:
                # 如果无法确定task_name，记录警告
                logger.warning(f"Could not determine task_name for recovered message. group_name='{group_name}', consumer='{consumer}'")
            
            # 构建事件
            event = {
                'event_id': msg_id.decode() if isinstance(msg_id, bytes) else msg_id,
                'event_data': event_data,
                'queue': queue,
                'consumer': consumer,
                'group_name': group_name,
                '_recovery': True,
                '_claimed_from': old_consumer
            }
            
            await event_queue.put(event)
            
        except Exception as e:
            logger.error(f"Error putting message to event queue: {e}")
            
    def stop(self):
        """停止恢复处理"""
        self._stop_recovery = True