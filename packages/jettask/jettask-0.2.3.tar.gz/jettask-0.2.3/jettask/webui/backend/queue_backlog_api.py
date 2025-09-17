"""
队列积压监控API接口
从stream_backlog_monitor表读取历史积压数据
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel
import asyncpg
import os
from contextlib import asynccontextmanager
import traceback

router = APIRouter(prefix="/api/queue-backlog", tags=["queue-backlog"])


class BacklogTrendRequest(BaseModel):
    """积压趋势请求参数"""
    namespace: str = "default"
    queues: Optional[List[str]] = None  # None表示所有队列
    time_range: str = "1h"  # 15m, 30m, 1h, 3h, 6h, 12h, 24h, 3d, 7d
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    granularity: Optional[str] = None  # auto, minute, 5minute, 10minute, 30minute, hour, day
    include_groups: bool = False  # 是否包含消费组级别的数据


class BacklogSnapshot(BaseModel):
    """积压快照"""
    namespace: str
    queue_name: str
    consumer_group: Optional[str]
    timestamp: datetime
    last_published_offset: int
    last_delivered_offset: int
    last_acked_offset: int
    pending_count: int
    backlog_undelivered: int
    backlog_unprocessed: int
    produce_rate: Optional[float]
    deliver_rate: Optional[float]
    ack_rate: Optional[float]


class BacklogStatistics(BaseModel):
    """积压统计信息"""
    queue_name: str
    current_backlog: int
    max_backlog: int
    avg_backlog: float
    min_backlog: int
    trend: str  # up, down, stable
    trend_percentage: float
    alert_level: Optional[str]  # normal, warning, critical


class BacklogTrendResponse(BaseModel):
    """积压趋势响应"""
    success: bool
    data: List[Dict[str, Any]]
    statistics: List[BacklogStatistics]
    granularity: str
    time_range: Dict[str, datetime]


# 数据库连接池
_db_pool = None


async def get_db_pool():
    """获取数据库连接池"""
    global _db_pool
    if _db_pool is None:
        pg_url = os.getenv('JETTASK_PG_URL', 'postgresql://jettask:123456@localhost:5432/jettask')
        # 解析连接字符串
        if pg_url.startswith('postgresql://'):
            pg_url = pg_url.replace('postgresql://', '')
        elif pg_url.startswith('postgresql+asyncpg://'):
            pg_url = pg_url.replace('postgresql+asyncpg://', '')
        
        # 分离用户名密码和主机信息
        if '@' in pg_url:
            auth, host_info = pg_url.split('@')
            if ':' in auth:
                user, password = auth.split(':')
            else:
                user = auth
                password = None
            
            if '/' in host_info:
                host_port, database = host_info.split('/')
                if ':' in host_port:
                    host, port = host_port.split(':')
                    port = int(port)
                else:
                    host = host_port
                    port = 5432
            else:
                host = host_info
                port = 5432
                database = 'jettask'
        else:
            user = 'jettask'
            password = '123456'
            host = 'localhost'
            port = 5432
            database = 'jettask'
        
        _db_pool = await asyncpg.create_pool(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            min_size=2,
            max_size=10
        )
    return _db_pool


def parse_time_range(time_range: str) -> timedelta:
    """解析时间范围字符串"""
    time_map = {
        '15m': timedelta(minutes=15),
        '30m': timedelta(minutes=30),
        '1h': timedelta(hours=1),
        '3h': timedelta(hours=3),
        '6h': timedelta(hours=6),
        '12h': timedelta(hours=12),
        '24h': timedelta(hours=24),
        '1d': timedelta(days=1),
        '3d': timedelta(days=3),
        '7d': timedelta(days=7),
    }
    return time_map.get(time_range, timedelta(hours=1))


def determine_granularity(time_delta: timedelta, granularity: Optional[str] = None) -> tuple[str, int]:
    """根据时间范围确定合适的数据粒度（参考fetch_queue_flow_rates的实现）
    
    Returns:
        (granularity_name, interval_seconds)
    """
    if granularity and granularity != 'auto':
        # 手动指定粒度时的秒数映射
        manual_map = {
            'second': ('second', 1),
            'minute': ('minute', 60),
            '5minute': ('5minute', 300),
            '10minute': ('10minute', 600),
            '30minute': ('30minute', 1800),
            'hour': ('hour', 3600),
            'day': ('day', 86400),
        }
        return manual_map.get(granularity, ('minute', 60))
    
    # 根据时间范围选择合适的粒度
    # 目标：保持合理的数据点数量，避免过多或过少
    duration_seconds = time_delta.total_seconds()
    duration_minutes = duration_seconds / 60
    duration_hours = duration_minutes / 60
    duration_days = duration_hours / 24
    
    # 根据时间范围选择粒度
    if duration_minutes <= 15:
        # 15分钟以内：5秒粒度（最多180个点）
        return ('second', 5)
    elif duration_minutes <= 30:
        # 30分钟以内：10秒粒度（最多180个点）
        return ('second', 10)
    elif duration_hours <= 1:
        # 1小时以内：30秒粒度（最多120个点）
        return ('second', 30)
    elif duration_hours <= 3:
        # 3小时以内：1分钟粒度（最多180个点）
        return ('minute', 60)
    elif duration_hours <= 6:
        # 6小时以内：2分钟粒度（最多180个点）
        return ('minute', 120)
    elif duration_hours <= 12:
        # 12小时以内：5分钟粒度（最多144个点）
        return ('5minute', 300)
    elif duration_hours <= 24:
        # 24小时以内：10分钟粒度（最多144个点）
        return ('10minute', 600)
    elif duration_days <= 3:
        # 3天以内：30分钟粒度（最多144个点）
        return ('30minute', 1800)
    elif duration_days <= 7:
        # 7天以内：1小时粒度（最多168个点）
        return ('hour', 3600)
    elif duration_days <= 30:
        # 30天以内：4小时粒度（最多180个点）
        return ('hour', 14400)
    else:
        # 超过30天：1天粒度
        return ('day', 86400)


def get_time_bucket_sql(granularity: str, interval_seconds: int) -> str:
    """获取时间分组的SQL表达式（改进版，支持更多粒度）"""
    
    # 对于秒级粒度
    if granularity == 'second':
        if interval_seconds == 1:
            return "date_trunc('second', created_at)"
        else:
            # 5秒、10秒、30秒等 - 修正算法
            return f"date_trunc('minute', created_at) + interval '{interval_seconds} seconds' * floor(extract(second from created_at)::int / {interval_seconds})"
    
    # 对于分钟级粒度
    elif granularity == 'minute':
        if interval_seconds == 60:
            return "date_trunc('minute', created_at)"
        elif interval_seconds == 120:
            return "date_trunc('hour', created_at) + interval '2 minutes' * floor(extract(minute from created_at)::int / 2)"
        else:
            # 其他分钟间隔
            minutes = interval_seconds // 60
            return f"date_trunc('hour', created_at) + interval '{minutes} minutes' * floor(extract(minute from created_at)::int / {minutes})"
    
    # 特定的分钟粒度
    elif granularity == '5minute':
        return "date_trunc('hour', created_at) + interval '5 minutes' * floor(extract(minute from created_at)::int / 5)"
    elif granularity == '10minute':
        return "date_trunc('hour', created_at) + interval '10 minutes' * floor(extract(minute from created_at)::int / 10)"
    elif granularity == '15minute':
        return "date_trunc('hour', created_at) + interval '15 minutes' * floor(extract(minute from created_at)::int / 15)"
    elif granularity == '30minute':
        return "date_trunc('hour', created_at) + interval '30 minutes' * floor(extract(minute from created_at)::int / 30)"
    
    # 小时级粒度
    elif granularity == 'hour':
        if interval_seconds == 3600:
            return "date_trunc('hour', created_at)"
        else:
            # 2小时、4小时、6小时、12小时等
            hours = interval_seconds // 3600
            return f"date_trunc('day', created_at) + interval '{hours} hours' * floor(extract(hour from created_at)::int / {hours})"
    
    # 天级粒度
    elif granularity == 'day':
        return "date_trunc('day', created_at)"
    
    # 默认值
    else:
        return "date_trunc('minute', created_at)"


@router.post("/trend", response_model=BacklogTrendResponse)
async def get_backlog_trend(request: BacklogTrendRequest):
    """
    获取队列积压趋势数据
    
    支持多种时间范围和数据粒度，自动聚合数据点
    """
    pool = await get_db_pool()
    
    # 确定时间范围
    if request.start_time and request.end_time:
        start_time = request.start_time
        end_time = request.end_time
        time_delta = end_time - start_time
    else:
        time_delta = parse_time_range(request.time_range)
        end_time = datetime.now(timezone.utc)
        start_time = end_time - time_delta
    
    # 确定数据粒度和间隔
    granularity_name, interval_seconds = determine_granularity(time_delta, request.granularity)
    time_bucket = get_time_bucket_sql(granularity_name, interval_seconds)
    
    # 记录日志
    actual_points = int(time_delta.total_seconds() / interval_seconds) + 1
    print(f"使用时间间隔: {interval_seconds}秒 ({granularity_name}), 预计生成 {actual_points} 个时间点")
    
    async with pool.acquire() as conn:
        # 构建查询条件
        conditions = [
            "namespace = $1",
            "created_at >= $2",
            "created_at <= $3"
        ]
        params = [request.namespace, start_time, end_time]
        
        # 添加队列筛选
        if request.queues:
            placeholders = [f"${i+4}" for i in range(len(request.queues))]
            conditions.append(f"stream_name IN ({','.join(placeholders)})")
            params.extend(request.queues)
        
        # 添加消费组筛选
        # if not request.include_groups:
        #     # 不包含消费组数据时，只查询整体Stream的统计（consumer_group为NULL）
        #     conditions.append("consumer_group IS NULL")
        
        where_clause = " AND ".join(conditions)
        
        # 根据是否包含groups构建不同的查询
        if request.include_groups:
            # 按任务名称聚合数据，但确保每个时间点只有一条记录
            # 从consumer_group中提取任务名称（最后一个点号后的部分）
            query = f"""
            WITH raw_data AS (
                SELECT 
                    {time_bucket} as time_bucket,
                    stream_name as queue_name,
                    consumer_group,
                    CASE 
                        -- 处理 default:QUEUE:queue_name:task.subtask 格式
                        WHEN consumer_group LIKE 'default:QUEUE:%' THEN 
                            SPLIT_PART(consumer_group, '.', -1)  -- 取最后一个点号后的部分
                        -- 保留原始的消费组名称（如 consumer_group_1）
                        ELSE consumer_group
                    END as task_name,
                    backlog_unprocessed,
                    last_published_offset,
                    last_delivered_offset,
                    pending_count,
                    produce_rate,
                    deliver_rate
                FROM stream_backlog_monitor
                WHERE {where_clause}
                    AND consumer_group != 'default_pg_consumer'  -- 屏蔽 default_pg_consumer
                    AND consumer_group IS NOT NULL  -- 确保有消费组
            ),
            task_aggregated AS (
                SELECT 
                    time_bucket,
                    queue_name,
                    task_name,
                    SUM(backlog_unprocessed) as total_backlog,
                    MAX(backlog_unprocessed) as max_backlog,
                    MIN(backlog_unprocessed) as min_backlog,
                    MAX(last_published_offset) as max_published,
                    MAX(last_delivered_offset) as max_delivered,
                    SUM(pending_count) as total_pending,
                    AVG(produce_rate) as avg_produce_rate,
                    AVG(deliver_rate) as avg_deliver_rate,
                    COUNT(DISTINCT consumer_group) as sample_count
                FROM raw_data
                GROUP BY time_bucket, queue_name, task_name
            )
            SELECT 
                time_bucket,
                queue_name,
                task_name as consumer_group,  -- 使用task_name作为consumer_group返回
                total_backlog::int as avg_backlog,
                max_backlog,
                min_backlog,
                max_published::int as avg_published,
                max_delivered::int as avg_delivered,
                total_pending::int as avg_pending,
                avg_produce_rate,
                avg_deliver_rate,
                sample_count
            FROM task_aggregated
            ORDER BY time_bucket, queue_name, task_name
            """
        else:
            # 不包含消费组，聚合所有消费组和优先级的数据
            query = f"""
            SELECT 
                {time_bucket} as time_bucket,
                stream_name as queue_name,
                NULL as consumer_group,
                COALESCE(SUM(backlog_unprocessed), 0)::int as avg_backlog,
                COALESCE(MAX(backlog_unprocessed), 0)::int as max_backlog,
                COALESCE(MIN(backlog_unprocessed), 0)::int as min_backlog,
                COALESCE(MAX(last_published_offset), 0)::int as avg_published,
                COALESCE(MAX(last_delivered_offset), 0)::int as avg_delivered,
                COALESCE(SUM(pending_count), 0)::int as avg_pending,
                AVG(produce_rate) as avg_produce_rate,
                AVG(deliver_rate) as avg_deliver_rate,
                COUNT(DISTINCT COALESCE(priority::text, '0') || ':' || COALESCE(consumer_group, 'null')) as sample_count
            FROM stream_backlog_monitor
            WHERE {where_clause}
            GROUP BY time_bucket, stream_name
            ORDER BY time_bucket, stream_name
            """
        
        rows = await conn.fetch(query, *params)
        
        # 查询统计信息
        if request.include_groups:
            # 包含消费组的统计
            stats_query = f"""
            WITH latest_data AS (
                SELECT DISTINCT ON (stream_name, consumer_group)
                    stream_name,
                    consumer_group,
                    backlog_unprocessed as current_backlog,
                    created_at
                FROM stream_backlog_monitor
                WHERE {where_clause}
                ORDER BY stream_name, consumer_group, created_at DESC
            ),
            stats AS (
                SELECT 
                    stream_name,
                    AVG(backlog_unprocessed) as avg_backlog,
                    MAX(backlog_unprocessed) as max_backlog,
                    MIN(backlog_unprocessed) as min_backlog
                FROM stream_backlog_monitor
                WHERE {where_clause}
                GROUP BY stream_name
            ),
            trend AS (
                SELECT 
                    stream_name,
                    CASE 
                        WHEN COUNT(*) >= 2 THEN
                            (AVG(CASE WHEN row_num <= 5 THEN backlog_unprocessed END) - 
                             AVG(CASE WHEN row_num > count_all - 5 THEN backlog_unprocessed END))
                        ELSE 0
                    END as trend_diff
                FROM (
                    SELECT 
                        stream_name,
                        backlog_unprocessed,
                        ROW_NUMBER() OVER (PARTITION BY stream_name ORDER BY created_at DESC) as row_num,
                        COUNT(*) OVER (PARTITION BY stream_name) as count_all
                    FROM stream_backlog_monitor
                    WHERE {where_clause} AND consumer_group IS NULL
                ) t
                GROUP BY stream_name
            )
            SELECT 
                s.stream_name,
                l.current_backlog,
                s.max_backlog,
                s.avg_backlog,
                s.min_backlog,
                COALESCE(t.trend_diff, 0) as trend_diff
            FROM stats s
            JOIN latest_data l ON s.stream_name = l.stream_name
            LEFT JOIN trend t ON s.stream_name = t.stream_name
            WHERE l.consumer_group IS NULL
            """
        else:
            # 不包含消费组，聚合所有消费组和优先级的统计
            stats_query = f"""
            WITH latest_per_priority AS (
                SELECT DISTINCT ON (stream_name, priority, consumer_group)
                    stream_name,
                    priority,
                    consumer_group,
                    backlog_unprocessed,
                    created_at
                FROM stream_backlog_monitor
                WHERE {where_clause}
                ORDER BY stream_name, priority, consumer_group, created_at DESC
            ),
            latest_data AS (
                SELECT 
                    stream_name,
                    SUM(backlog_unprocessed) as current_backlog,
                    MAX(created_at) as latest_time
                FROM latest_per_priority
                GROUP BY stream_name
            ),
            stats AS (
                SELECT 
                    stream_name,
                    AVG(backlog_unprocessed) as avg_backlog,
                    MAX(backlog_unprocessed) as max_backlog,
                    MIN(backlog_unprocessed) as min_backlog
                FROM stream_backlog_monitor
                WHERE {where_clause}
                GROUP BY stream_name
            ),
            trend AS (
                SELECT 
                    stream_name,
                    CASE 
                        WHEN COUNT(DISTINCT time_bucket) >= 2 THEN
                            (AVG(CASE WHEN row_num <= 5 THEN total_backlog END) - 
                             AVG(CASE WHEN row_num > count_all - 5 THEN total_backlog END))
                        ELSE 0
                    END as trend_diff
                FROM (
                    SELECT 
                        stream_name,
                        {time_bucket} as time_bucket,
                        SUM(backlog_unprocessed) as total_backlog,
                        ROW_NUMBER() OVER (PARTITION BY stream_name ORDER BY {time_bucket} DESC) as row_num,
                        COUNT(*) OVER (PARTITION BY stream_name) as count_all
                    FROM stream_backlog_monitor
                    WHERE {where_clause}
                    GROUP BY stream_name, {time_bucket}
                ) t
                GROUP BY stream_name
            )
            SELECT 
                s.stream_name,
                l.current_backlog,
                s.max_backlog,
                s.avg_backlog,
                s.min_backlog,
                COALESCE(t.trend_diff, 0) as trend_diff
            FROM stats s
            JOIN latest_data l ON s.stream_name = l.stream_name
            LEFT JOIN trend t ON s.stream_name = t.stream_name
            """
        
        stats_rows = await conn.fetch(stats_query, *params)
    
    # 转换数据格式
    data = []
    for row in rows:
        data_item = {
            'time': row['time_bucket'].isoformat(),
            'queue': row['queue_name'],
            'group': row['consumer_group'],
            'backlog': row['avg_backlog'],
            'max_backlog': row['max_backlog'],
            'min_backlog': row['min_backlog'],
            'published': row['avg_published'],
            'delivered': row['avg_delivered'],
            'pending': row['avg_pending'],
            'produce_rate': row['avg_produce_rate'],
            'deliver_rate': row['avg_deliver_rate'],
        }
        # 注意：现在聚合了优先级，不再返回priority字段
        data.append(data_item)
    
    # 生成统计信息
    statistics = []
    for stat_row in stats_rows:
        # 计算趋势
        trend_diff = stat_row['trend_diff'] or 0
        avg_backlog = stat_row['avg_backlog'] or 1
        trend_percentage = (trend_diff / avg_backlog * 100) if avg_backlog > 0 else 0
        
        if trend_percentage > 20:
            trend = 'up'
        elif trend_percentage < -20:
            trend = 'down'
        else:
            trend = 'stable'
        
        # 确定告警级别
        current = stat_row['current_backlog'] or 0
        if current >= 5000:
            alert_level = 'critical'
        elif current >= 1000:
            alert_level = 'warning'
        else:
            alert_level = 'normal'
        
        statistics.append(BacklogStatistics(
            queue_name=stat_row['stream_name'],
            current_backlog=current,
            max_backlog=stat_row['max_backlog'] or 0,
            avg_backlog=float(stat_row['avg_backlog'] or 0),
            min_backlog=stat_row['min_backlog'] or 0,
            trend=trend,
            trend_percentage=trend_percentage,
            alert_level=alert_level
        ))
    
    return BacklogTrendResponse(
        success=True,
        data=data,
        statistics=statistics,
        granularity=granularity_name,  # 使用granularity_name而不是granularity
        time_range={
            'start': start_time,
            'end': end_time
        }
    )


@router.get("/current", response_model=Dict[str, Any])
async def get_current_backlog(
    namespace: str = Query("default", description="命名空间"),
    queue: Optional[str] = Query(None, description="队列名称"),
    include_groups: bool = Query(False, description="是否包含消费组数据")
):
    """
    获取当前队列积压状态（最新数据）
    """
    pool = await get_db_pool()
    
    async with pool.acquire() as conn:
        # 构建查询条件
        conditions = ["namespace = $1"]
        params = [namespace]
        
        if queue:
            conditions.append("stream_name = $2")
            params.append(queue)
        
        if not include_groups:
            conditions.append("consumer_group IS NULL")
        
        where_clause = " AND ".join(conditions)
        
        # 使用视图获取最新数据
        query = f"""
        SELECT DISTINCT ON (stream_name, consumer_group)
            namespace,
            stream_name,
            consumer_group,
            last_published_offset,
            last_delivered_offset,
            last_acked_offset,
            pending_count,
            backlog_undelivered,
            backlog_unprocessed,
            produce_rate,
            deliver_rate,
            ack_rate,
            created_at
        FROM stream_backlog_monitor
        WHERE {where_clause}
        ORDER BY stream_name, consumer_group, created_at DESC
        """
        
        rows = await conn.fetch(query, *params)
    
    # 按队列组织数据
    result = {}
    for row in rows:
        queue_name = row['stream_name']
        if queue_name not in result:
            result[queue_name] = {
                'queue_name': queue_name,
                'namespace': row['namespace'],
                'last_update': row['created_at'].isoformat(),
                'summary': None,
                'consumer_groups': []
            }
        
        data = {
            'consumer_group': row['consumer_group'],
            'last_published_offset': row['last_published_offset'],
            'last_delivered_offset': row['last_delivered_offset'],
            'last_acked_offset': row['last_acked_offset'],
            'pending_count': row['pending_count'],
            'backlog_undelivered': row['backlog_undelivered'],
            'backlog_unprocessed': row['backlog_unprocessed'],
            'produce_rate': row['produce_rate'],
            'deliver_rate': row['deliver_rate'],
            'ack_rate': row['ack_rate'],
        }
        
        if row['consumer_group'] is None:
            result[queue_name]['summary'] = data
        else:
            result[queue_name]['consumer_groups'].append(data)
    
    return {
        'success': True,
        'data': list(result.values())
    }


@router.get("/alert-queues", response_model=Dict[str, Any])
async def get_alert_queues(
    namespace: str = Query("default", description="命名空间"),
    warning_threshold: int = Query(1000, description="警告阈值"),
    critical_threshold: int = Query(5000, description="严重阈值")
):
    """
    获取需要告警的队列列表
    """
    pool = await get_db_pool()
    
    async with pool.acquire() as conn:
        query = """
        SELECT DISTINCT ON (stream_name)
            stream_name,
            backlog_unprocessed,
            produce_rate,
            deliver_rate,
            created_at
        FROM stream_backlog_monitor
        WHERE 
            namespace = $1 
            AND consumer_group IS NULL
            AND backlog_unprocessed >= $2
        ORDER BY stream_name, created_at DESC
        """
        
        rows = await conn.fetch(query, namespace, warning_threshold)
    
    # 分类告警
    alerts = {
        'critical': [],
        'warning': [],
    }
    
    for row in rows:
        alert_data = {
            'queue_name': row['stream_name'],
            'backlog': row['backlog_unprocessed'],
            'produce_rate': row['produce_rate'],
            'deliver_rate': row['deliver_rate'],
            'last_update': row['created_at'].isoformat()
        }
        
        if row['backlog_unprocessed'] >= critical_threshold:
            alerts['critical'].append(alert_data)
        else:
            alerts['warning'].append(alert_data)
    
    return {
        'success': True,
        'namespace': namespace,
        'thresholds': {
            'warning': warning_threshold,
            'critical': critical_threshold
        },
        'alerts': alerts,
        'total_alerts': len(alerts['critical']) + len(alerts['warning'])
    }


# 清理函数
async def cleanup():
    """清理资源"""
    global _db_pool
    if _db_pool:
        await _db_pool.close()
        _db_pool = None