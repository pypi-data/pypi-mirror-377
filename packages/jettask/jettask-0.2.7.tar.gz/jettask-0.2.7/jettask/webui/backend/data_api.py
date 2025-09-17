"""
数据查询API路由
所有接口都需要指定namespace参数
"""
from fastapi import APIRouter, HTTPException, Query, Request
from typing import List, Dict, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
import logging
import time
import traceback
from sqlalchemy import text

from namespace_data_access import get_namespace_data_access

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/data", tags=["data"])

# 获取全局数据访问实例
data_access = get_namespace_data_access()


async def handle_database_connection_error(e: Exception, namespace: str, operation_name: str):
    """
    处理数据库连接异常，重置连接并抛出适当的HTTP异常
    
    Args:
        e: 原始异常
        namespace: 命名空间名称
        operation_name: 操作名称（用于错误消息）
    """
    error_msg = str(e)
    
    # 检查是否为连接相关的错误
    is_connection_error = (
        "password authentication failed" in error_msg or 
        "connection failed" in error_msg or
        "could not connect to server" in error_msg
    )
    
    if is_connection_error:
        # 重置连接以便重新初始化
        try:
            await data_access.reset_connection(namespace)
            logger.info(f"已重置命名空间 {namespace} 的数据库连接")
        except Exception as reset_error:
            logger.error(f"重置命名空间 {namespace} 连接失败: {reset_error}")
        
        if "password authentication failed" in error_msg or "connection failed" in error_msg:
            raise HTTPException(
                status_code=500, 
                detail=f"命名空间 '{namespace}' 的数据库连接失败，请检查该命名空间的数据库配置"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"命名空间 '{namespace}' 的数据库服务不可用，请检查数据库是否正常运行"
            )
    else:
        # 其他类型的错误
        raise HTTPException(status_code=500, detail=f"{operation_name}失败: {error_msg}")


def build_queue_filter_and_params(queues: Optional[str] = None):
    """
    构建队列筛选条件和参数
    
    Args:
        queues: 逗号分隔的队列名称列表
        
    Returns:
        tuple: (queue_filter_sql, queue_list, queue_params_dict)
    """
    queue_list = []
    if queues:
        queue_list = [q.strip() for q in queues.split(',') if q.strip()]
    
    queue_filter = ""
    queue_params = {}
    
    if queue_list:
        queue_placeholders = ','.join([f':queue_{i}' for i in range(len(queue_list))])
        queue_filter = f"AND t.queue IN ({queue_placeholders})"
        
        # 添加队列参数
        for i, queue in enumerate(queue_list):
            queue_params[f'queue_{i}'] = queue
    
    return queue_filter, queue_list, queue_params


class TimeRangeQuery(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    time_range: Optional[str] = "15m"
    queues: Optional[List[str]] = None
    filters: Optional[List[Dict]] = None


class TimeRangeResult:
    """时间范围处理结果"""
    def __init__(self, start_time: datetime, end_time: datetime, interval: str, interval_seconds: int, granularity: str):
        self.start_time = start_time
        self.end_time = end_time
        self.interval = interval
        self.interval_seconds = interval_seconds
        self.granularity = granularity


def parse_time_range_query(query: TimeRangeQuery) -> TimeRangeResult:
    """
    解析TimeRangeQuery对象，返回时间范围和间隔信息
    
    Args:
        query: TimeRangeQuery对象
        
    Returns:
        TimeRangeResult对象，包含start_time, end_time, interval, interval_seconds, granularity
    """
    end_time = datetime.now(timezone.utc)
    
    if query.time_range and query.time_range != 'custom':
        # 解析时间范围字符串
        if query.time_range.endswith('m'):
            minutes = int(query.time_range[:-1])
            start_time = end_time - timedelta(minutes=minutes)
        elif query.time_range.endswith('h'):
            hours = int(query.time_range[:-1])
            start_time = end_time - timedelta(hours=hours)
        elif query.time_range.endswith('d'):
            days = int(query.time_range[:-1])
            start_time = end_time - timedelta(days=days)
        else:
            start_time = end_time - timedelta(minutes=15)
    else:
        # 使用自定义时间范围或默认值
        start_time = query.start_time or (end_time - timedelta(minutes=15))
        end_time = query.end_time or end_time
    
    # 动态计算时间间隔
    return calculate_dynamic_interval(start_time, end_time)


def parse_time_range_string(time_range: str) -> TimeRangeResult:
    """
    解析时间范围字符串，返回时间范围和间隔信息
    
    Args:
        time_range: 时间范围字符串，如'1h', '30m', '7d'
        
    Returns:
        TimeRangeResult对象，包含start_time, end_time, interval, interval_seconds, granularity
    """
    end_time = datetime.now(timezone.utc)
    
    if time_range.endswith('m'):
        minutes = int(time_range[:-1])
        start_time = end_time - timedelta(minutes=minutes)
    elif time_range.endswith('h'):
        hours = int(time_range[:-1])
        start_time = end_time - timedelta(hours=hours)
    elif time_range.endswith('d'):
        days = int(time_range[:-1])
        start_time = end_time - timedelta(days=days)
    else:
        start_time = end_time - timedelta(hours=1)
    
    # 动态计算时间间隔
    return calculate_dynamic_interval(start_time, end_time)


def calculate_dynamic_interval(start_time: datetime, end_time: datetime, target_points: int = 200) -> TimeRangeResult:
    """
    根据时间范围动态计算合适的时间间隔
    
    Args:
        start_time: 开始时间
        end_time: 结束时间
        target_points: 目标数据点数量，默认200
        
    Returns:
        TimeRangeResult对象，包含时间间隔信息
    """
    duration = (end_time - start_time).total_seconds()
    ideal_interval_seconds = duration / target_points
    
    # 选择合适的间隔
    if ideal_interval_seconds <= 1:
        interval_seconds = 1
        interval = '1 seconds'
        granularity = 'second'
    elif ideal_interval_seconds <= 5:
        interval_seconds = 5
        interval = '5 seconds'
        granularity = 'second'
    elif ideal_interval_seconds <= 10:
        interval_seconds = 10
        interval = '10 seconds'
        granularity = 'second'
    elif ideal_interval_seconds <= 30:
        interval_seconds = 30
        interval = '30 seconds'
        granularity = 'second'
    elif ideal_interval_seconds <= 60:
        interval_seconds = 60
        interval = '1 minute'
        granularity = 'minute'
    elif ideal_interval_seconds <= 120:
        interval_seconds = 120
        interval = '2 minutes'
        granularity = 'minute'
    elif ideal_interval_seconds <= 300:
        interval_seconds = 300
        interval = '5 minutes'
        granularity = 'minute'
    elif ideal_interval_seconds <= 600:
        interval_seconds = 600
        interval = '10 minutes'
        granularity = 'minute'
    elif ideal_interval_seconds <= 1800:
        interval_seconds = 1800
        interval = '30 minutes'
        granularity = 'minute'
    elif ideal_interval_seconds <= 3600:
        interval_seconds = 3600
        interval = '1 hour'
        granularity = 'hour'
    else:
        interval_seconds = 86400
        interval = '1 day'
        granularity = 'day'
    
    return TimeRangeResult(start_time, end_time, interval, interval_seconds, granularity)


class QueueStatsResponse(BaseModel):
    queue_name: str
    length: int
    consumer_groups: int
    consumers: int
    pending: int


class TaskDetailResponse(BaseModel):
    id: str
    status: str
    name: str
    queue: str
    worker_id: Optional[str]
    created_at: Optional[str]
    started_at: Optional[str]
    completed_at: Optional[str]
    result: Optional[str]
    error: Optional[str]
    retry_count: int


class ScheduledTaskResponse(BaseModel):
    id: int
    name: str
    queue: str
    schedule: str
    task_data: dict
    enabled: bool
    last_run_at: Optional[str]
    next_run_at: Optional[str]
    execution_count: int
    created_at: Optional[str]
    updated_at: Optional[str]
    description: Optional[str]
    max_retries: Optional[int]
    retry_delay: Optional[int]
    timeout: Optional[int]
    priority: Optional[int]


@router.get("/namespaces", response_model=List[dict])
async def list_available_namespaces():
    """获取所有可用的命名空间列表"""
    try:
        namespaces = await data_access.manager.list_namespaces()
        # 只返回基本信息
        return [
            {
                'id': ns.get('id'),
                'name': ns.get('name'),
                'description': ns.get('description', ''),
                'created_at': ns.get('created_at')
            }
            for ns in namespaces
        ]
    except Exception as e:
        logger.error(f"获取命名空间列表失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/queues/{namespace}", response_model=List[QueueStatsResponse])
async def get_queue_stats(namespace: str):
    """
    获取指定命名空间的队列统计信息
    
    Args:
        namespace: 命名空间名称
    """
    try:
        stats = await data_access.get_queue_stats(namespace)
        return stats
    except Exception as e:
        logger.error(f"获取队列统计失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/{namespace}/{task_id}", response_model=TaskDetailResponse)
async def get_task_detail(namespace: str, task_id: str):
    """
    获取指定命名空间中的任务详情
    
    Args:
        namespace: 命名空间名称
        task_id: 任务ID
    """
    try:
        task = await data_access.get_task_detail(namespace, task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取任务详情失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scheduled-tasks/{namespace}")
async def get_scheduled_tasks(
    namespace: str,
    limit: int = Query(100, description="返回记录数"),
    offset: int = Query(0, description="偏移量")
):
    """
    获取指定命名空间的定时任务列表
    
    Args:
        namespace: 命名空间名称
        limit: 返回记录数
        offset: 偏移量
    """
    try:
        result = await data_access.get_scheduled_tasks(namespace, limit, offset)
        return result
    except Exception as e:
        logger.error(f"获取定时任务列表失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/queue-history/{namespace}/{queue_name}")
async def get_queue_history(
    namespace: str,
    queue_name: str,
    hours: int = Query(24, description="历史时间范围（小时）"),
    interval: int = Query(1, description="时间间隔（小时）")
):
    """
    获取指定命名空间中队列的历史数据
    
    Args:
        namespace: 命名空间名称
        queue_name: 队列名称
        hours: 历史时间范围（小时）
        interval: 时间间隔（小时）
    """
    try:
        history = await data_access.get_queue_history(
            namespace, queue_name, hours, interval
        )
        return history
    except Exception as e:
        logger.error(f"获取队列历史数据失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/queue-timeline/{namespace}")
async def get_queue_timeline(namespace: str, query: TimeRangeQuery):
    """
    获取指定命名空间的队列时间线数据
    
    Args:
        namespace: 命名空间名称
        query: 时间范围查询参数
    """
    try:
        # 使用路径参数中的namespace（TimeRangeQuery没有namespace属性）
        
        conn = await data_access.manager.get_connection(namespace)
        
        # 使用公共工具函数处理时间范围
        time_range_result = parse_time_range_query(query)
        start_time = time_range_result.start_time
        end_time = time_range_result.end_time
        
        # 如果没有PostgreSQL配置，返回模拟数据
        if not conn.pg_config:
            # 生成模拟的时序数据
            timeline_data = []
            duration = (end_time - start_time).total_seconds()
            num_points = min(50, max(10, int(duration / 60)))  # 10-50个数据点
            
            for i in range(num_points):
                timestamp = start_time + timedelta(seconds=i * duration / num_points)
                for queue_name in (query.queues or ['default']):
                    timeline_data.append({
                        'time': timestamp.isoformat(),
                        'queue': queue_name,
                        'value': 100 + i * 2  # 模拟增长
                    })
            
            return {
                "data": timeline_data,
                "granularity": "1m"
            }
        
        # 从PostgreSQL查询时序数据
        async with await conn.get_pg_session() as session:
            try:
                # 动态计算时间间隔，目标是生成约200个时间点
                duration = (end_time - start_time).total_seconds()
                TARGET_POINTS = 200  # 目标数据点数
                ideal_interval_seconds = duration / TARGET_POINTS
                
                # 将间隔秒数规范化到合理的值
                if ideal_interval_seconds <= 1:
                    interval = '1 second'
                    granularity = 'second'
                elif ideal_interval_seconds <= 5:
                    interval = '5 seconds'
                    granularity = 'second'
                elif ideal_interval_seconds <= 10:
                    interval = '10 seconds'
                    granularity = 'second'
                elif ideal_interval_seconds <= 30:
                    interval = '30 seconds'
                    granularity = 'second'
                elif ideal_interval_seconds <= 60:
                    interval = '1 minute'
                    granularity = 'minute'
                elif ideal_interval_seconds <= 120:
                    interval = '2 minutes'
                    granularity = 'minute'
                elif ideal_interval_seconds <= 300:
                    interval = '5 minutes'
                    granularity = 'minute'
                elif ideal_interval_seconds <= 600:
                    interval = '10 minutes'
                    granularity = 'minute'
                elif ideal_interval_seconds <= 900:
                    interval = '15 minutes'
                    granularity = 'minute'
                elif ideal_interval_seconds <= 1800:
                    interval = '30 minutes'
                    granularity = 'minute'
                elif ideal_interval_seconds <= 3600:
                    interval = '1 hour'
                    granularity = 'hour'
                elif ideal_interval_seconds <= 7200:
                    interval = '2 hours'
                    granularity = 'hour'
                elif ideal_interval_seconds <= 14400:
                    interval = '4 hours'
                    granularity = 'hour'
                elif ideal_interval_seconds <= 21600:
                    interval = '6 hours'
                    granularity = 'hour'
                elif ideal_interval_seconds <= 43200:
                    interval = '12 hours'
                    granularity = 'hour'
                else:
                    interval = '1 day'
                    granularity = 'day'
                
                timeline_data = []
                
                # 计算间隔秒数用于时间桶对齐
                interval_seconds_map = {
                    '1 second': 1, '5 seconds': 5, '10 seconds': 10, '30 seconds': 30,
                    '1 minute': 60, '2 minutes': 120, '5 minutes': 300, '10 minutes': 600,
                    '15 minutes': 900, '30 minutes': 1800, '1 hour': 3600, '2 hours': 7200,
                    '4 hours': 14400, '6 hours': 21600, '12 hours': 43200, '1 day': 86400
                }
                interval_seconds = interval_seconds_map.get(interval, 60)  # 默认1分钟
                
                for queue_name in (query.queues or []):
                    # 使用对齐到固定边界的时间序列生成方案
                    # 注意：需要匹配基础队列名及其所有优先级队列
                    query_sql = text(f"""
                        WITH time_series AS (
                            -- 生成对齐到固定边界的时间序列
                            SELECT generate_series(
                                to_timestamp(FLOOR(EXTRACT(epoch FROM CAST(:start_time AS timestamptz)) / {interval_seconds}) * {interval_seconds}),
                                to_timestamp(CEILING(EXTRACT(epoch FROM CAST(:end_time AS timestamptz)) / {interval_seconds}) * {interval_seconds} + {interval_seconds}),
                                CAST(:interval_val AS interval)
                            ) AS time_bucket
                        ),
                        task_counts AS (
                            SELECT 
                                -- 任务时间也对齐到相同边界
                                to_timestamp(
                                    FLOOR(EXTRACT(epoch FROM t.created_at) / {interval_seconds}) * {interval_seconds}
                                ) AS time_bucket,
                                COUNT(t.stream_id) as count,
                                COUNT(CASE WHEN t.stream_id NOT IN (SELECT stream_id FROM task_runs) THEN 1 END) as pending,
                                COUNT(CASE WHEN EXISTS (SELECT 1 FROM task_runs tr WHERE tr.stream_id = t.stream_id AND tr.status = 'pending') THEN 1 END) as processing
                            FROM tasks t
                            WHERE t.namespace = :namespace
                                -- 匹配基础队列名和所有优先级队列（如 shared_queue, shared_queue:0, shared_queue:5 等）
                                AND (t.queue = :queue_name OR t.queue LIKE :queue_pattern)
                                AND t.created_at >= :start_time
                                AND t.created_at <= :end_time
                            GROUP BY 1
                        )
                        SELECT 
                            ts.time_bucket,
                            COALESCE(tc.count, 0) as value,
                            COALESCE(tc.pending, 0) as pending,
                            COALESCE(tc.processing, 0) as processing
                        FROM time_series ts
                        LEFT JOIN task_counts tc ON ts.time_bucket = tc.time_bucket
                        ORDER BY ts.time_bucket
                    """)
                    
                    result = await session.execute(query_sql, {
                        'namespace': namespace,
                        'queue_name': queue_name,
                        'queue_pattern': f'{queue_name}:%',  # 匹配所有优先级队列
                        'start_time': start_time,
                        'end_time': end_time,
                        'interval_val': interval
                    })
                    
                    # 转换结果为列表以便获取索引
                    rows = list(result)
                    end_index = len(rows) - 1
                    
                    for idx, row in enumerate(rows):
                        timeline_data.append({
                            'time': row.time_bucket.isoformat(),
                            'queue': queue_name,
                            'value': int(row.value) or None if idx > 0 and end_index != idx else int(row.value)
                        })
                
                return {
                    "data": timeline_data,
                    "granularity": granularity
                }
                
            except Exception as e:
                logger.warning(f"查询时序数据失败，返回当前快照: {e}")
                traceback.print_exc()
                
                # 如果查询失败，返回Redis当前快照
                redis_client = await conn.get_redis_client()
                try:
                    timeline_data = []
                    for queue_name in (query.queues or []):
                        queue_key = f"{conn.redis_prefix}:QUEUE:{queue_name}"
                        queue_len = await redis_client.xlen(queue_key)
                        
                        timeline_data.append({
                            'time': end_time.isoformat(),
                            'queue': queue_name,
                            'value': queue_len
                        })
                    
                    return {
                        "data": timeline_data,
                        "granularity": "snapshot"
                    }
                finally:
                    await redis_client.aclose()
            
    except Exception as e:
        logger.error(f"获取队列时间线失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/queue-consumers/{namespace}/{queue_name}")
async def get_queue_consumers(namespace: str, queue_name: str):
    """
    获取指定命名空间中队列的消费者信息
    
    Args:
        namespace: 命名空间名称
        queue_name: 队列名称
    """
    try:
        conn = await data_access.manager.get_connection(namespace)
        redis_client = await conn.get_redis_client()
        
        try:
            queue_key = f"{conn.redis_prefix}:QUEUE:{queue_name}"
            
            # 获取消费组信息
            groups_info = await redis_client.xinfo_groups(queue_key)
            
            result = {
                'queue_name': queue_name,
                'consumer_groups': []
            }
            
            for group in groups_info:
                # 获取消费者详情
                consumers_info = await redis_client.xinfo_consumers(queue_key, group['name'])
                
                group_data = {
                    'name': group['name'],
                    'consumers': group.get('consumers', 0),
                    'pending': group.get('pending', 0),
                    'last_delivered_id': group.get('last-delivered-id'),
                    'consumer_details': []
                }
                
                for consumer in consumers_info:
                    group_data['consumer_details'].append({
                        'name': consumer.get('name'),
                        'pending': consumer.get('pending', 0),
                        'idle': consumer.get('idle', 0)
                    })
                
                result['consumer_groups'].append(group_data)
            
            return result
            
        finally:
            await redis_client.aclose()
            
    except Exception as e:
        logger.error(f"获取消费者信息失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system-stats/{namespace}")
async def get_system_stats(namespace: str):
    """
    获取指定命名空间的系统统计信息
    
    Args:
        namespace: 命名空间名称
    """
    try:
        conn = await data_access.manager.get_connection(namespace)
        redis_client = await conn.get_redis_client()
        
        try:
            # 统计各种类型的键
            stats = {
                'namespace': namespace,
                'queues': 0,
                'tasks': 0,
                'delayed_tasks': 0,
                'workers': 0
            }
            
            # 统计队列数量
            queue_pattern = f"{conn.redis_prefix}:QUEUE:*"
            async for _ in redis_client.scan_iter(match=queue_pattern):
                stats['queues'] += 1
            
            # 统计任务数量
            task_pattern = f"{conn.redis_prefix}:TASK:*"
            async for _ in redis_client.scan_iter(match=task_pattern):
                stats['tasks'] += 1
            
            # 统计延迟任务数量
            delayed_pattern = f"{conn.redis_prefix}:DELAYED_QUEUE:*"
            async for key in redis_client.scan_iter(match=delayed_pattern):
                count = await redis_client.zcard(key)
                stats['delayed_tasks'] += count
            
            # 统计工作进程数量
            worker_pattern = f"{conn.redis_prefix}:WORKER:*"
            async for _ in redis_client.scan_iter(match=worker_pattern):
                stats['workers'] += 1
            
            return stats
            
        finally:
            await redis_client.aclose()
            
    except Exception as e:
        logger.error(f"获取系统统计信息失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/queue-details/{namespace}")
async def get_queue_details(namespace: str, query: TimeRangeQuery):
    """
    获取指定命名空间中队列的详细信息
    
    Args:
        namespace: 命名空间名称
        query: 查询参数（包含队列列表和时间范围）
    """
    try:
        conn = await data_access.manager.get_connection(namespace)
        redis_client = await conn.get_redis_client()
        
        # 确定时间范围
        end_time = datetime.now(timezone.utc)
        if query.time_range and query.time_range != 'custom':
            # 解析时间范围字符串
            if query.time_range.endswith('m'):
                minutes = int(query.time_range[:-1])
                start_time = end_time - timedelta(minutes=minutes)
            elif query.time_range.endswith('h'):
                hours = int(query.time_range[:-1])
                start_time = end_time - timedelta(hours=hours)
            elif query.time_range.endswith('d'):
                days = int(query.time_range[:-1])
                start_time = end_time - timedelta(days=days)
            else:
                start_time = end_time - timedelta(minutes=15)
        else:
            # 使用自定义时间范围或默认值
            start_time = query.start_time or (end_time - timedelta(minutes=15))
            end_time = query.end_time or end_time
        
        result = []
        
        for queue_name in query.queues:
            queue_key = f"{conn.redis_prefix}:QUEUE:{queue_name}"
            
            # 获取Redis中的队列信息
            queue_len = await redis_client.xlen(queue_key)
            
            # 获取消费组信息
            try:
                groups_info = await redis_client.xinfo_groups(queue_key)
                consumer_groups = len(groups_info)
                total_consumers = sum(g.get('consumers', 0) for g in groups_info)
                
                # 计算所有消费者已领取但未确认的消息数（不可见消息）
                invisible_messages_count = 0
                for group in groups_info:
                    try:
                        consumers = await redis_client.xinfo_consumers(queue_key, group['name'])
                        for consumer in consumers:
                            invisible_messages_count += consumer.get('pending', 0)  # 消费者已领取但未确认
                    except:
                        pass
                
                # 注意：这里不再使用这些变量，将在后面根据数据库的pending任务重新计算
                # visible_messages_count 和 invisible_messages_count 将在获取数据库数据后重新计算
                
            except:
                consumer_groups = 0
                total_consumers = 0
                invisible_messages_count = 0
                # visible_messages_count 将在获取数据库数据后计算
            
            # 获取活跃的workers数量
            active_workers = 0
            try:
                worker_keys = []
                async for key in redis_client.scan_iter(match=f"{conn.redis_prefix}:WORKER:*"):
                    worker_keys.append(key)
                
                for worker_key in worker_keys:
                    worker_info = await redis_client.hgetall(worker_key)
                    if worker_info:
                        last_heartbeat = worker_info.get('last_heartbeat')
                        if last_heartbeat:
                            try:
                                heartbeat_time = float(last_heartbeat)
                                if time.time() - heartbeat_time < 60:  # 60秒内有心跳
                                    worker_queues = worker_info.get('queues', '')
                                    if queue_name in worker_queues:
                                        active_workers += 1
                            except:
                                pass
            except Exception as e:
                logger.warning(f"获取活跃workers失败: {e}")
                traceback.print_exc()
            
            # 从PostgreSQL获取统计数据
            total_tasks = 0
            pending_tasks_db = 0  # 数据库中的pending任务数
            completed_tasks = 0
            failed_tasks = 0
            processing_tasks = 0
            enqueue_rate = 0
            dequeue_rate = 0
            tasks_per_minute = 0
            
            if conn.pg_config:
                try:
                    async with await conn.get_pg_session() as session:
                        # 查询任务统计
                        query_sql = text("""
                            SELECT 
                                COUNT(DISTINCT t.stream_id) as total,
                                COUNT(DISTINCT CASE WHEN t.stream_id NOT IN (SELECT stream_id FROM task_runs) THEN t.stream_id END) as pending,
                                COUNT(DISTINCT CASE WHEN tr.status = 'success' THEN t.stream_id END) as completed,
                                COUNT(DISTINCT CASE WHEN tr.status = 'error' THEN t.stream_id END) as failed,
                                COUNT(DISTINCT CASE WHEN tr.status = 'pending' THEN t.stream_id END) as processing,
                                COUNT(DISTINCT CASE WHEN t.created_at >= :recent_time THEN t.stream_id END) as recent_created,
                                COUNT(DISTINCT CASE WHEN tr.status = 'success' AND tr.end_time >= :recent_time THEN t.stream_id END) as recent_completed
                            FROM tasks t
                            LEFT JOIN task_runs tr ON t.stream_id = tr.stream_id
                            WHERE t.namespace = :namespace
                                -- 匹配基础队列名和所有优先级队列
                                AND (t.queue = :queue_name OR t.queue LIKE :queue_pattern)
                                AND t.created_at >= :start_time
                                AND t.created_at <= :end_time
                        """)
                        
                        # 最近1分钟的时间点，用于计算速率
                        recent_time = end_time - timedelta(minutes=1)
                        
                        params = {
                            'namespace': namespace,
                            'queue_name': queue_name,
                            'queue_pattern': f'{queue_name}:%',  # 匹配所有优先级队列
                            'start_time': start_time,
                            'end_time': end_time,
                            'recent_time': recent_time
                        }
                        print(f'PostgreSQL查询参数: {params}')
                        
                        result_db = await session.execute(query_sql, params)
                        
                        row = result_db.first()
                        print(f'PostgreSQL查询结果: {row=}')
                        
                        # 额外调试：检查是否有该队列的任务（不限时间）
                        debug_query = text("SELECT COUNT(*) as count FROM tasks WHERE namespace = :namespace AND (queue = :queue_name OR queue LIKE :queue_pattern)")
                        debug_result = await session.execute(debug_query, {
                            'namespace': namespace,
                            'queue_name': queue_name,
                            'queue_pattern': f'{queue_name}:%'
                        })
                        debug_row = debug_result.first()
                        print(f'该队列总任务数（不限时间）: {debug_row.count if debug_row else 0}')
                        if row:
                            total_tasks = row.total or 0
                            pending_tasks_db = row.pending or 0  # 获取数据库中的pending任务数
                            completed_tasks = row.completed or 0
                            failed_tasks = row.failed or 0
                            processing_tasks = row.processing or 0
                            
                            # 计算速率（基于最近1分钟）
                            enqueue_rate = row.recent_created or 0
                            dequeue_rate = row.recent_completed or 0
                            
                            # 计算整个时间段的平均处理速度
                            time_diff_minutes = (end_time - start_time).total_seconds() / 60
                            if time_diff_minutes > 0:
                                tasks_per_minute = round(total_tasks / time_diff_minutes, 2)
                            
                except Exception as e:
                    logger.warning(f"查询数据库失败: {e}")
                    traceback.print_exc()
            
            # 根据用户要求重新计算可见和不可见消息
            # 注意：这里的计算基于时间范围内的数据库pending任务
            # 但Redis的invisible_messages_count是实时的，可能包含时间范围外的任务
            # 为了保持逻辑一致，我们使用以下计算：
            # - 如果时间范围内没有pending任务，则可见和不可见都为0
            # - 否则，不可见消息取Redis实际值和DB pending任务的较小值
            if pending_tasks_db > 0:
                # 不可见消息不能超过pending任务总数
                actual_invisible = min(invisible_messages_count, pending_tasks_db)
                visible_messages_count = pending_tasks_db - actual_invisible
            else:
                visible_messages_count = 0
                actual_invisible = 0
            
            result.append({
                'queue_name': queue_name,
                # 基于查询条件的数据库统计
                'message_count': total_tasks,  # 符合查询条件的任务总数（来自数据库）
                'visible_messages': visible_messages_count,  # 可见消息 = DB pending - min(Redis invisible, DB pending)
                'invisible_messages': actual_invisible,  # 不可见消息 = min(Redis invisible, DB pending)
                'processing': processing_tasks,  # 数据库中processing状态的任务数
                'queue_length': queue_len,  # Redis实时队列长度（保留用于参考）
                
                # 历史统计数据（来自PostgreSQL）- 基于选定时间范围
                'completed': completed_tasks,  # 时间范围内已完成
                'failed': failed_tasks,  # 时间范围内失败
                'consumption_rate': tasks_per_minute,  # 消费速度
                'enqueue_rate': enqueue_rate,  # 入队速率
                'dequeue_rate': dequeue_rate,  # 出队速率
                
                # 混合数据
                'success_rate': round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 2),  # 成功率（基于历史）
                'queue_status': 'active' if queue_len > 0 or active_workers > 0 else 'idle',  # 状态（基于实时）
                'active_workers': active_workers,  # 活跃Workers
                'consumer_groups': consumer_groups,  # 消费组数
                'consumers': total_consumers,  # 消费者数
                
                # 调试信息（可选）
                'historical_tasks': total_tasks,  # 时间范围内的任务总数（用于调试）
            })
        
        await redis_client.aclose()
        return {'success': True, 'data': result}
        
    except Exception as e:
        logger.error(f"获取队列详情失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/queue-flow-rates/{namespace}")
async def get_queue_flow_rates(namespace: str, query: TimeRangeQuery):
    """
    获取指定命名空间中队列的流量速率（入队、完成、失败）
    
    Args:
        namespace: 命名空间名称
        query: 时间范围查询参数
    """
    try:
        print(f'请求参数: get_queue_flow_rates {namespace=}, {query=}')
        
        # 使用公共工具函数处理时间范围
        time_range_result = parse_time_range_query(query)
        start_time = time_range_result.start_time
        end_time = time_range_result.end_time
        
        print(f'时间范围: {start_time=}, {end_time=}')
        
        # 使用命名空间数据访问
        conn = await data_access.manager.get_connection(namespace)
        
        # 如果没有PostgreSQL配置，返回空数据
        if not conn.pg_config:
            return {"data": [], "granularity": "minute"}
        
        async with await conn.get_pg_session() as session:
            # 如果没有指定队列，获取所有队列
            if not query.queues or len(query.queues) == 0:
                # 获取所有队列名称
                queue_sql = text("""
                    SELECT DISTINCT queue 
                    FROM tasks 
                    WHERE namespace = :namespace 
                    ORDER BY queue
                """)
                queue_result = await session.execute(queue_sql, {'namespace': namespace})
                all_queues = [row.queue for row in queue_result.fetchall()]
                
                print(f'所有队列: {all_queues=}')
                
                if not all_queues:
                    return {"data": [], "granularity": "minute"}
                
                # 统计所有队列的流量数据
                queue_conditions = "(" + " OR ".join([f"t.queue = '{queue}'" for queue in all_queues]) + ")"
            else:
                # 使用指定的队列（支持基础队列名和优先级队列）
                queue_name = query.queues[0]
                # 匹配精确队列名或带优先级的队列名（如 shared_queue 或 shared_queue:5）
                queue_conditions = f"(t.queue = '{queue_name}' OR t.queue LIKE '{queue_name}:%')"
                print(f'指定队列: {queue_name=}, 条件: {queue_conditions}')
            
            # 使用已计算好的时间间隔信息
            interval = time_range_result.interval
            interval_seconds = time_range_result.interval_seconds
            granularity = time_range_result.granularity
            
            # 查询流量数据
            flow_sql = text(f"""
                WITH time_series AS (
                    SELECT to_timestamp(FLOOR(EXTRACT(epoch FROM ts) / {interval_seconds}) * {interval_seconds}) AS time_bucket
                    FROM generate_series(
                        :start_time ::timestamptz,
                        :end_time ::timestamptz + INTERVAL '{interval_seconds} seconds',
                        :interval_val ::interval
                    ) AS ts
                ),
                enqueue_counts AS (
                    SELECT 
                        to_timestamp(FLOOR(EXTRACT(epoch FROM t.created_at) / {interval_seconds}) * {interval_seconds}) AS time_bucket,
                        COUNT(*) as enqueued
                    FROM tasks t
                    WHERE t.namespace = :namespace
                        AND ({queue_conditions})
                        AND t.created_at >= :start_time
                        AND t.created_at <= :end_time
                    GROUP BY time_bucket
                ),
                complete_counts AS (
                    SELECT 
                        to_timestamp(FLOOR(EXTRACT(epoch FROM tr.end_time) / {interval_seconds}) * {interval_seconds}) AS time_bucket,
                        COUNT(*) as completed
                    FROM task_runs tr
                    JOIN tasks t ON tr.stream_id = t.stream_id
                    WHERE t.namespace = :namespace
                        AND ({queue_conditions})
                        AND tr.end_time >= :start_time
                        AND tr.end_time <= :end_time
                        AND tr.status = 'success'
                    GROUP BY time_bucket
                ),
                failed_counts AS (
                    SELECT 
                        to_timestamp(FLOOR(EXTRACT(epoch FROM tr.end_time) / {interval_seconds}) * {interval_seconds}) AS time_bucket,
                        COUNT(*) as failed
                    FROM task_runs tr
                    JOIN tasks t ON tr.stream_id = t.stream_id
                    WHERE t.namespace = :namespace
                        AND ({queue_conditions})
                        AND tr.end_time >= :start_time
                        AND tr.end_time <= :end_time
                        AND tr.status = 'error'
                    GROUP BY time_bucket
                )
                SELECT 
                    ts.time_bucket,
                    COALESCE(eq.enqueued, 0) as enqueued,
                    COALESCE(cc.completed, 0) as completed,
                    COALESCE(fc.failed, 0) as failed
                FROM time_series ts
                LEFT JOIN enqueue_counts eq ON ts.time_bucket = eq.time_bucket
                LEFT JOIN complete_counts cc ON ts.time_bucket = cc.time_bucket
                LEFT JOIN failed_counts fc ON ts.time_bucket = fc.time_bucket
                ORDER BY ts.time_bucket
            """)
            
            # 先查询tasks表看有没有数据（不限时间范围）
            test_sql = text("""
                SELECT COUNT(*) as total_count,
                       COUNT(CASE WHEN created_at >= :start_time AND created_at <= :end_time THEN 1 END) as range_count,
                       MIN(created_at) as min_time,
                       MAX(created_at) as max_time
                FROM tasks 
                WHERE namespace = :namespace
            """)
            test_result = await session.execute(test_sql, {
                'namespace': namespace,
                'start_time': start_time,
                'end_time': end_time
            })
            test_row = test_result.fetchone()
            print(f'tasks表统计 - 总记录数: {test_row.total_count}, 时间范围内: {test_row.range_count}')
            print(f'tasks表时间范围: {test_row.min_time} 到 {test_row.max_time}')
            
            result = await session.execute(flow_sql, {
                'namespace': namespace,
                'start_time': start_time,
                'end_time': end_time,
                'interval_val': interval
            })
            
            # 格式化数据
            data = []
            rows = result.fetchall()
            print(f'查询结果行数: {len(rows)}')
            end_index = len(rows) - 1
            
            for idx, row in enumerate(rows):
                time_point = row.time_bucket.isoformat()
                
                # 直接使用实际值，不管是否为0
                # 这样可以保持与tasks接口的行为一致
                data.append({'time': time_point, 'value': row.enqueued, 'metric': '入队速率'})
                data.append({'time': time_point, 'value': row.completed, 'metric': '完成速率'})
                data.append({'time': time_point, 'value': row.failed, 'metric': '失败数'})
            
            return {"data": data, "granularity": granularity}
        
        # 下面是新的实现，暂时注释掉
        '''
        # 获取命名空间连接
        conn = await data_access.manager.get_connection(namespace)
        
        # 如果没有PostgreSQL配置，返回模拟数据
        if not conn.pg_config:
            # 生成模拟数据
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(minutes=15)
            
            data = []
            num_points = 10
            for i in range(num_points):
                timestamp = start_time + timedelta(seconds=i * 90)
                time_str = timestamp.isoformat()
                
                data.append({'time': time_str, 'value': 10 + i, 'metric': '入队速率'})
                data.append({'time': time_str, 'value': 8 + i, 'metric': '完成速率'})
                data.append({'time': time_str, 'value': 1, 'metric': '失败数'})
            
            return {"data": data, "granularity": "minute"}
        
        # 处理时间范围
        end_time = datetime.now(timezone.utc)
        if query.time_range and query.time_range != 'custom':
            # 解析时间范围字符串
            if query.time_range.endswith('m'):
                minutes = int(query.time_range[:-1])
                start_time = end_time - timedelta(minutes=minutes)
            elif query.time_range.endswith('h'):
                hours = int(query.time_range[:-1])
                start_time = end_time - timedelta(hours=hours)
            elif query.time_range.endswith('d'):
                days = int(query.time_range[:-1])
                start_time = end_time - timedelta(days=days)
            else:
                start_time = end_time - timedelta(minutes=15)
        else:
            # 使用自定义时间范围或默认值
            start_time = query.start_time or (end_time - timedelta(minutes=15))
            end_time = query.end_time or end_time
        
        # 从PostgreSQL查询流量数据
        async with await conn.get_pg_session() as session:
            # 动态计算时间间隔
            duration = (end_time - start_time).total_seconds()
            TARGET_POINTS = 200
            ideal_interval_seconds = duration / TARGET_POINTS
            
            # 选择合适的间隔
            if ideal_interval_seconds <= 1:
                interval = '1 second'
                granularity = 'second'
            elif ideal_interval_seconds <= 5:
                interval = '5 seconds'
                granularity = 'second'
            elif ideal_interval_seconds <= 10:
                interval = '10 seconds'
                granularity = 'second'
            elif ideal_interval_seconds <= 30:
                interval = '30 seconds'
                granularity = 'second'
            elif ideal_interval_seconds <= 60:
                interval = '1 minute'
                granularity = 'minute'
            elif ideal_interval_seconds <= 300:
                interval = '5 minutes'
                granularity = 'minute'
            elif ideal_interval_seconds <= 600:
                interval = '10 minutes'
                granularity = 'minute'
            elif ideal_interval_seconds <= 900:
                interval = '15 minutes'
                granularity = 'minute'
            elif ideal_interval_seconds <= 1800:
                interval = '30 minutes'
                granularity = 'minute'
            elif ideal_interval_seconds <= 3600:
                interval = '1 hour'
                granularity = 'hour'
            else:
                interval = '1 day'
                granularity = 'day'
            
            # 构建筛选条件
            filter_conditions = []
            if query.filters:
                for filter_item in query.filters:
                    field = filter_item.get('field')
                    operator = filter_item.get('operator')
                    value = filter_item.get('value')
                    
                    if field and operator and value:
                        if operator == 'eq':
                            filter_conditions.append(f"AND {field} = '{value}'")
                        elif operator == 'ne':
                            filter_conditions.append(f"AND {field} != '{value}'")
                        elif operator == 'contains':
                            filter_conditions.append(f"AND {field} LIKE '%{value}%'")
            
            extra_where = " ".join(filter_conditions)
            
            # 根据间隔确定聚合粒度
            if granularity == 'second':
                if ideal_interval_seconds <= 1:
                    time_trunc = 'second'
                    interval_seconds = 1
                elif ideal_interval_seconds <= 5:
                    time_trunc = '5 seconds'
                    interval_seconds = 5
                elif ideal_interval_seconds <= 10:
                    time_trunc = '10 seconds'
                    interval_seconds = 10
                else:
                    time_trunc = '30 seconds'
                    interval_seconds = 30
            elif granularity == 'minute':
                time_trunc = 'minute'
                interval_seconds = 60
            elif granularity == 'hour':
                time_trunc = 'hour'  
                interval_seconds = 3600
            else:
                time_trunc = 'day'
                interval_seconds = 86400
            
            # 查询入队速率、完成速率和失败数
            # 重要：时间序列也要对齐到相同的时间桶
            query_sql = text(f"""
                WITH time_series AS (
                    SELECT to_timestamp(FLOOR(EXTRACT(epoch FROM ts) / {interval_seconds}) * {interval_seconds}) AS time_bucket
                    FROM generate_series(
                        :start_time ::timestamptz,
                        :end_time ::timestamptz,
                        :interval_val ::interval
                    ) AS ts
                ),
                enqueued_rate AS (
                    SELECT 
                        to_timestamp(FLOOR(EXTRACT(epoch FROM created_at) / {interval_seconds}) * {interval_seconds}) AS time_bucket,
                        COUNT(*) AS count
                    FROM tasks
                    WHERE namespace = :namespace
                        AND queue_name = :queue_name
                        AND created_at >= :start_time
                        AND created_at <= :end_time
                    GROUP BY 1
                ),
                completed_rate AS (
                    SELECT 
                        to_timestamp(FLOOR(EXTRACT(epoch FROM completed_at) / {interval_seconds}) * {interval_seconds}) AS time_bucket,
                        COUNT(*) AS count
                    FROM tasks
                    WHERE namespace = :namespace
                        AND queue_name = :queue_name
                        AND completed_at >= :start_time
                        AND completed_at <= :end_time
                        AND status = 'success'
                    GROUP BY 1
                ),
                failed_rate AS (
                    SELECT 
                        to_timestamp(FLOOR(EXTRACT(epoch FROM completed_at) / {interval_seconds}) * {interval_seconds}) AS time_bucket,
                        COUNT(*) AS count
                    FROM tasks
                    WHERE namespace = :namespace
                        AND queue_name = :queue_name
                        AND completed_at >= :start_time
                        AND completed_at <= :end_time
                        AND status = 'error'
                    GROUP BY 1
                )
                SELECT 
                    ts.time_bucket,
                    COALESCE(e.count, 0) AS enqueued,
                    COALESCE(c.count, 0) AS completed,
                    COALESCE(f.count, 0) AS failed
                FROM time_series ts
                LEFT JOIN enqueued_rate e ON ts.time_bucket = e.time_bucket
                LEFT JOIN completed_rate c ON ts.time_bucket = c.time_bucket
                LEFT JOIN failed_rate f ON ts.time_bucket = f.time_bucket
                ORDER BY ts.time_bucket
            """)
            
            result = await session.execute(query_sql, {
                'namespace': namespace,
                'queue_name': queue_name,
                'start_time': start_time,
                'end_time': end_time,
                'interval_val': interval
            })
            
            # 格式化数据为前端需要的格式
            data = []
            rows = result.fetchall()
            end_index = len(rows) - 1
            
            for idx, row in enumerate(rows):
                time_str = row.time_bucket.isoformat()
                
                # 对于中间的数据点，如果值为0则设为None，让图表自动连接
                # 只保留第一个和最后一个点的0值
                enqueued_val = row.enqueued if row.enqueued > 0 or idx == 0 or idx == end_index else None
                completed_val = row.completed if row.completed > 0 or idx == 0 or idx == end_index else None
                failed_val = row.failed if row.failed > 0 or idx == 0 or idx == end_index else None
                
                data.append({'time': time_str, 'value': enqueued_val, 'metric': '入队速率'})
                data.append({'time': time_str, 'value': completed_val, 'metric': '完成速率'})
                data.append({'time': time_str, 'value': failed_val, 'metric': '失败数'})
            
            return {"data": data, "granularity": granularity}
        '''
            
    except Exception as e:
        logger.error(f"获取队列流量速率失败: {e}")
        traceback.print_exc()
        
        await handle_database_connection_error(e, namespace, "获取队列流量数据")


@router.get("/dashboard-stats/{namespace}")
async def get_dashboard_stats(
    namespace: str,
    time_range: str = "24h",
    queues: Optional[str] = Query(None, description="逗号分隔的队列名称列表")
):
    """
    获取仪表板统计数据（任务总数、成功数、失败数、成功率、吞吐量等）
    
    Args:
        namespace: 命名空间名称
        time_range: 时间范围（如'1h', '24h', '7d'）
    """
    try:
        conn = await data_access.manager.get_connection(namespace)
        
        # 如果没有PostgreSQL配置，返回空数据
        if not conn.pg_config:
            return {
                "success": True,
                "data": {
                    "total_tasks": 0,
                    "completed_tasks": 0,
                    "failed_tasks": 0,
                    "running_tasks": 0,
                    "pending_tasks": 0,
                    "success_rate": 0,
                    "throughput": 0,
                    "avg_processing_time": 0,
                    "total_queues": 0
                }
            }
        
        # 计算时间范围
        end_time = datetime.now(timezone.utc)
        if time_range.endswith('m'):
            minutes = int(time_range[:-1])
            start_time = end_time - timedelta(minutes=minutes)
        elif time_range.endswith('h'):
            hours = int(time_range[:-1])
            start_time = end_time - timedelta(hours=hours)
        elif time_range.endswith('d'):
            days = int(time_range[:-1])
            start_time = end_time - timedelta(days=days)
        else:
            start_time = end_time - timedelta(hours=24)  # 默认24小时
        
        # 构建队列筛选条件
        queue_filter, queue_list, queue_params = build_queue_filter_and_params(queues)
        print(f'🔍 Dashboard Stats - 收到队列参数: {queues}')
        print(f'🔍 Dashboard Stats - 解析后的队列列表: {queue_list}')
        print(f'🔍 Dashboard Stats - SQL筛选条件: {queue_filter}')
        print(f'🔍 Dashboard Stats - 查询参数: {queue_params}')
        async with await conn.get_pg_session() as session:
            # 获取任务统计数据
            # 修复：正确区分pending任务（在tasks表但不在task_runs表中的任务）
            stats_sql = text(f"""
                WITH task_stats AS (
                    SELECT 
                        t.stream_id,
                        t.created_at,
                        t.queue,
                        tr.status,
                        tr.execution_time,
                        tr.end_time
                    FROM tasks t
                    LEFT JOIN task_runs tr ON t.stream_id = tr.stream_id
                    WHERE t.namespace = :namespace
                        AND t.created_at >= :start_time
                        AND t.created_at <= :end_time
                        {queue_filter}
                )
                SELECT 
                    COUNT(DISTINCT stream_id) as total_tasks,
                    COUNT(DISTINCT CASE WHEN status = 'success' THEN stream_id END) as completed_tasks,
                    COUNT(DISTINCT CASE WHEN status = 'error' THEN stream_id END) as failed_tasks,
                    COUNT(DISTINCT CASE WHEN status = 'running' THEN stream_id END) as running_tasks,
                    -- pending任务：在tasks表中但没有在task_runs表中（status为NULL）或status='pending'
                    COUNT(DISTINCT CASE WHEN status IS NULL OR status = 'pending' THEN stream_id END) as pending_tasks,
                    COUNT(DISTINCT queue) as total_queues,
                    AVG(CASE WHEN status = 'success' AND execution_time IS NOT NULL 
                        THEN execution_time END) as avg_execution_time
                FROM task_stats
            """)
            
            # 准备查询参数
            query_params = {
                'namespace': namespace,
                'start_time': start_time,
                'end_time': end_time,
                **queue_params
            }
            
            print(f'🔍 Dashboard Stats - 最终SQL: {stats_sql}')
            print(f'🔍 Dashboard Stats - 最终查询参数: {query_params}')
            
            # 调试：查看数据库中实际的队列名称
            debug_sql = text("""
                SELECT DISTINCT t.queue 
                FROM tasks t 
                WHERE t.namespace = :namespace 
                    AND t.created_at >= :start_time 
                    AND t.created_at <= :end_time 
                LIMIT 10
            """)
            debug_result = await session.execute(debug_sql, {
                'namespace': namespace,
                'start_time': start_time,
                'end_time': end_time
            })
            actual_queues = [row.queue for row in debug_result.fetchall()]
            print(f'🔍 Dashboard Stats - 数据库中实际的队列名称: {actual_queues}')
            
            result = await session.execute(stats_sql, query_params)
            
            row = result.first()
            
            if row:
                total_tasks = row.total_tasks or 0
                completed_tasks = row.completed_tasks or 0
                failed_tasks = row.failed_tasks or 0
                pending_tasks = row.pending_tasks or 0
                total_queues = row.total_queues or 0
                avg_execution_time = row.avg_execution_time or 0
                
                # 从task_runs表计算当前正在执行的任务数（start_time <= now < end_time）
                running_tasks = 0
                try:
                    running_sql = text(f"""
                        SELECT COUNT(*) as total_running
                        FROM task_runs tr
                        JOIN tasks t ON tr.stream_id = t.stream_id
                        WHERE t.namespace = :namespace
                            AND tr.start_time IS NOT NULL
                            AND tr.start_time <= NOW()
                            AND (tr.end_time IS NULL OR tr.end_time > NOW())
                            {queue_filter}
                    """)
                    
                    running_result = await session.execute(running_sql, query_params)
                    
                    running_row = running_result.first()
                    running_tasks = int(running_row.total_running) if running_row else 0
                    
                except Exception as e:
                    logger.warning(f"计算当前并发任务数失败，使用默认值: {e}")
                    traceback.print_exc()
                    running_tasks = row.running_tasks or 0
                
                # 计算成功率
                success_rate = round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1)
                
                # 计算吞吐量（每分钟完成的任务数）
                # 使用递进的时间窗口来找到最合适的吞吐量计算方式
                recent_end_time = datetime.now(timezone.utc)
                throughput = 0
                
                # 尝试多个时间窗口，从短到长，找到有足够数据的窗口
                time_windows = [
                    (5, "最近5分钟"),
                    (10, "最近10分钟"), 
                    (30, "最近30分钟"),
                    (60, "最近1小时")
                ]
                
                for window_minutes, window_desc in time_windows:
                    recent_start_time = recent_end_time - timedelta(minutes=window_minutes)
                    
                    recent_query = text(f"""
                        SELECT COUNT(DISTINCT t.stream_id) as recent_completed
                        FROM tasks t
                        LEFT JOIN task_runs tr ON t.stream_id = tr.stream_id
                        WHERE t.namespace = :namespace
                            AND tr.status = 'success'
                            AND tr.end_time >= :recent_start_time
                            AND tr.end_time <= :recent_end_time
                            {queue_filter}
                    """)
                    
                    # 准备吞吐量查询参数
                    throughput_params = {
                        'namespace': namespace,
                        'recent_start_time': recent_start_time,
                        'recent_end_time': recent_end_time,
                        **queue_params
                    }
                    
                    recent_result = await session.execute(recent_query, throughput_params)
                    
                    recent_row = recent_result.first()
                    recent_completed = recent_row.recent_completed if recent_row else 0
                    
                    print(f'🔍 Dashboard Stats - 吞吐量计算 {window_desc}: {recent_completed} 个任务完成')
                    
                    # 如果这个时间窗口有足够的数据（至少5个任务），就使用它
                    if recent_completed >= 5:
                        throughput = round(recent_completed / window_minutes, 1)
                        logger.info(f"使用{window_desc}计算吞吐量: {recent_completed}个任务/{window_minutes}分钟 = {throughput}任务/分钟")
                        break
                    elif recent_completed > 0:
                        # 如果有少量数据，也计算但继续寻找更好的窗口
                        throughput = round(recent_completed / window_minutes, 1)
                
                # 如果所有窗口都没有数据，吞吐量为0
                if throughput == 0:
                    logger.info("最近1小时内没有完成的任务，吞吐量为0")
                
                # 将execution_time从秒转换为毫秒
                avg_processing_time = round(avg_execution_time * 1000 if avg_execution_time else 0, 1)
                
                # 同时获取任务数量分布数据（按队列分组，不区分状态）
                distribution_sql = text(f"""
                    SELECT 
                        t.queue,
                        COUNT(DISTINCT t.stream_id) as count
                    FROM tasks t
                    WHERE t.namespace = :namespace
                        AND t.created_at >= :start_time
                        AND t.created_at <= :end_time
                        {queue_filter}
                    GROUP BY t.queue
                    ORDER BY count DESC, t.queue
                """)
                
                distribution_result = await session.execute(distribution_sql, query_params)
                
                # 格式化分布数据为饼图格式（只按队列，不区分状态）
                distribution_data = []
                
                for row in distribution_result.fetchall():
                    queue = row.queue
                    count = row.count
                    
                    if count > 0:
                        distribution_data.append({
                            'type': queue,  # 直接使用队列名，不添加状态后缀
                            'value': count,
                            'queue': queue,
                            'status': 'all'  # 表示所有状态
                        })
                
                # 如果没有数据，返回默认值
                if not distribution_data:
                    distribution_data = [
                        {'type': '暂无数据', 'value': 1, 'queue': '', 'status': 'empty'}
                    ]
                
                return {
                    "success": True,
                    "data": {
                        "total_tasks": total_tasks,
                        "completed_tasks": completed_tasks,
                        "failed_tasks": failed_tasks,
                        "running_tasks": running_tasks,
                        "pending_tasks": pending_tasks,
                        "success_rate": success_rate,
                        "throughput": throughput,
                        "avg_processing_time": avg_processing_time,
                        "total_queues": total_queues,
                        "time_range": time_range,
                        "start_time": start_time.isoformat(),
                        "end_time": end_time.isoformat(),
                        "task_distribution": distribution_data  # 新增：任务状态分布数据
                    }
                }
            else:
                return {
                    "success": True,
                    "data": {
                        "total_tasks": 0,
                        "completed_tasks": 0,
                        "failed_tasks": 0,
                        "running_tasks": 0,
                        "pending_tasks": 0,
                        "success_rate": 0,
                        "throughput": 0,
                        "avg_processing_time": 0,
                        "total_queues": 0
                    }
                }
                
    except Exception as e:
        logger.error(f"获取仪表板统计数据失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/queue-backlog-trend/{namespace}")
async def get_queue_backlog_trend(
    namespace: str,
    time_range: str = "1h",
    queue_name: Optional[str] = None,
    queues: Optional[str] = Query(None, description="逗号分隔的队列名称列表")
):
    """
    获取队列积压趋势数据（排队任务数）
    
    Args:
        namespace: 命名空间名称
        time_range: 时间范围（如'1h', '24h', '7d'）
        queue_name: 队列名称（可选，不指定则获取所有队列的总积压）
    """
    try:
        conn = await data_access.manager.get_connection(namespace)
        
        # 使用公共工具函数处理时间范围
        time_range_result = parse_time_range_string(time_range)
        start_time = time_range_result.start_time
        end_time = time_range_result.end_time
        interval = time_range_result.interval
        interval_seconds = time_range_result.interval_seconds
        
        # 如果没有PostgreSQL配置，返回模拟数据
        if not conn.pg_config:
            # 生成模拟的排队任务数趋势
            data = []
            num_points = min(50, max(10, int((end_time - start_time).total_seconds() / interval_seconds)))
            
            for i in range(num_points):
                timestamp = start_time + timedelta(seconds=i * interval_seconds)
                data.append({
                    'time': timestamp.isoformat(),
                    'value': max(0, 5 + int(2 * (0.5 - abs(i - num_points/2) / (num_points/2)))),  # 模拟波动
                    'metric': '排队任务数'
                })
            
            return {"data": data, "granularity": "minute"}
        
        async with await conn.get_pg_session() as session:
            # 从stream_backlog_monitor表获取数据，使用pending_count字段
            try:
                backlog_sql = text(f"""
                    WITH time_series AS (
                        SELECT to_timestamp(FLOOR(EXTRACT(epoch FROM ts) / {interval_seconds}) * {interval_seconds}) AS time_bucket
                        FROM generate_series(
                            :start_time ::timestamptz,
                            :end_time ::timestamptz,
                            :interval_val ::interval
                        ) AS ts
                    ),
                    backlog_data AS (
                        SELECT 
                            to_timestamp(FLOOR(EXTRACT(epoch FROM created_at) / {interval_seconds}) * {interval_seconds}) AS time_bucket,
                            -- 使用pending_count字段，它表示实际的待处理任务数
                            -- 如果没有pending_count，则使用0
                            MAX(COALESCE(pending_count, 0)) as max_pending
                        FROM stream_backlog_monitor
                        WHERE namespace = :namespace
                            AND created_at >= :start_time
                            AND created_at <= :end_time
                            {f"AND stream_name = :queue_name" if queue_name else ""}
                        GROUP BY 1
                    )
                    SELECT 
                        ts.time_bucket,
                        COALESCE(bd.max_pending, 0) as pending_value
                    FROM time_series ts
                    LEFT JOIN backlog_data bd ON ts.time_bucket = bd.time_bucket
                    ORDER BY ts.time_bucket
                """)
                
                params = {
                    'namespace': namespace,
                    'start_time': start_time,
                    'end_time': end_time,
                    'interval_val': interval
                }
                if queue_name:
                    params['queue_name'] = queue_name
                
                result = await session.execute(backlog_sql, params)
                rows = result.fetchall()
                
                # 直接使用pending_count数据，不需要检查是否有非零值
                data = []
                for idx, row in enumerate(rows):
                    # 第0个和最后一个元素的value不能为null，其他的可以为null
                    is_first_or_last = idx == 0 or idx == len(rows) - 1
                    value = int(row.pending_value) if row.pending_value > 0 else (0 if is_first_or_last else None)
                    
                    data.append({
                        'time': row.time_bucket.isoformat(),
                        'value': value,
                        'metric': '排队任务数'
                    })
                return {"data": data, "granularity": "minute"}
                
            except Exception as e:
                logger.error(f"从stream_backlog_monitor获取数据失败: {e}")
                traceback.print_exc()
                raise HTTPException(status_code=500, detail=f"获取排队任务数据失败: {str(e)}")
            
    except Exception as e:
        logger.error(f"获取队列积压趋势失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/task-creation-latency/{namespace}")
async def get_task_creation_latency(
    namespace: str,
    time_range: str = "1h"
):
    """
    获取任务创建延时趋势数据
    
    Args:
        namespace: 命名空间名称
        time_range: 时间范围（如'1h', '24h', '7d'）
    """
    try:
        conn = await data_access.manager.get_connection(namespace)
        
        # 计算时间范围
        end_time = datetime.now(timezone.utc)
        if time_range.endswith('m'):
            minutes = int(time_range[:-1])
            start_time = end_time - timedelta(minutes=minutes)
            interval = '1 minute'
            interval_seconds = 60
        elif time_range.endswith('h'):
            hours = int(time_range[:-1])
            start_time = end_time - timedelta(hours=hours)
            interval = '5 minutes' if hours <= 6 else '10 minutes'
            interval_seconds = 300 if hours <= 6 else 600
        elif time_range.endswith('d'):
            days = int(time_range[:-1])
            start_time = end_time - timedelta(days=days)
            interval = '1 hour'
            interval_seconds = 3600
        else:
            start_time = end_time - timedelta(hours=1)
            interval = '1 minute'
            interval_seconds = 60
        
        # 如果没有PostgreSQL配置，返回模拟数据
        if not conn.pg_config:
            data = []
            num_points = min(30, max(10, int((end_time - start_time).total_seconds() / interval_seconds)))
            
            for i in range(num_points):
                timestamp = start_time + timedelta(seconds=i * interval_seconds)
                data.append({
                    'time': timestamp.isoformat(),
                    'value': 50 + 20 * (0.5 - abs((i - num_points/2) / (num_points/2))),  # 模拟延时波动
                    'type': '创建延时'
                })
            
            return {"data": data, "granularity": "minute"}
        
        async with await conn.get_pg_session() as session:
            # 计算任务创建延时（从提交到开始处理的时间）
            try:
                latency_sql = text(f"""
                    WITH time_series AS (
                        SELECT to_timestamp(FLOOR(EXTRACT(epoch FROM ts) / {interval_seconds}) * {interval_seconds}) AS time_bucket
                        FROM generate_series(
                            :start_time ::timestamptz,
                            :end_time ::timestamptz,
                            :interval_val ::interval
                        ) AS ts
                    ),
                    task_latency AS (
                        SELECT 
                            to_timestamp(FLOOR(EXTRACT(epoch FROM tr.start_time) / {interval_seconds}) * {interval_seconds}) AS time_bucket,
                            AVG(EXTRACT(epoch FROM (tr.start_time - t.created_at))) as avg_latency_seconds
                        FROM tasks t
                        JOIN task_runs tr ON t.stream_id = tr.stream_id
                        WHERE t.namespace = :namespace
                            AND tr.start_time >= :start_time
                            AND tr.start_time <= :end_time
                            AND tr.start_time IS NOT NULL
                        GROUP BY 1
                    )
                    SELECT 
                        ts.time_bucket,
                        COALESCE(tl.avg_latency_seconds, 0) as latency_ms
                    FROM time_series ts
                    LEFT JOIN task_latency tl ON ts.time_bucket = tl.time_bucket
                    ORDER BY ts.time_bucket
                """)
                
                result = await session.execute(latency_sql, {
                    'namespace': namespace,
                    'start_time': start_time,
                    'end_time': end_time,
                    'interval_val': interval
                })
                
                data = []
                for row in result.fetchall():
                    # 转换为毫秒
                    latency_ms = row.latency_ms * 1000 if row.latency_ms > 0 else None
                    data.append({
                        'time': row.time_bucket.isoformat(),
                        'value': round(latency_ms, 1) if latency_ms else None,
                        'type': '创建延时'
                    })
                
                return {"data": data, "granularity": "minute"}
                
            except Exception as e:
                logger.error(f"获取任务创建延时失败: {e}")
                traceback.print_exc()
                raise HTTPException(status_code=500, detail=f"获取创建延时数据失败: {str(e)}")
            
    except Exception as e:
        logger.error(f"获取任务创建延时失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top-queues/{namespace}")
async def get_top_queues(
    namespace: str,
    metric: str = Query("backlog", description="指标类型: backlog(积压) 或 error(错误率)"),
    limit: int = 10,
    time_range: str = "24h",
    queues: Optional[str] = Query(None, description="逗号分隔的队列名称列表")
):
    """
    获取队列排行榜 - 支持积压和错误率两种指标
    
    Args:
        namespace: 命名空间名称
        metric: 指标类型 (backlog/error)
        limit: 返回的队列数量限制
        time_range: 时间范围
    """
    if metric == "backlog":
        return await _get_top_backlog_queues(namespace, limit, queues)
    elif metric == "error":
        return await _get_top_error_queues(namespace, limit, time_range, queues)
    else:
        raise HTTPException(status_code=400, detail=f"不支持的指标类型: {metric}")


@router.get("/top-backlog-queues/{namespace}")
async def get_top_backlog_queues(
    namespace: str,
    limit: int = 10,
    time_range: str = Query("1h", description="时间范围，如1h、24h、7d"),
    queues: Optional[str] = Query(None, description="逗号分隔的队列名称列表")
):
    """
    获取积压最多的队列Top10 (已废弃，请使用 /top-queues/{namespace}?metric=backlog)
    
    Args:
        namespace: 命名空间名称
        limit: 返回的队列数量限制
        time_range: 时间范围，如1h、24h、7d
    """
    return await _get_top_backlog_queues(namespace, limit, time_range, queues)


async def _get_top_backlog_queues(
    namespace: str,
    limit: int = 10,
    time_range: str = "1h",
    queues: Optional[str] = None
):
    """
    内部方法：获取积压最多的队列Top10
    """
    try:
        conn = await data_access.manager.get_connection(namespace)
        
        # 计算时间范围
        end_time = datetime.now(timezone.utc)
        if time_range.endswith('h'):
            hours = int(time_range[:-1])
            start_time = end_time - timedelta(hours=hours)
        elif time_range.endswith('d'):
            days = int(time_range[:-1])
            start_time = end_time - timedelta(days=days)
        else:
            # 默认1小时
            start_time = end_time - timedelta(hours=1)
        
        # 如果没有PostgreSQL配置，返回空数据
        if not conn.pg_config:
            return {
                "success": True,
                "data": []
            }
        
        async with await conn.get_pg_session() as session:
            try:
                # 处理队列筛选参数
                queue_list = []
                if queues:
                    queue_list = [q.strip() for q in queues.split(',') if q.strip()]
                
                # 优先从stream_backlog_monitor获取最新的积压数据
                # 使用backlog_unprocessed字段表示总积压（包括未投递和已投递未处理的消息）
                if queue_list:
                    backlog_sql = text("""
                        SELECT 
                            stream_name as queue,
                            MAX(backlog_unprocessed) as backlog,
                            CASE 
                                WHEN MAX(backlog_unprocessed) > 100 THEN 'critical'
                                WHEN MAX(backlog_unprocessed) > 50 THEN 'warning'
                                ELSE 'normal'
                            END as status
                        FROM stream_backlog_monitor
                        WHERE namespace = :namespace
                            AND created_at >= :start_time
                            AND created_at <= :end_time
                            AND stream_name = ANY(:queues)
                        GROUP BY stream_name
                        HAVING MAX(backlog_unprocessed) > 0
                        ORDER BY backlog DESC
                        LIMIT :limit
                    """)
                    
                    result = await session.execute(backlog_sql, {
                        'namespace': namespace,
                        'start_time': start_time,
                        'end_time': end_time,
                        'queues': queue_list,
                        'limit': limit
                    })
                else:
                    backlog_sql = text("""
                        SELECT 
                            stream_name as queue,
                            MAX(backlog_unprocessed) as backlog,
                            CASE 
                                WHEN MAX(backlog_unprocessed) > 100 THEN 'critical'
                                WHEN MAX(backlog_unprocessed) > 50 THEN 'warning'
                                ELSE 'normal'
                            END as status
                        FROM stream_backlog_monitor
                        WHERE namespace = :namespace
                            AND created_at >= :start_time
                            AND created_at <= :end_time
                        GROUP BY stream_name
                        HAVING MAX(backlog_unprocessed) > 0
                        ORDER BY backlog DESC
                        LIMIT :limit
                    """)
                    
                    result = await session.execute(backlog_sql, {
                        'namespace': namespace,
                        'start_time': start_time,
                        'end_time': end_time,
                        'limit': limit
                    })
                
                backlog_queues = []
                for row in result.fetchall():
                    backlog_queues.append({
                        "queue": row.queue,
                        "backlog": int(row.backlog),
                        "status": row.status
                    })
                
                if backlog_queues:
                    return {"success": True, "data": backlog_queues}
                
            except Exception as e:
                logger.warning(f"从stream_backlog_monitor获取积压数据失败: {e}")
                traceback.print_exc()
            
            # 如果没有积压监控数据，从tasks表统计pending任务
            try:
                task_sql = text("""
                    SELECT 
                        t.queue,
                        COUNT(DISTINCT t.stream_id) as backlog,
                        CASE 
                            WHEN COUNT(DISTINCT t.stream_id) > 1000 THEN 'critical'
                            WHEN COUNT(DISTINCT t.stream_id) > 500 THEN 'warning'
                            ELSE 'normal'
                        END as status
                    FROM tasks t
                    LEFT JOIN task_runs tr ON t.stream_id = tr.stream_id
                    WHERE t.namespace = :namespace
                        AND (tr.stream_id IS NULL OR tr.status = 'pending')
                        AND t.created_at > NOW() - INTERVAL '24 hour'
                    GROUP BY t.queue
                    ORDER BY backlog DESC
                    LIMIT :limit
                """)
                
                result = await session.execute(task_sql, {
                    'namespace': namespace,
                    'limit': limit
                })
                
                backlog_queues = []
                for row in result.fetchall():
                    backlog_queues.append({
                        "queue": row.queue,
                        "backlog": int(row.backlog),
                        "status": row.status
                    })
                
                return {"success": True, "data": backlog_queues}
                
            except Exception as e:
                logger.error(f"从tasks表获取积压数据失败: {e}")
                traceback.print_exc()
                raise HTTPException(status_code=500, detail=f"获取积压排行数据失败: {str(e)}")
            
    except Exception as e:
        logger.error(f"获取积压排行失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top-error-queues/{namespace}")
async def get_top_error_queues(
    namespace: str,
    limit: int = 10,
    time_range: str = "24h",
    queues: Optional[str] = Query(None, description="逗号分隔的队列名称列表")
):
    """
    获取错误率最高的队列Top10 (已废弃，请使用 /top-queues/{namespace}?metric=error)
    
    Args:
        namespace: 命名空间名称
        limit: 返回的队列数量限制
        time_range: 时间范围
    """
    return await _get_top_error_queues(namespace, limit, time_range, queues)


async def _get_top_error_queues(
    namespace: str,
    limit: int = 10,
    time_range: str = "24h",
    queues: Optional[str] = None
):
    """
    内部方法：获取错误率最高的队列Top10
    """
    try:
        conn = await data_access.manager.get_connection(namespace)
        
        # 计算时间范围
        end_time = datetime.now(timezone.utc)
        if time_range.endswith('h'):
            hours = int(time_range[:-1])
            start_time = end_time - timedelta(hours=hours)
        elif time_range.endswith('d'):
            days = int(time_range[:-1])
            start_time = end_time - timedelta(days=days)
        else:
            start_time = end_time - timedelta(hours=24)
        
        # 如果没有PostgreSQL配置，返回空数据
        if not conn.pg_config:
            return {
                "success": True,
                "data": []
            }
        
        async with await conn.get_pg_session() as session:
            try:
                # 直接从task_runs表查询，因为只有执行过的任务才会有错误记录
                # 通过consumer_group提取队列名（格式通常是 namespace:QUEUE:queue_name:task_name）
                error_sql = text("""
                    WITH queue_stats AS (
                        SELECT 
                            CASE 
                                WHEN consumer_group LIKE :queue_prefix || '%'
                                THEN SPLIT_PART(consumer_group, ':', 3)
                                ELSE consumer_group
                            END as queue,
                            COUNT(DISTINCT stream_id) as total,
                            COUNT(DISTINCT CASE WHEN status IN ('failed', 'error', 'timeout') THEN stream_id END) as failed
                        FROM task_runs
                        WHERE created_at >= :start_time
                            AND created_at <= :end_time
                            AND consumer_group LIKE :namespace_prefix || '%'
                        GROUP BY 1
                    )
                    SELECT 
                        queue,
                        total,
                        failed,
                        ROUND(failed * 100.0 / NULLIF(total, 0), 1) as error_rate
                    FROM queue_stats
                    WHERE failed > 0
                    ORDER BY error_rate DESC, failed DESC
                    LIMIT :limit
                """)
                
                result = await session.execute(error_sql, {
                    'namespace_prefix': f'{namespace}:',
                    'queue_prefix': f'{namespace}:QUEUE:',
                    'start_time': start_time,
                    'end_time': end_time,
                    'limit': limit
                })
                
                error_queues = []
                for row in result.fetchall():
                    error_queues.append({
                        "queue": row.queue,
                        "errorRate": str(row.error_rate or 0),
                        "failed": int(row.failed),
                        "total": int(row.total)
                    })
                
                return {"success": True, "data": error_queues}
                
            except Exception as e:
                logger.error(f"获取错误率排行数据失败: {e}")
                traceback.print_exc()
                raise HTTPException(status_code=500, detail=f"获取错误率排行数据失败: {str(e)}")
            
    except Exception as e:
        logger.error(f"获取错误率排行失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/task-concurrency-trend/{namespace}")
async def get_task_concurrency_trend(
    namespace: str,
    time_range: str = "1h"
):
    """
    获取任务执行数量趋势数据（每个时间间隔内开始执行的任务数量）
    
    Args:
        namespace: 命名空间名称
        time_range: 时间范围（如'1h', '24h', '7d'）
    """
    try:
        conn = await data_access.manager.get_connection(namespace)
        
        # 计算时间范围
        end_time = datetime.now(timezone.utc)
        if time_range.endswith('m'):
            minutes = int(time_range[:-1])
            start_time = end_time - timedelta(minutes=minutes)
            interval = '1 minute'
            interval_seconds = 60
        elif time_range.endswith('h'):
            hours = int(time_range[:-1])
            start_time = end_time - timedelta(hours=hours)
            interval = '5 minutes' if hours <= 6 else '10 minutes'
            interval_seconds = 300 if hours <= 6 else 600
        elif time_range.endswith('d'):
            days = int(time_range[:-1])
            start_time = end_time - timedelta(days=days)
            interval = '1 hour'
            interval_seconds = 3600
        else:
            start_time = end_time - timedelta(hours=1)
            interval = '1 minute'
            interval_seconds = 60
        
        async with await conn.get_pg_session() as session:
            try:
                # 计算每个时间间隔内执行的任务数量（更实用的指标）
                concurrency_sql = text(f"""
                    WITH time_series AS (
                        SELECT 
                            to_timestamp(FLOOR(EXTRACT(epoch FROM ts) / {interval_seconds}) * {interval_seconds}) AS time_bucket_start,
                            to_timestamp(FLOOR(EXTRACT(epoch FROM ts) / {interval_seconds}) * {interval_seconds}) + INTERVAL '{interval_seconds} seconds' AS time_bucket_end
                        FROM generate_series(
                            :start_time ::timestamptz,
                            :end_time ::timestamptz,
                            :interval_val ::interval
                        ) AS ts
                    )
                    SELECT 
                        ts.time_bucket_start as time_bucket,
                        COUNT(tr.stream_id) as concurrent_count
                    FROM time_series ts
                    LEFT JOIN task_runs tr ON (
                        EXISTS (
                            SELECT 1 FROM tasks t 
                            WHERE t.stream_id = tr.stream_id 
                            AND t.namespace = :namespace
                        )
                        AND tr.start_time IS NOT NULL 
                        AND tr.start_time >= ts.time_bucket_start
                        AND tr.start_time < ts.time_bucket_end
                    )
                    GROUP BY ts.time_bucket_start
                    ORDER BY ts.time_bucket_start
                """)
                
                result = await session.execute(concurrency_sql, {
                    'namespace': namespace,
                    'start_time': start_time,
                    'end_time': end_time,
                    'interval_val': interval
                })
                
                data = []
                for row in result.fetchall():
                    concurrent_count = row.concurrent_count or 0
                    data.append({
                        'time': row.time_bucket.isoformat(),
                        'value': int(concurrent_count),
                        'type': '执行数量'
                    })
                
                return {"data": data, "granularity": "minute"}
                
            except Exception as e:
                logger.error(f"获取任务并发数据失败: {e}")
                traceback.print_exc()
                # 如果查询失败，从Redis获取当前并发数作为静态数据
                try:
                    redis_client = await conn.get_redis_client()
                    
                    # 统计当前正在处理的任务数
                    worker_pattern = f"{conn.redis_prefix}:WORKER:*"
                    current_concurrent = 0
                    
                    async for worker_key in redis_client.scan_iter(match=worker_pattern):
                        worker_info = await redis_client.hgetall(worker_key)
                        if worker_info and worker_info.get('status') == 'busy':
                            current_concurrent += 1
                    
                    await redis_client.aclose()
                    
                    # 生成静态数据点
                    data = []
                    num_points = min(20, max(5, int((end_time - start_time).total_seconds() / interval_seconds)))
                    
                    for i in range(num_points):
                        timestamp = start_time + timedelta(seconds=i * interval_seconds)
                        data.append({
                            'time': timestamp.isoformat(),
                            'value': current_concurrent if i == num_points - 1 else None,
                            'type': '并发数'
                        })
                    
                    return {"data": data, "granularity": "minute"}
                    
                except Exception as redis_error:
                    logger.error(f"从Redis获取并发数据也失败: {redis_error}")
                    raise HTTPException(status_code=500, detail=f"获取并发数据失败: {str(e)}")
            
    except Exception as e:
        logger.error(f"获取任务并发趋势失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tasks/{namespace}")
async def get_namespace_tasks(namespace: str, request: Request):
    """
    获取指定命名空间中队列的任务列表
    
    Args:
        namespace: 命名空间名称
        request: 请求体，包含queue_name、分页、筛选等参数
    """
    try:
        # 解析请求体
        body = await request.json()
        queue_name = body.get('queue_name')
        page = body.get('page', 1)
        page_size = body.get('page_size', 20)
        filters = body.get('filters', [])
        sort_field = body.get('sort_field')
        sort_order = body.get('sort_order', 'desc')
        
        # 处理时间范围参数
        start_time = body.get('start_time')
        end_time = body.get('end_time')
        time_range = body.get('time_range')
        
        if not queue_name:
            raise HTTPException(status_code=400, detail="queue_name is required")
        
        # 获取命名空间连接
        conn = await data_access.manager.get_connection(namespace)
        
        # 如果没有PostgreSQL配置，返回空数据
        if not conn.pg_config:
            return {
                "success": True,
                "data": [],
                "total": 0,
                "page": page,
                "page_size": page_size
            }
        
        # 如果提供了时间范围，计算起止时间
        if not start_time or not end_time:
            if time_range and time_range != 'custom':
                now = datetime.now(timezone.utc)
                time_range_map = {
                    "15m": timedelta(minutes=15),
                    "30m": timedelta(minutes=30),
                    "1h": timedelta(hours=1),
                    "3h": timedelta(hours=3),
                    "6h": timedelta(hours=6),
                    "12h": timedelta(hours=12),
                    "24h": timedelta(hours=24),
                    "7d": timedelta(days=7),
                    "30d": timedelta(days=30),
                }
                
                delta = time_range_map.get(time_range)
                if delta:
                    end_time = now
                    start_time = end_time - delta
        
        # 如果有时间范围，将其转换为datetime对象
        if start_time and isinstance(start_time, str):
            start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        if end_time and isinstance(end_time, str):
            end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        
        # 从PostgreSQL查询任务数据
        async with await conn.get_pg_session() as session:
            # 构建基础查询（支持基础队列名和优先级队列）
            query_conditions = ["t.namespace = :namespace", "(t.queue = :queue_name OR t.queue LIKE :queue_pattern)"]
            query_params = {
                'namespace': namespace,
                'queue_name': queue_name,
                'queue_pattern': f'{queue_name}:%'  # 匹配所有优先级队列
            }
            
            # 添加时间范围条件
            if start_time:
                query_conditions.append("t.created_at >= :start_time")
                query_params['start_time'] = start_time
            if end_time:
                query_conditions.append("t.created_at <= :end_time")
                query_params['end_time'] = end_time
            
            # 添加筛选条件
            for filter_item in filters:
                # 跳过被禁用的筛选条件
                if filter_item.get('enabled') == False:
                    continue
                    
                field = filter_item.get('field')
                operator = filter_item.get('operator')
                value = filter_item.get('value')
                
                if not field or not operator:
                    continue
                
                # 特殊处理id字段（映射到stream_id）
                if field == 'id':
                    actual_field = 'stream_id'
                    table_prefix = 't.'
                elif field == 'scheduled_task_id':
                    # scheduled_task_id特殊处理，需要转换为字符串
                    actual_field = field
                    table_prefix = 't.'
                    # 将值转换为字符串
                    if operator == 'eq':
                        query_conditions.append(f"{table_prefix}{actual_field} = :{field}")
                        query_params[field] = str(value)
                    elif operator == 'ne':
                        query_conditions.append(f"{table_prefix}{actual_field} != :{field}")
                        query_params[field] = str(value)
                    elif operator == 'contains':
                        query_conditions.append(f"{table_prefix}{actual_field} LIKE :{field}")
                        query_params[field] = f'%{str(value)}%'
                    continue  # 跳过后续的通用处理
                else:
                    actual_field = field
                    # 根据字段决定使用哪个表的别名
                    table_prefix = 't.'
                    if field in ['status', 'task_name', 'worker_id', 'consumer_group']:
                        table_prefix = 'tr.'
                    elif field in ['queue', 'namespace', 'stream_id']:
                        table_prefix = 't.'
                
                # 简单的相等筛选
                if operator == 'eq':
                    # 对于status字段的特殊处理
                    if field == 'status' and value == 'pending':
                        # pending状态：task_runs中没有记录（status为NULL）或status='pending'
                        query_conditions.append(f"({table_prefix}{actual_field} IS NULL OR {table_prefix}{actual_field} = :{field})")
                        query_params[field] = value
                    else:
                        query_conditions.append(f"{table_prefix}{actual_field} = :{field}")
                        query_params[field] = value
                elif operator == 'ne':
                    # 对于status字段的特殊处理，需要包含NULL值
                    if field == 'status':
                        # 使用COALESCE处理NULL值，将NULL视为'pending'
                        query_conditions.append(f"(COALESCE({table_prefix}{actual_field}, 'pending') != :{field})")
                        query_params[field] = value
                    else:
                        query_conditions.append(f"{table_prefix}{actual_field} != :{field}")
                        query_params[field] = value
                elif operator == 'contains':
                    query_conditions.append(f"{table_prefix}{actual_field} LIKE :{field}")
                    query_params[field] = f'%{value}%'
            
            # 构建WHERE子句
            where_clause = " AND ".join(query_conditions)
            
            # 计算总数（需要JOIN因为WHERE条件可能涉及task_runs表）
            count_sql = text(f"""
                SELECT COUNT(DISTINCT t.stream_id) 
                FROM tasks t 
                LEFT JOIN task_runs tr ON t.stream_id = tr.stream_id
                WHERE {where_clause}
            """)
            total_result = await session.execute(count_sql, query_params)
            total = total_result.scalar()
            
            # 构建排序子句
            order_clause = "t.created_at DESC"  # 默认排序
            if sort_field:
                # 根据字段添加正确的表别名
                if sort_field in ['created_at', 'queue', 'stream_id']:
                    order_clause = f"t.{sort_field} {sort_order.upper()}"
                elif sort_field in ['status', 'task_name', 'worker_id', 'consumer_group', 'started_at', 'completed_at']:
                    order_clause = f"tr.{sort_field} {sort_order.upper()}"
                else:
                    order_clause = f"{sort_field} {sort_order.upper()}"
            
            # 查询任务列表（连接tasks和task_runs表）
            offset = (page - 1) * page_size
            query_sql = text(f"""
                SELECT 
                    t.stream_id as id,
                    COALESCE(tr.status, 'pending') as status,
                    COALESCE(tr.task_name, t.payload->>'task_name', 'unknown') as task_name,
                    t.queue as queue_name,
                    tr.consumer_group,
                    tr.worker_id,
                    t.created_at,
                    tr.start_time as started_at,
                    tr.end_time as completed_at,
                    tr.duration,
                    tr.execution_time,
                    t.payload as task_data,
                    tr.result,
                    tr.error_message,
                    tr.retry_count
                FROM tasks t
                LEFT JOIN task_runs tr ON t.stream_id = tr.stream_id
                WHERE {where_clause}
                ORDER BY {order_clause}
                LIMIT :limit OFFSET :offset
            """)
            
            query_params['limit'] = page_size
            query_params['offset'] = offset
            
            result = await session.execute(query_sql, query_params)
            
            # 格式化数据
            tasks = []
            for row in result:
                # 使用error_message字段或从result中提取错误信息
                error = row.error_message
                retry_count = row.retry_count if row.retry_count else 0
                
                if not error and row.result:
                    try:
                        import json
                        result_data = json.loads(row.result) if isinstance(row.result, str) else row.result
                        if isinstance(result_data, dict):
                            error = result_data.get('error')
                    except:
                        pass
                
                task = {
                    'id': row.id,
                    'status': row.status,
                    'task_name': row.task_name,  # 改为task_name以匹配前端
                    'queue': row.queue_name,
                    'consumer_group': row.consumer_group if row.consumer_group else '-',  # 添加消费者组字段
                    'worker_id': row.worker_id,
                    'created_at': row.created_at.isoformat() if row.created_at else None,
                    'started_at': row.started_at.isoformat() if row.started_at else None,
                    'completed_at': row.completed_at.isoformat() if row.completed_at else None,
                    'error': error,
                    'retry_count': retry_count
                }
                
                # 执行时间（从开始到完成）- 直接使用秒数值
                if row.execution_time is not None:
                    task['execution_time'] = row.execution_time  # 返回数字类型，前端会格式化
                else:
                    task['execution_time'] = None
             
                
                # 计算总耗时（从创建到完成）
                if row.created_at and row.completed_at:
                    duration = (row.completed_at - row.created_at).total_seconds()
                    task['duration'] = duration  # 返回数字类型，前端会格式化
                elif row.created_at and row.status == 'running':
                    # 如果任务还在运行，计算从创建到现在的时间
                    duration = (datetime.now(timezone.utc) - row.created_at).total_seconds()
                    task['duration'] = duration
                else:
                    task['duration'] = None
                
                tasks.append(task)
            
            return {
                "success": True,
                "data": tasks,
                "total": total,
                "page": page,
                "page_size": page_size
            }
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error(f"获取任务列表失败: {e}")
        
        await handle_database_connection_error(e, namespace, "获取任务列表")


@router.get("/message-offset-trend/{namespace}")
async def get_message_offset_trend(
    namespace: str,
    time_range: str = "1h"
):
    """
    获取消息offset趋势数据（投递和确认进度）
    
    Args:
        namespace: 命名空间名称
        time_range: 时间范围（如'1h', '24h', '7d'）
    """
    try:
        conn = await data_access.manager.get_connection(namespace)
        
        # 计算时间范围
        end_time = datetime.now(timezone.utc)
        if time_range.endswith('m'):
            minutes = int(time_range[:-1])
            start_time = end_time - timedelta(minutes=minutes)
            interval = '1 minute'
            interval_seconds = 60
        elif time_range.endswith('h'):
            hours = int(time_range[:-1])
            start_time = end_time - timedelta(hours=hours)
            interval = '5 minutes' if hours <= 6 else '10 minutes'
            interval_seconds = 300 if hours <= 6 else 600
        elif time_range.endswith('d'):
            days = int(time_range[:-1])
            start_time = end_time - timedelta(days=days)
            interval = '1 hour'
            interval_seconds = 3600
        else:
            start_time = end_time - timedelta(hours=1)
            interval = '1 minute'
            interval_seconds = 60
        
        # 如果没有PostgreSQL配置，返回模拟数据
        if not conn.pg_config:
            data = []
            num_points = min(30, max(10, int((end_time - start_time).total_seconds() / interval_seconds)))
            
            for i in range(num_points):
                timestamp = start_time + timedelta(seconds=i * interval_seconds)
                base_offset = 1000 + i * 10
                data.extend([
                    {
                        'time': timestamp.isoformat(),
                        'value': base_offset + 10,
                        'type': '已发布Offset'
                    },
                    {
                        'time': timestamp.isoformat(),
                        'value': base_offset + 5,
                        'type': '已投递Offset'
                    },
                    {
                        'time': timestamp.isoformat(),
                        'value': base_offset,
                        'type': '已确认Offset'
                    }
                ])
            
            return {"data": data, "granularity": "minute"}
        
        async with await conn.get_pg_session() as session:
            try:
                # 从stream_backlog_monitor表获取offset进度的时间序列数据
                offset_sql = text(f"""
                    WITH time_series AS (
                        SELECT to_timestamp(FLOOR(EXTRACT(epoch FROM ts) / {interval_seconds}) * {interval_seconds}) AS time_bucket
                        FROM generate_series(
                            :start_time ::timestamptz,
                            :end_time ::timestamptz,
                            :interval_val ::interval
                        ) AS ts
                    ),
                    offset_aggregated AS (
                        SELECT 
                            to_timestamp(FLOOR(EXTRACT(epoch FROM created_at) / {interval_seconds}) * {interval_seconds}) AS time_bucket,
                            MAX(last_delivered_offset) as max_delivered_offset,
                            MAX(last_acked_offset) as max_acked_offset,
                            MAX(last_published_offset) as max_published_offset
                        FROM stream_backlog_monitor
                        WHERE namespace = :namespace
                            AND created_at >= :start_time
                            AND created_at <= :end_time
                        GROUP BY time_bucket
                    )
                    SELECT 
                        ts.time_bucket,
                        COALESCE(oa.max_delivered_offset, 0) as delivered_offset,
                        COALESCE(oa.max_acked_offset, 0) as acked_offset,
                        COALESCE(oa.max_published_offset, 0) as published_offset
                    FROM time_series ts
                    LEFT JOIN offset_aggregated oa ON ts.time_bucket = oa.time_bucket
                    ORDER BY ts.time_bucket
                """)
                
                result = await session.execute(offset_sql, {
                    'namespace': namespace,
                    'start_time': start_time,
                    'end_time': end_time,
                    'interval_val': interval
                })
                
                data = []
                for row in result.fetchall():
                    timestamp = row.time_bucket.isoformat()
                    
                    # 添加已发布offset数据
                    data.append({
                        'time': timestamp,
                        'value': int(row.published_offset),
                        'type': '已发布Offset'
                    })
                    
                    # 添加已投递offset数据
                    data.append({
                        'time': timestamp,
                        'value': int(row.delivered_offset),
                        'type': '已投递Offset'
                    })
                    
                    # 添加已确认offset数据
                    data.append({
                        'time': timestamp,
                        'value': int(row.acked_offset),
                        'type': '已确认Offset'
                    })
                
                return {"data": data, "granularity": "minute"}
                
            except Exception as e:
                logger.error(f"查询offset趋势数据失败: {e}")
                traceback.print_exc()
                # 返回模拟数据
                data = []
                num_points = min(20, max(10, int((end_time - start_time).total_seconds() / interval_seconds)))
                
                for i in range(num_points):
                    timestamp = start_time + timedelta(seconds=i * interval_seconds)
                    base_offset = 1000 + i * 10
                    data.extend([
                        {
                            'time': timestamp.isoformat(),
                            'value': base_offset + 10,
                            'type': '已发布Offset'
                        },
                        {
                            'time': timestamp.isoformat(),
                            'value': base_offset + 5,
                            'type': '已投递Offset'
                        },
                        {
                            'time': timestamp.isoformat(),
                            'value': base_offset,
                            'type': '已确认Offset'
                        }
                    ])
                
                return {"data": data, "granularity": "minute"}
                
    except Exception as e:
        logger.error(f"获取消息offset趋势失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dashboard-overview-stats/{namespace}")
async def get_dashboard_overview_stats(namespace: str, query: TimeRangeQuery):
    """
    获取概览页面的统一统计数据
    包含：任务处理趋势、任务并发数量、任务处理时间、任务执行延时
    
    Args:
        namespace: 命名空间名称
        query: 时间范围查询参数
    
    Returns:
        统一的时间序列数据，包含所有概览图表需要的指标和granularity字段
    """
    try:
        conn = await data_access.manager.get_connection(namespace)
        
        # 如果没有PostgreSQL配置，返回空数据
        if not conn.pg_config:
            return {
                "task_trend": [],
                "concurrency": [],
                "processing_time": [],
                "creation_latency": [],
                "granularity": "minute"
            }
        
        # 使用公共工具函数处理时间范围
        time_range_result = parse_time_range_query(query)
        start_time = time_range_result.start_time
        end_time = time_range_result.end_time
        interval = time_range_result.interval
        interval_seconds = time_range_result.interval_seconds
        granularity = time_range_result.granularity
        
        # 构建队列筛选条件
        queues_str = ','.join(query.queues) if query.queues else None
        queue_filter, queue_list, queue_params = build_queue_filter_and_params(queues_str)
        print(f'🔍 Dashboard Overview - 收到队列参数: {query.queues}')
        print(f'🔍 Dashboard Overview - SQL筛选条件: {queue_filter}')
        
        async with await conn.get_pg_session() as session:
            # 统一查询所有概览页面需要的数据
            sql = text(f"""
                WITH time_series AS (
                    SELECT to_timestamp(FLOOR(EXTRACT(epoch FROM ts) / {interval_seconds}) * {interval_seconds}) AS time_bucket
                    FROM generate_series(
                        :start_time ::timestamptz,
                        :end_time ::timestamptz + INTERVAL '{interval_seconds} seconds',
                        :interval_val ::interval
                    ) AS ts
                ),
                enqueue_counts AS (
                    SELECT 
                        to_timestamp(FLOOR(EXTRACT(epoch FROM t.created_at) / {interval_seconds}) * {interval_seconds}) AS time_bucket,
                        COUNT(DISTINCT t.stream_id) as enqueued
                    FROM tasks t
                    WHERE t.namespace = :namespace
                        AND t.created_at >= :start_time
                        AND t.created_at <= :end_time
                        {queue_filter}
                    GROUP BY time_bucket
                ),
                complete_counts AS (
                    SELECT 
                        to_timestamp(FLOOR(EXTRACT(epoch FROM tr.end_time) / {interval_seconds}) * {interval_seconds}) AS time_bucket,
                        COUNT(DISTINCT t.stream_id) as completed
                    FROM task_runs tr
                    JOIN tasks t ON tr.stream_id = t.stream_id
                    WHERE t.namespace = :namespace
                        AND tr.end_time >= :start_time
                        AND tr.end_time <= :end_time
                        AND tr.status = 'success'
                        -- 只统计在时间范围内创建的任务的完成情况
                        AND t.created_at >= :start_time
                        AND t.created_at <= :end_time
                        {queue_filter}
                    GROUP BY time_bucket
                ),
                failed_counts AS (
                    SELECT 
                        to_timestamp(FLOOR(EXTRACT(epoch FROM tr.end_time) / {interval_seconds}) * {interval_seconds}) AS time_bucket,
                        COUNT(DISTINCT t.stream_id) as failed
                    FROM task_runs tr
                    JOIN tasks t ON tr.stream_id = t.stream_id
                    WHERE t.namespace = :namespace
                        AND tr.end_time >= :start_time
                        AND tr.end_time <= :end_time
                        AND tr.status = 'error'
                        -- 只统计在时间范围内创建的任务的失败情况
                        AND t.created_at >= :start_time
                        AND t.created_at <= :end_time
                        {queue_filter}
                    GROUP BY time_bucket
                ),
                concurrency_data AS (
                    -- 计算每个时间桶内任务开始时的并发数
                    -- 统计唯一任务，避免重试导致的重复计数
                    SELECT 
                        to_timestamp(FLOOR(EXTRACT(epoch FROM tr.start_time) / {interval_seconds}) * {interval_seconds}) AS time_bucket,
                        COUNT(DISTINCT t.stream_id) as concurrent_tasks
                    FROM task_runs tr
                    JOIN tasks t ON tr.stream_id = t.stream_id
                    WHERE t.namespace = :namespace
                        AND tr.start_time >= :start_time
                        AND tr.start_time <= :end_time
                        AND tr.start_time IS NOT NULL
                        AND tr.end_time IS NOT NULL
                        -- 只统计在时间范围内创建的任务
                        AND t.created_at >= :start_time
                        AND t.created_at <= :end_time
                        {queue_filter}
                    GROUP BY time_bucket
                ),
                processing_time_data AS (
                    SELECT 
                        to_timestamp(FLOOR(EXTRACT(epoch FROM tr.end_time) / {interval_seconds}) * {interval_seconds}) AS time_bucket,
                        AVG(CASE WHEN tr.status = 'success' AND tr.execution_time > 0 
                            THEN tr.execution_time END) as avg_processing_time,
                        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY 
                            CASE WHEN tr.status = 'success' AND tr.execution_time > 0 
                            THEN tr.execution_time END) as p50_processing_time,
                        PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY 
                            CASE WHEN tr.status = 'success' AND tr.execution_time > 0 
                            THEN tr.execution_time END) as p90_processing_time
                    FROM task_runs tr
                    JOIN tasks t ON tr.stream_id = t.stream_id
                    WHERE t.namespace = :namespace
                        AND tr.end_time >= :start_time
                        AND tr.end_time <= :end_time
                        AND tr.status = 'success'
                        {queue_filter}
                    GROUP BY time_bucket
                ),
                creation_latency_data AS (
                    SELECT 
                        to_timestamp(FLOOR(EXTRACT(epoch FROM tr.start_time) / {interval_seconds}) * {interval_seconds}) AS time_bucket,
                        AVG(EXTRACT(EPOCH FROM (tr.start_time - t.created_at))) as avg_creation_latency,
                        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY 
                            EXTRACT(EPOCH FROM (tr.start_time - t.created_at))) as p50_creation_latency,
                        PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY 
                            EXTRACT(EPOCH FROM (tr.start_time - t.created_at))) as p90_creation_latency
                    FROM task_runs tr
                    JOIN tasks t ON tr.stream_id = t.stream_id
                    WHERE t.namespace = :namespace
                        AND tr.start_time >= :start_time
                        AND tr.start_time <= :end_time
                        AND tr.start_time IS NOT NULL
                        {queue_filter}
                    GROUP BY time_bucket
                )
                SELECT 
                    ts.time_bucket,
                    COALESCE(eq.enqueued, 0) as enqueued,
                    COALESCE(cc.completed, 0) as completed,
                    COALESCE(fc.failed, 0) as failed,
                    COALESCE(cd.concurrent_tasks, 0) as concurrent_tasks,
                    ROUND(ptd.avg_processing_time::numeric, 6) as avg_processing_time,
                    ROUND(ptd.p50_processing_time::numeric, 6) as p50_processing_time,
                    ROUND(ptd.p90_processing_time::numeric, 6) as p90_processing_time,
                    ROUND(cld.avg_creation_latency::numeric, 3) as avg_creation_latency,
                    ROUND(cld.p50_creation_latency::numeric, 3) as p50_creation_latency,
                    ROUND(cld.p90_creation_latency::numeric, 3) as p90_creation_latency
                FROM time_series ts
                LEFT JOIN enqueue_counts eq ON ts.time_bucket = eq.time_bucket
                LEFT JOIN complete_counts cc ON ts.time_bucket = cc.time_bucket
                LEFT JOIN failed_counts fc ON ts.time_bucket = fc.time_bucket
                LEFT JOIN concurrency_data cd ON ts.time_bucket = cd.time_bucket
                LEFT JOIN processing_time_data ptd ON ts.time_bucket = ptd.time_bucket
                LEFT JOIN creation_latency_data cld ON ts.time_bucket = cld.time_bucket
                ORDER BY ts.time_bucket
            """)
            
            # 准备查询参数
            query_params = {
                'namespace': namespace,
                'start_time': start_time,
                'end_time': end_time,
                'interval_val': interval,
                **queue_params
            }
            
            print(f'🔍 Dashboard Overview - 最终查询参数: {query_params}')
            
            result = await session.execute(sql, query_params)
            
            
            # 格式化数据，按业务分组
            task_trend = []
            concurrency = []
            processing_time = []
            creation_latency = []
            
            rows = result.fetchall()
            end_index = len(rows) - 1
            
            for idx, row in enumerate(rows):
                time_str = row.time_bucket.isoformat()
                
                # 任务处理趋势数据
                enqueued_val = row.enqueued if row.enqueued > 0 or idx == 0 or idx == end_index else None
                completed_val = row.completed if row.completed > 0 or idx == 0 or idx == end_index else None
                failed_val = row.failed if row.failed > 0 or idx == 0 or idx == end_index else None
                
                task_trend.extend([
                    {'time': time_str, 'value': enqueued_val, 'metric': '入队速率'},
                    {'time': time_str, 'value': completed_val, 'metric': '完成速率'},
                    {'time': time_str, 'value': failed_val, 'metric': '失败数'}
                ])
                
                # 任务并发数量 - 直接显示计算的并发数（包括0）
                concurrent_val = row.concurrent_tasks or 0
                
                concurrency.append({
                    'time': time_str,
                    'value': concurrent_val,
                    'metric': '并发任务数'
                })
                
                # 任务处理时间（转换为毫秒）
                if row.avg_processing_time is not None:
                    avg_time_val = round(float(row.avg_processing_time * 1000), 1)
                else:
                    avg_time_val = None if idx != 0 and idx != end_index else 0
                    
                if row.p50_processing_time is not None:
                    p50_time_val = round(float(row.p50_processing_time * 1000), 1)
                else:
                    p50_time_val = None if idx != 0 and idx != end_index else 0
                    
                if row.p90_processing_time is not None:
                    p90_time_val = round(float(row.p90_processing_time * 1000), 1)
                else:
                    p90_time_val = None if idx != 0 and idx != end_index else 0
                
                processing_time.extend([
                    {'time': time_str, 'value': avg_time_val, 'metric': '平均处理时间'},
                    {'time': time_str, 'value': p50_time_val, 'metric': 'P50处理时间'},
                    {'time': time_str, 'value': p90_time_val, 'metric': 'P90处理时间'}
                ])
                
                # 任务执行延时（秒）
                if row.avg_creation_latency is not None:
                    avg_latency_val = round(float(row.avg_creation_latency), 3)
                else:
                    avg_latency_val = None if idx != 0 and idx != end_index else 0
                    
                if row.p50_creation_latency is not None:
                    p50_latency_val = round(float(row.p50_creation_latency), 3)
                else:
                    p50_latency_val = None if idx != 0 and idx != end_index else 0
                    
                if row.p90_creation_latency is not None:
                    p90_latency_val = round(float(row.p90_creation_latency), 3)
                else:
                    p90_latency_val = None if idx != 0 and idx != end_index else 0
                
                creation_latency.extend([
                    {'time': time_str, 'value': avg_latency_val, 'metric': '平均执行延时'},
                    {'time': time_str, 'value': p50_latency_val, 'metric': 'P50执行延时'},
                    {'time': time_str, 'value': p90_latency_val, 'metric': 'P90执行延时'}
                ])
            
            total_data_points = len(task_trend) + len(concurrency) + len(processing_time) + len(creation_latency)
            logger.info(f"获取到 {total_data_points} 条概览统计数据，粒度: {granularity}")
            
            return {
                "task_trend": task_trend,
                "concurrency": concurrency,  
                "processing_time": processing_time,
                "creation_latency": creation_latency,
                "granularity": granularity
            }
    
    except Exception as e:
        logger.error(f"获取概览统计数据失败: {e}")
        traceback.print_exc()
        return {
            "task_trend": [],
            "concurrency": [],
            "processing_time": [],
            "creation_latency": [],
            "granularity": "minute"
        }


@router.get("/task-processing-time-trend/{namespace}")
async def get_task_processing_time_trend(
    namespace: str,
    time_range: str = "24h"
):
    """
    获取任务处理时间趋势数据（用于时间序列图表）
    
    Args:
        namespace: 命名空间名称
        time_range: 时间范围（如'1h', '24h', '7d'）
    
    Returns:
        按时间间隔分组的处理时间统计（平均值、P50、P90等）
    """
    try:
        conn = await data_access.manager.get_connection(namespace)
        
        # 如果没有PostgreSQL配置，返回空数据
        if not conn.pg_config:
            return {
                "success": True,
                "data": []
            }
        
        # 计算时间范围和间隔
        end_time = datetime.now(timezone.utc)
        interval = "15 minutes"  # 默认15分钟间隔
        
        if time_range.endswith('m'):
            minutes = int(time_range[:-1])
            start_time = end_time - timedelta(minutes=minutes)
            if minutes <= 60:
                interval = "5 minutes"
            elif minutes <= 240:
                interval = "15 minutes" 
            else:
                interval = "1 hour"
        elif time_range.endswith('h'):
            hours = int(time_range[:-1])
            start_time = end_time - timedelta(hours=hours)
            if hours <= 6:
                interval = "15 minutes"
            elif hours <= 24:
                interval = "1 hour"
            else:
                interval = "4 hours"
        elif time_range.endswith('d'):
            days = int(time_range[:-1])
            start_time = end_time - timedelta(days=days)
            if days <= 1:
                interval = "1 hour"
            elif days <= 7:
                interval = "4 hours"
            else:
                interval = "1 day"
        else:
            start_time = end_time - timedelta(hours=24)  # 默认24小时
            interval = "1 hour"
        
        async with await conn.get_pg_session() as session:
            # 首先检查execution_time的样本数据
            sample_sql = text("""
                SELECT 
                    tr.execution_time,
                    tr.duration,
                    tr.start_time,
                    tr.end_time,
                    t.queue
                FROM task_runs tr
                JOIN tasks t ON tr.stream_id = t.stream_id
                WHERE t.namespace = :namespace
                    AND tr.end_time >= :start_time
                    AND tr.end_time <= :end_time
                    AND tr.status = 'success'
                    AND (tr.execution_time IS NOT NULL OR tr.duration IS NOT NULL)
                ORDER BY tr.end_time DESC
                LIMIT 10
            """)
            
            sample_result = await session.execute(sample_sql, {
                'namespace': namespace,
                'start_time': start_time,
                'end_time': end_time
            })
            
            logger.info("=== 样本execution_time数据 ===")
            for sample_row in sample_result:
                logger.info(f"execution_time={sample_row.execution_time}, duration={sample_row.duration}, "
                           f"queue={sample_row.queue}, start_time={sample_row.start_time}, end_time={sample_row.end_time}")
            
            # 查询处理时间趋势数据 - 使用duration字段如果execution_time为空
            sql = text("""
                WITH processing_stats AS (
                    SELECT 
                        date_trunc('hour', tr.end_time) as time_bucket,
                        COALESCE(tr.execution_time, tr.duration) as processing_time,
                        t.queue
                    FROM task_runs tr
                    JOIN tasks t ON tr.stream_id = t.stream_id
                    WHERE t.namespace = :namespace
                        AND tr.end_time >= :start_time
                        AND tr.end_time <= :end_time
                        AND tr.status = 'success'
                        AND (tr.execution_time IS NOT NULL OR tr.duration IS NOT NULL)
                        AND COALESCE(tr.execution_time, tr.duration) > 0
                )
                SELECT 
                    ps.time_bucket,
                    COUNT(ps.processing_time) as task_count,
                    ROUND(AVG(ps.processing_time)::numeric, 6) as avg_processing_time,
                    ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ps.processing_time)::numeric, 6) as p50_processing_time,
                    ROUND(PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY ps.processing_time)::numeric, 6) as p90_processing_time,
                    ROUND(MIN(ps.processing_time)::numeric, 6) as min_processing_time,
                    ROUND(MAX(ps.processing_time)::numeric, 6) as max_processing_time
                FROM processing_stats ps
                GROUP BY ps.time_bucket
                ORDER BY ps.time_bucket
            """)
            
            result = await session.execute(sql, {
                'namespace': namespace,
                'start_time': start_time,
                'end_time': end_time
            })
            
            data = []
            for row in result:
                # 调试日志
                logger.info(f"处理时间数据行: time_bucket={row.time_bucket}, task_count={row.task_count}, "
                           f"avg_processing_time={row.avg_processing_time}, "
                           f"p50_processing_time={row.p50_processing_time}, "
                           f"p90_processing_time={row.p90_processing_time}")
                
                # 将处理时间从秒转换为毫秒
                data.append({
                    'time': row.time_bucket.isoformat() if row.time_bucket else None,
                    'metric': '平均处理时间',
                    'value': round(float(row.avg_processing_time * 1000), 1) if row.avg_processing_time else 0,
                    'queue': 'all',
                    'task_count': row.task_count or 0
                })
                data.append({
                    'time': row.time_bucket.isoformat() if row.time_bucket else None,
                    'metric': 'P50处理时间',
                    'value': round(float(row.p50_processing_time * 1000), 1) if row.p50_processing_time else 0,
                    'queue': 'all',
                    'task_count': row.task_count or 0
                })
                data.append({
                    'time': row.time_bucket.isoformat() if row.time_bucket else None,
                    'metric': 'P90处理时间',
                    'value': round(float(row.p90_processing_time * 1000), 1) if row.p90_processing_time else 0,
                    'queue': 'all', 
                    'task_count': row.task_count or 0
                })
            
            logger.info(f"获取到 {len(data)} 条处理时间趋势数据")
            
            return {
                "success": True,
                "data": data,
                "time_range": time_range,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat()
            }
    
    except Exception as e:
        logger.error(f"获取任务处理时间趋势数据失败: {e}")
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "data": []
        }


@router.get("/task-status-distribution/{namespace}")
async def get_task_status_distribution(
    namespace: str, 
    time_range: str = "24h",
    queues: Optional[str] = Query(None, description="逗号分隔的队列名称列表")
):
    """
    获取任务状态分布数据，按队列分组统计
    
    Args:
        namespace: 命名空间名称
        time_range: 时间范围（如'1h', '24h', '7d'）
    
    Returns:
        按队列分组的任务状态分布数据，用于饼图展示
    """
    try:
        conn = await data_access.manager.get_connection(namespace)
        
        if not conn.pg_config:
            return {"data": []}
        
        # 计算时间范围
        end_time = datetime.now(timezone.utc)
        if time_range.endswith('m'):
            minutes = int(time_range[:-1])
            start_time = end_time - timedelta(minutes=minutes)
        elif time_range.endswith('h'):
            hours = int(time_range[:-1])
            start_time = end_time - timedelta(hours=hours)
        elif time_range.endswith('d'):
            days = int(time_range[:-1])
            start_time = end_time - timedelta(days=days)
        else:
            start_time = end_time - timedelta(hours=24)
        
        # 解析队列列表
        queue_list = []
        if queues:
            queue_list = [q.strip() for q in queues.split(',') if q.strip()]
        
        async with await conn.get_pg_session() as session:
            # 构建队列筛选条件
            queue_filter = ""
            if queue_list:
                queue_placeholders = ','.join([f':queue_{i}' for i in range(len(queue_list))])
                queue_filter = f"AND t.queue IN ({queue_placeholders})"
            
            # 查询任务状态分布数据
            distribution_sql = text(f"""
                SELECT 
                    t.queue,
                    tr.status,
                    COUNT(*) as count
                FROM task_runs tr
                JOIN tasks t ON tr.stream_id = t.stream_id
                WHERE t.namespace = :namespace
                    AND tr.end_time >= :start_time
                    AND tr.end_time <= :end_time
                    AND tr.status IS NOT NULL
                    {queue_filter}
                GROUP BY t.queue, tr.status
                ORDER BY t.queue, tr.status
            """)
            
            # 准备查询参数
            query_params = {
                'namespace': namespace,
                'start_time': start_time,
                'end_time': end_time
            }
            
            # 添加队列参数
            for i, queue in enumerate(queue_list):
                query_params[f'queue_{i}'] = queue
            
            result = await session.execute(distribution_sql, query_params)
            
            # 处理数据，按队列分组
            queue_data = {}
            total_by_status = {}
            
            for row in result.fetchall():
                queue = row.queue
                status = row.status
                count = row.count
                
                # 按队列统计
                if queue not in queue_data:
                    queue_data[queue] = {'success': 0, 'error': 0, 'timeout': 0}
                
                if status == 'success':
                    queue_data[queue]['success'] += count
                elif status == 'error':
                    queue_data[queue]['error'] += count
                elif status == 'timeout':
                    queue_data[queue]['timeout'] += count
                
                # 按状态统计总数
                if status not in total_by_status:
                    total_by_status[status] = 0
                total_by_status[status] += count
            
            # 格式化数据为饼图格式
            data = []
            
            # 方案1: 按队列分组显示
            for queue, counts in queue_data.items():
                total_queue = counts['success'] + counts['error'] + counts['timeout']
                if total_queue > 0:
                    data.append({
                        'type': f'{queue} (成功)',
                        'value': counts['success'],
                        'queue': queue,
                        'status': 'success'
                    })
                    if counts['error'] > 0:
                        data.append({
                            'type': f'{queue} (失败)',
                            'value': counts['error'],
                            'queue': queue,
                            'status': 'error'
                        })
                    if counts['timeout'] > 0:
                        data.append({
                            'type': f'{queue} (超时)',
                            'value': counts['timeout'],
                            'queue': queue,
                            'status': 'timeout'
                        })
            
            # 如果没有数据，返回默认值
            if not data:
                data = [
                    {'type': '暂无数据', 'value': 1, 'queue': '', 'status': 'empty'}
                ]
            
            return {"data": data}
            
    except Exception as e:
        logger.error(f"获取任务状态分布失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))