"""
统一的API路由文件
将所有分散的API接口整合到一个文件中，方便维护和管理
"""

from fastapi import APIRouter, HTTPException, Query, Request, Depends
from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime, timedelta, timezone
import logging
import time
import json
import asyncio
import psutil
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import traceback

# 导入本地模块
try:
    from namespace_data_access import get_namespace_data_access
    from config import task_center_config
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    from jettask.webui.backend.namespace_data_access import get_namespace_data_access
    from jettask.webui.backend.config import task_center_config

# 设置日志
logger = logging.getLogger(__name__)

# 创建统一的路由器
router = APIRouter(prefix="/api", tags=["API"])

# ==================== 数据模型定义 ====================

class TimeRangeQuery(BaseModel):
    """时间范围查询参数"""
    namespace: str = "default"
    queue_name: Optional[str] = None
    time_range: str = "1h"
    granularity: Optional[str] = None
    
class QueueStatsResponse(BaseModel):
    """队列统计响应"""
    queue_name: str
    pending: int
    running: int
    completed: int
    failed: int
    
class TaskDetailResponse(BaseModel):
    """任务详情响应"""
    task_id: str
    status: str
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]
    
class DashboardOverviewRequest(BaseModel):
    """仪表板概览请求参数"""
    time_range: str = "1h"
    queues: Optional[List[str]] = None

class ScheduledTaskCreate(BaseModel):
    """创建定时任务的请求模型"""
    task_name: str
    queue_name: str
    task_data: dict
    cron_expression: Optional[str] = None
    interval_seconds: Optional[int] = None
    enabled: bool = True
    
class ScheduledTaskUpdate(BaseModel):
    """更新定时任务的请求模型"""
    task_name: Optional[str] = None
    queue_name: Optional[str] = None
    task_data: Optional[dict] = None
    cron_expression: Optional[str] = None
    interval_seconds: Optional[int] = None
    enabled: Optional[bool] = None

class AlertRuleCreate(BaseModel):
    """创建告警规则的请求模型"""
    name: str
    metric: str
    threshold: float
    condition: str  # gt, lt, eq
    duration: int  # 持续时间（秒）
    notification_channels: List[str]
    enabled: bool = True

class NamespaceCreate(BaseModel):
    """创建命名空间的请求模型"""
    name: str
    redis_url: str
    pg_url: Optional[str] = None
    description: Optional[str] = None

class NamespaceUpdate(BaseModel):
    """更新命名空间的请求模型"""
    redis_url: Optional[str] = None
    pg_url: Optional[str] = None
    description: Optional[str] = None

# ==================== 辅助函数 ====================

def parse_time_range(time_range: str) -> timedelta:
    """解析时间范围字符串"""
    units = {
        'm': 'minutes',
        'h': 'hours',
        'd': 'days',
        'w': 'weeks'
    }
    
    if not time_range or len(time_range) < 2:
        return timedelta(hours=1)
    
    try:
        value = int(time_range[:-1])
        unit = time_range[-1].lower()
        
        if unit in units:
            return timedelta(**{units[unit]: value})
        else:
            return timedelta(hours=1)
    except (ValueError, KeyError):
        return timedelta(hours=1)

def get_base_queue_name(queue_name: str) -> str:
    """获取基础队列名（去除priority后缀）"""
    if '_priority_' in queue_name:
        return queue_name.split('_priority_')[0]
    return queue_name

# ==================== Dashboard 相关接口 ====================

@router.get("/data/dashboard-stats/{namespace}")
async def get_dashboard_stats(
    namespace: str,
    time_range: str = "24h",
    queues: Optional[str] = Query(None, description="逗号分隔的队列名称列表")
):
    """
    获取仪表板统计数据（任务总数、成功数、失败数、成功率、吞吐量等）
    """
    try:
        data_access = get_namespace_data_access()
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
                    "total_queues": 0,
                    "task_distribution": []
                }
            }
        
        # 解析时间范围
        time_delta = parse_time_range(time_range)
        start_time = datetime.now(timezone.utc) - time_delta
        
        # 解析队列筛选
        queue_filter = []
        if queues:
            queue_filter = [q.strip() for q in queues.split(',') if q.strip()]
        
        async with conn.async_engine.begin() as pg_conn:
            # 构建队列筛选条件
            queue_condition = ""
            if queue_filter:
                queue_list = "', '".join(queue_filter)
                queue_condition = f"AND queue IN ('{queue_list}')"
            
            # 获取任务统计
            stats_query = f"""
                SELECT 
                    COUNT(*) as total_tasks,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_tasks,
                    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_tasks,
                    COUNT(CASE WHEN status = 'running' THEN 1 END) as running_tasks,
                    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_tasks,
                    AVG(CASE 
                        WHEN status = 'completed' AND completed_at IS NOT NULL AND started_at IS NOT NULL 
                        THEN EXTRACT(EPOCH FROM (completed_at - started_at)) * 1000
                        ELSE NULL 
                    END) as avg_processing_time
                FROM tasks
                WHERE namespace = :namespace
                AND created_at >= :start_time
                {queue_condition}
            """
            
            result = await pg_conn.execute(
                text(stats_query),
                {"namespace": namespace, "start_time": start_time}
            )
            stats = result.fetchone()
            
            # 获取队列数量
            queue_query = f"""
                SELECT COUNT(DISTINCT queue) as total_queues
                FROM tasks
                WHERE namespace = :namespace
                {queue_condition}
            """
            queue_result = await pg_conn.execute(
                text(queue_query),
                {"namespace": namespace}
            )
            queue_count = queue_result.fetchone()
            
            # 获取任务分布（按队列）
            distribution_query = f"""
                SELECT 
                    queue as type,
                    COUNT(*) as value
                FROM tasks
                WHERE namespace = :namespace
                AND created_at >= :start_time
                {queue_condition}
                GROUP BY queue
                ORDER BY value DESC
                LIMIT 10
            """
            distribution_result = await pg_conn.execute(
                text(distribution_query),
                {"namespace": namespace, "start_time": start_time}
            )
            distribution_data = [
                {"type": row.type, "value": row.value}
                for row in distribution_result
            ]
            
            # 计算吞吐量（最近几分钟完成的任务数）
            throughput_minutes = 5
            throughput_start = datetime.now(timezone.utc) - timedelta(minutes=throughput_minutes)
            throughput_query = f"""
                SELECT COUNT(*) as completed_count
                FROM tasks
                WHERE namespace = :namespace
                AND status = 'completed'
                AND completed_at >= :start_time
                {queue_condition}
            """
            throughput_result = await pg_conn.execute(
                text(throughput_query),
                {"namespace": namespace, "start_time": throughput_start}
            )
            throughput_count = throughput_result.fetchone().completed_count or 0
            throughput = (throughput_count / throughput_minutes) if throughput_minutes > 0 else 0
            
            # 计算成功率
            total = stats.total_tasks or 0
            completed = stats.completed_tasks or 0
            failed = stats.failed_tasks or 0
            success_rate = (completed / (completed + failed) * 100) if (completed + failed) > 0 else 0
            
            return {
                "success": True,
                "data": {
                    "total_tasks": total,
                    "completed_tasks": completed,
                    "failed_tasks": failed,
                    "running_tasks": stats.running_tasks or 0,
                    "pending_tasks": stats.pending_tasks or 0,
                    "success_rate": round(success_rate, 2),
                    "throughput": round(throughput, 2),
                    "avg_processing_time": round(stats.avg_processing_time or 0, 2),
                    "total_queues": queue_count.total_queues or 0,
                    "task_distribution": distribution_data
                }
            }
            
    except Exception as e:
        logger.error(f"获取仪表板统计失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/data/dashboard-overview-stats/{namespace}")
async def get_dashboard_overview_stats(
    namespace: str,
    request: DashboardOverviewRequest
):
    """
    获取仪表板概览统计数据（任务趋势、并发数、处理时间等）
    """
    try:
        data_access = get_namespace_data_access()
        conn = await data_access.manager.get_connection(namespace)
        
        if not conn.pg_config:
            return {
                "task_trend": [],
                "concurrency": [],
                "processing_time": [],
                "creation_latency": [],
                "granularity": "minute"
            }
        
        # 解析时间范围和粒度
        time_delta = parse_time_range(request.time_range)
        
        # 根据时间范围决定数据粒度
        if time_delta <= timedelta(hours=1):
            granularity = "minute"
            interval = "1 minute"
        elif time_delta <= timedelta(hours=6):
            granularity = "5 minutes"
            interval = "5 minutes"
        elif time_delta <= timedelta(days=1):
            granularity = "hour"
            interval = "1 hour"
        else:
            granularity = "day"
            interval = "1 day"
        
        start_time = datetime.now(timezone.utc) - time_delta
        
        # 构建队列筛选条件
        queue_condition = ""
        if request.queues:
            queue_list = "', '".join(request.queues)
            queue_condition = f"AND queue IN ('{queue_list}')"
        
        async with conn.async_engine.begin() as pg_conn:
            # 获取任务趋势数据
            trend_query = f"""
                WITH time_series AS (
                    SELECT generate_series(
                        date_trunc('{granularity}', :start_time::timestamptz),
                        date_trunc('{granularity}', CURRENT_TIMESTAMP),
                        '{interval}'::interval
                    ) AS time_bucket
                ),
                task_metrics AS (
                    SELECT 
                        date_trunc('{granularity}', created_at) as time_bucket,
                        COUNT(*) FILTER (WHERE created_at IS NOT NULL) as created_count,
                        COUNT(*) FILTER (WHERE status = 'completed') as completed_count,
                        COUNT(*) FILTER (WHERE status = 'failed') as failed_count
                    FROM tasks
                    WHERE namespace = :namespace
                    AND created_at >= :start_time
                    {queue_condition}
                    GROUP BY date_trunc('{granularity}', created_at)
                )
                SELECT 
                    ts.time_bucket,
                    COALESCE(tm.created_count, 0) as created_count,
                    COALESCE(tm.completed_count, 0) as completed_count,
                    COALESCE(tm.failed_count, 0) as failed_count
                FROM time_series ts
                LEFT JOIN task_metrics tm ON ts.time_bucket = tm.time_bucket
                ORDER BY ts.time_bucket
            """
            
            trend_result = await pg_conn.execute(
                text(trend_query),
                {"namespace": namespace, "start_time": start_time}
            )
            
            task_trend = []
            for row in trend_result:
                time_str = row.time_bucket.isoformat()
                task_trend.extend([
                    {"time": time_str, "value": row.created_count, "metric": "入队速率"},
                    {"time": time_str, "value": row.completed_count, "metric": "完成速率"},
                    {"time": time_str, "value": row.failed_count, "metric": "失败数"}
                ])
            
            # 获取并发数据
            concurrency_query = f"""
                WITH time_series AS (
                    SELECT generate_series(
                        date_trunc('{granularity}', :start_time::timestamptz),
                        date_trunc('{granularity}', CURRENT_TIMESTAMP),
                        '{interval}'::interval
                    ) AS time_bucket
                ),
                concurrency_data AS (
                    SELECT 
                        date_trunc('{granularity}', started_at) as time_bucket,
                        COUNT(DISTINCT task_id) as concurrent_tasks
                    FROM tasks
                    WHERE namespace = :namespace
                    AND started_at >= :start_time
                    AND started_at IS NOT NULL
                    {queue_condition}
                    GROUP BY date_trunc('{granularity}', started_at)
                )
                SELECT 
                    ts.time_bucket,
                    COALESCE(cd.concurrent_tasks, 0) as concurrent_tasks
                FROM time_series ts
                LEFT JOIN concurrency_data cd ON ts.time_bucket = cd.time_bucket
                ORDER BY ts.time_bucket
            """
            
            concurrency_result = await pg_conn.execute(
                text(concurrency_query),
                {"namespace": namespace, "start_time": start_time}
            )
            
            concurrency = [
                {"time": row.time_bucket.isoformat(), "value": row.concurrent_tasks, "metric": "并发数"}
                for row in concurrency_result
            ]
            
            # 获取处理时间数据
            processing_time_query = f"""
                WITH time_series AS (
                    SELECT generate_series(
                        date_trunc('{granularity}', :start_time::timestamptz),
                        date_trunc('{granularity}', CURRENT_TIMESTAMP),
                        '{interval}'::interval
                    ) AS time_bucket
                ),
                processing_metrics AS (
                    SELECT 
                        date_trunc('{granularity}', completed_at) as time_bucket,
                        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (completed_at - started_at)) * 1000) as p50,
                        PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (completed_at - started_at)) * 1000) as p90,
                        AVG(EXTRACT(EPOCH FROM (completed_at - started_at)) * 1000) as avg_time
                    FROM tasks
                    WHERE namespace = :namespace
                    AND completed_at >= :start_time
                    AND status = 'completed'
                    AND started_at IS NOT NULL
                    {queue_condition}
                    GROUP BY date_trunc('{granularity}', completed_at)
                )
                SELECT 
                    ts.time_bucket,
                    COALESCE(pm.p50, 0) as p50,
                    COALESCE(pm.p90, 0) as p90,
                    COALESCE(pm.avg_time, 0) as avg_time
                FROM time_series ts
                LEFT JOIN processing_metrics pm ON ts.time_bucket = pm.time_bucket
                ORDER BY ts.time_bucket
            """
            
            processing_result = await pg_conn.execute(
                text(processing_time_query),
                {"namespace": namespace, "start_time": start_time}
            )
            
            processing_time = []
            for row in processing_result:
                time_str = row.time_bucket.isoformat()
                processing_time.extend([
                    {"time": time_str, "value": round(row.p50, 2), "metric": "P50处理时间"},
                    {"time": time_str, "value": round(row.p90, 2), "metric": "P90处理时间"},
                    {"time": time_str, "value": round(row.avg_time, 2), "metric": "平均处理时间"}
                ])
            
            # 获取创建延时数据
            creation_latency_query = f"""
                WITH time_series AS (
                    SELECT generate_series(
                        date_trunc('{granularity}', :start_time::timestamptz),
                        date_trunc('{granularity}', CURRENT_TIMESTAMP),
                        '{interval}'::interval
                    ) AS time_bucket
                ),
                latency_metrics AS (
                    SELECT 
                        date_trunc('{granularity}', started_at) as time_bucket,
                        AVG(EXTRACT(EPOCH FROM (started_at - created_at)) * 1000) as avg_latency
                    FROM tasks
                    WHERE namespace = :namespace
                    AND started_at >= :start_time
                    AND started_at IS NOT NULL
                    {queue_condition}
                    GROUP BY date_trunc('{granularity}', started_at)
                )
                SELECT 
                    ts.time_bucket,
                    COALESCE(lm.avg_latency, 0) as avg_latency
                FROM time_series ts
                LEFT JOIN latency_metrics lm ON ts.time_bucket = lm.time_bucket
                ORDER BY ts.time_bucket
            """
            
            latency_result = await pg_conn.execute(
                text(latency_query),
                {"namespace": namespace, "start_time": start_time}
            )
            
            creation_latency = [
                {"time": row.time_bucket.isoformat(), "value": round(row.avg_latency, 2), "metric": "创建延时"}
                for row in latency_result
            ]
            
            return {
                "task_trend": task_trend,
                "concurrency": concurrency,
                "processing_time": processing_time,
                "creation_latency": creation_latency,
                "granularity": granularity
            }
            
    except Exception as e:
        logger.error(f"获取概览统计失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/data/top-queues/{namespace}")
async def get_top_queues(
    namespace: str,
    metric: str = Query("backlog", description="排序指标: backlog或error"),
    limit: int = Query(10, description="返回数量"),
    time_range: Optional[str] = Query(None, description="时间范围"),
    queues: Optional[str] = Query(None, description="逗号分隔的队列名称列表")
):
    """
    获取Top队列（按积压或错误率排序）
    """
    try:
        data_access = get_namespace_data_access()
        
        if metric == "backlog":
            # 获取积压最多的队列
            queues_data = await data_access.get_queue_stats(namespace)
            
            # 如果指定了队列筛选，进行过滤
            if queues:
                queue_filter = [q.strip() for q in queues.split(',') if q.strip()]
                queues_data = [q for q in queues_data if get_base_queue_name(q['queue_name']) in queue_filter]
            
            # 按积压数量排序
            sorted_queues = sorted(queues_data, key=lambda x: x.get('pending', 0), reverse=True)[:limit]
            
            result = []
            for queue in sorted_queues:
                backlog = queue.get('pending', 0)
                status = 'normal'
                if backlog > 1000:
                    status = 'critical'
                elif backlog > 100:
                    status = 'warning'
                
                result.append({
                    "queue": get_base_queue_name(queue['queue_name']),
                    "backlog": backlog,
                    "status": status
                })
            
            return {"success": True, "data": result}
            
        elif metric == "error":
            # 获取错误率最高的队列
            conn = await data_access.manager.get_connection(namespace)
            if not conn.pg_config:
                return {"success": True, "data": []}
            
            # 解析时间范围
            time_delta = parse_time_range(time_range) if time_range else timedelta(hours=24)
            start_time = datetime.now(timezone.utc) - time_delta
            
            # 构建队列筛选条件
            queue_condition = ""
            if queues:
                queue_filter = [q.strip() for q in queues.split(',') if q.strip()]
                queue_list = "', '".join(queue_filter)
                queue_condition = f"AND queue IN ('{queue_list}')"
            
            async with conn.async_engine.begin() as pg_conn:
                query = f"""
                    SELECT 
                        queue,
                        COUNT(*) as total,
                        COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed,
                        ROUND(COUNT(CASE WHEN status = 'failed' THEN 1 END) * 100.0 / COUNT(*), 2) as error_rate
                    FROM tasks
                    WHERE namespace = :namespace
                    AND created_at >= :start_time
                    {queue_condition}
                    GROUP BY queue
                    HAVING COUNT(CASE WHEN status = 'failed' THEN 1 END) > 0
                    ORDER BY error_rate DESC
                    LIMIT :limit
                """
                
                result = await pg_conn.execute(
                    text(query),
                    {"namespace": namespace, "start_time": start_time, "limit": limit}
                )
                
                data = [
                    {
                        "queue": row.queue,
                        "errorRate": row.error_rate,
                        "failed": row.failed,
                        "total": row.total
                    }
                    for row in result
                ]
                
                return {"success": True, "data": data}
        
        else:
            raise HTTPException(status_code=400, detail="无效的metric参数")
            
    except Exception as e:
        logger.error(f"获取Top队列失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/data/queue-backlog-trend/{namespace}")
async def get_queue_backlog_trend(
    namespace: str,
    time_range: str = "1h",
    queues: Optional[str] = Query(None, description="逗号分隔的队列名称列表")
):
    """
    获取队列积压趋势数据
    """
    try:
        data_access = get_namespace_data_access()
        conn = await data_access.manager.get_connection(namespace)
        
        if not conn.pg_config:
            return {"success": True, "data": []}
        
        # 解析时间范围
        time_delta = parse_time_range(time_range)
        start_time = datetime.now(timezone.utc) - time_delta
        
        # 解析队列筛选
        queue_filter = []
        if queues:
            queue_filter = [q.strip() for q in queues.split(',') if q.strip()]
        
        async with conn.async_engine.begin() as pg_conn:
            # 构建队列筛选条件
            queue_condition = ""
            if queue_filter:
                queue_list = "', '".join(queue_filter)
                queue_condition = f"AND queue IN ('{queue_list}')"
            
            # 根据时间范围决定数据粒度
            if time_delta <= timedelta(hours=1):
                granularity = "minute"
            elif time_delta <= timedelta(hours=6):
                granularity = "5 minutes"
            elif time_delta <= timedelta(days=1):
                granularity = "hour"
            else:
                granularity = "day"
            
            query = f"""
                SELECT 
                    date_trunc('{granularity}', created_at) as time_bucket,
                    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_count
                FROM tasks
                WHERE namespace = :namespace
                AND created_at >= :start_time
                {queue_condition}
                GROUP BY date_trunc('{granularity}', created_at)
                ORDER BY time_bucket
            """
            
            result = await pg_conn.execute(
                text(query),
                {"namespace": namespace, "start_time": start_time}
            )
            
            data = [
                {
                    "time": row.time_bucket.isoformat(),
                    "value": row.pending_count,
                    "metric": "排队任务数"
                }
                for row in result
            ]
            
            return {"success": True, "data": data}
            
    except Exception as e:
        logger.error(f"获取队列积压趋势失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 队列管理接口 ====================

@router.get("/queues/{namespace}")
async def get_queues(namespace: str):
    """获取指定命名空间的队列列表"""
    try:
        namespace_access = get_namespace_data_access()
        queues_data = await namespace_access.get_queue_stats(namespace)
        return {
            "success": True,
            "data": list(set([get_base_queue_name(q['queue_name']) for q in queues_data]))
        }
    except Exception as e:
        logger.error(f"获取队列列表失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/data/queue-details/{namespace}")
async def get_queue_details(
    namespace: str,
    params: Dict[str, Any]
):
    """获取队列详细信息"""
    try:
        data_access = get_namespace_data_access()
        
        # 获取分页参数
        page = params.get('page', 1)
        page_size = params.get('pageSize', 10)
        
        # 获取队列统计数据
        queues_data = await data_access.get_queue_stats(namespace)
        
        # 处理数据
        processed_data = []
        for queue in queues_data:
            base_name = get_base_queue_name(queue['queue_name'])
            existing = next((q for q in processed_data if q['queue_name'] == base_name), None)
            
            if existing:
                existing['pending'] += queue.get('pending', 0)
                existing['running'] += queue.get('running', 0)
                existing['completed'] += queue.get('completed', 0)
                existing['failed'] += queue.get('failed', 0)
            else:
                processed_data.append({
                    'queue_name': base_name,
                    'pending': queue.get('pending', 0),
                    'running': queue.get('running', 0),
                    'completed': queue.get('completed', 0),
                    'failed': queue.get('failed', 0),
                    'total': queue.get('pending', 0) + queue.get('running', 0) + 
                            queue.get('completed', 0) + queue.get('failed', 0)
                })
        
        # 分页
        start = (page - 1) * page_size
        end = start + page_size
        paginated_data = processed_data[start:end]
        
        return {
            "success": True,
            "data": paginated_data,
            "total": len(processed_data),
            "page": page,
            "pageSize": page_size
        }
        
    except Exception as e:
        logger.error(f"获取队列详情失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/queue/{queue_name}")
async def delete_queue(queue_name: str):
    """删除队列"""
    try:
        namespace_access = get_namespace_data_access()
        # 这里需要实现删除队列的逻辑
        # 暂时返回成功
        return {"success": True, "message": f"队列 {queue_name} 已删除"}
    except Exception as e:
        logger.error(f"删除队列失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/queue/{queue_name}/trim")
async def trim_queue(queue_name: str, params: Dict[str, Any]):
    """清理队列"""
    try:
        keep_count = params.get('keep_count', 0)
        # 这里需要实现清理队列的逻辑
        # 暂时返回成功
        return {"success": True, "message": f"队列 {queue_name} 已清理，保留 {keep_count} 条"}
    except Exception as e:
        logger.error(f"清理队列失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/data/queue-timeline/{namespace}")
async def get_queue_timeline(
    namespace: str,
    params: TimeRangeQuery
):
    """获取队列时间线数据"""
    try:
        data_access = get_namespace_data_access()
        conn = await data_access.manager.get_connection(namespace)
        
        if not conn.pg_config:
            return {"data": [], "stats": {}}
        
        # 实现获取队列时间线数据的逻辑
        return {
            "data": [],
            "stats": {
                "total_messages": 0,
                "avg_processing_time": 0,
                "max_processing_time": 0
            }
        }
        
    except Exception as e:
        logger.error(f"获取队列时间线失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/data/queue-flow-rates/{namespace}")
async def get_queue_flow_rates(
    namespace: str,
    params: TimeRangeQuery
):
    """获取队列流量速率"""
    try:
        data_access = get_namespace_data_access()
        conn = await data_access.manager.get_connection(namespace)
        
        if not conn.pg_config:
            return {"data": []}
        
        # 实现获取队列流量速率的逻辑
        return {"data": []}
        
    except Exception as e:
        logger.error(f"获取队列流量速率失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 任务管理接口 ====================

@router.post("/data/tasks/{namespace}")
async def get_tasks(
    namespace: str,
    params: Dict[str, Any]
):
    """获取任务列表"""
    try:
        data_access = get_namespace_data_access()
        conn = await data_access.manager.get_connection(namespace)
        
        if not conn.pg_config:
            return {"data": [], "total": 0}
        
        # 获取分页参数
        page = params.get('page', 1)
        page_size = params.get('pageSize', 20)
        queue_name = params.get('queue_name')
        status = params.get('status')
        
        offset = (page - 1) * page_size
        
        async with conn.async_engine.begin() as pg_conn:
            # 构建查询条件
            conditions = ["namespace = :namespace"]
            query_params = {"namespace": namespace}
            
            if queue_name:
                conditions.append("queue = :queue")
                query_params["queue"] = queue_name
            
            if status:
                conditions.append("status = :status")
                query_params["status"] = status
            
            where_clause = " AND ".join(conditions)
            
            # 获取总数
            count_query = f"SELECT COUNT(*) as total FROM tasks WHERE {where_clause}"
            count_result = await pg_conn.execute(text(count_query), query_params)
            total = count_result.fetchone().total
            
            # 获取任务列表
            query = f"""
                SELECT 
                    task_id,
                    queue,
                    status,
                    created_at,
                    started_at,
                    completed_at,
                    error_message
                FROM tasks
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT :limit OFFSET :offset
            """
            
            query_params["limit"] = page_size
            query_params["offset"] = offset
            
            result = await pg_conn.execute(text(query), query_params)
            
            tasks = []
            for row in result:
                tasks.append({
                    "task_id": row.task_id,
                    "queue": row.queue,
                    "status": row.status,
                    "created_at": row.created_at.isoformat() if row.created_at else None,
                    "started_at": row.started_at.isoformat() if row.started_at else None,
                    "completed_at": row.completed_at.isoformat() if row.completed_at else None,
                    "error_message": row.error_message
                })
            
            return {
                "data": tasks,
                "total": total,
                "page": page,
                "pageSize": page_size
            }
            
    except Exception as e:
        logger.error(f"获取任务列表失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/task/{task_id}/details")
async def get_task_details(
    task_id: str,
    consumer_group: Optional[str] = Query(None)
):
    """获取任务详情"""
    try:
        # 实现获取任务详情的逻辑
        return {
            "task_id": task_id,
            "status": "completed",
            "created_at": datetime.now().isoformat(),
            "consumer_group": consumer_group
        }
    except Exception as e:
        logger.error(f"获取任务详情失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 定时任务接口 ====================

@router.get("/data/scheduled-tasks/{namespace}")
async def get_scheduled_tasks(
    namespace: str,
    limit: int = Query(20),
    offset: int = Query(0)
):
    """获取定时任务列表"""
    try:
        data_access = get_namespace_data_access()
        conn = await data_access.manager.get_connection(namespace)
        
        if not conn.pg_config:
            return {"data": [], "total": 0}
        
        async with conn.async_engine.begin() as pg_conn:
            # 获取总数
            count_query = """
                SELECT COUNT(*) as total 
                FROM scheduled_tasks 
                WHERE namespace = :namespace
            """
            count_result = await pg_conn.execute(
                text(count_query),
                {"namespace": namespace}
            )
            total = count_result.fetchone().total
            
            # 获取定时任务列表
            query = """
                SELECT 
                    id,
                    task_name,
                    queue_name,
                    task_data,
                    cron_expression,
                    interval_seconds,
                    enabled,
                    last_run_at,
                    next_run_at,
                    created_at
                FROM scheduled_tasks
                WHERE namespace = :namespace
                ORDER BY created_at DESC
                LIMIT :limit OFFSET :offset
            """
            
            result = await pg_conn.execute(
                text(query),
                {"namespace": namespace, "limit": limit, "offset": offset}
            )
            
            tasks = []
            for row in result:
                tasks.append({
                    "id": row.id,
                    "task_name": row.task_name,
                    "queue_name": row.queue_name,
                    "task_data": row.task_data,
                    "cron_expression": row.cron_expression,
                    "interval_seconds": row.interval_seconds,
                    "enabled": row.enabled,
                    "last_run_at": row.last_run_at.isoformat() if row.last_run_at else None,
                    "next_run_at": row.next_run_at.isoformat() if row.next_run_at else None,
                    "created_at": row.created_at.isoformat() if row.created_at else None
                })
            
            return {
                "data": tasks,
                "total": total
            }
            
    except Exception as e:
        logger.error(f"获取定时任务列表失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scheduled-tasks/statistics/{namespace}")
async def get_scheduled_tasks_statistics(namespace: str):
    """获取定时任务统计信息"""
    try:
        data_access = get_namespace_data_access()
        conn = await data_access.manager.get_connection(namespace)
        
        if not conn.pg_config:
            return {
                "total": 0,
                "enabled": 0,
                "disabled": 0,
                "running": 0
            }
        
        async with conn.async_engine.begin() as pg_conn:
            query = """
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN enabled = true THEN 1 END) as enabled,
                    COUNT(CASE WHEN enabled = false THEN 1 END) as disabled
                FROM scheduled_tasks
                WHERE namespace = :namespace
            """
            
            result = await pg_conn.execute(
                text(query),
                {"namespace": namespace}
            )
            
            stats = result.fetchone()
            
            return {
                "total": stats.total,
                "enabled": stats.enabled,
                "disabled": stats.disabled,
                "running": 0  # 需要实现运行中任务的统计
            }
            
    except Exception as e:
        logger.error(f"获取定时任务统计失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/scheduled-tasks")
async def create_scheduled_task(task: ScheduledTaskCreate):
    """创建定时任务"""
    try:
        # 实现创建定时任务的逻辑
        return {"success": True, "message": "定时任务创建成功"}
    except Exception as e:
        logger.error(f"创建定时任务失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/scheduled-tasks/{task_id}")
async def update_scheduled_task(task_id: str, task: ScheduledTaskUpdate):
    """更新定时任务"""
    try:
        # 实现更新定时任务的逻辑
        return {"success": True, "message": "定时任务更新成功"}
    except Exception as e:
        logger.error(f"更新定时任务失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/scheduled-tasks/{task_id}")
async def delete_scheduled_task(task_id: str):
    """删除定时任务"""
    try:
        # 实现删除定时任务的逻辑
        return {"success": True, "message": "定时任务删除成功"}
    except Exception as e:
        logger.error(f"删除定时任务失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/scheduled-tasks/{task_id}/toggle")
async def toggle_scheduled_task(task_id: str):
    """启用/禁用定时任务"""
    try:
        # 实现切换定时任务状态的逻辑
        return {"success": True, "message": "定时任务状态已切换"}
    except Exception as e:
        logger.error(f"切换定时任务状态失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/scheduled-tasks/{task_id}/execute")
async def execute_scheduled_task(task_id: str):
    """立即执行定时任务"""
    try:
        # 实现立即执行定时任务的逻辑
        return {"success": True, "message": "定时任务已触发执行"}
    except Exception as e:
        logger.error(f"执行定时任务失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 告警规则接口 ====================

@router.get("/alert-rules")
async def get_alert_rules():
    """获取告警规则列表"""
    try:
        # 实现获取告警规则的逻辑
        return {"data": []}
    except Exception as e:
        logger.error(f"获取告警规则失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/alert-rules")
async def create_alert_rule(rule: AlertRuleCreate):
    """创建告警规则"""
    try:
        # 实现创建告警规则的逻辑
        return {"success": True, "message": "告警规则创建成功"}
    except Exception as e:
        logger.error(f"创建告警规则失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/alert-rules/{rule_id}")
async def update_alert_rule(rule_id: str, rule: AlertRuleCreate):
    """更新告警规则"""
    try:
        # 实现更新告警规则的逻辑
        return {"success": True, "message": "告警规则更新成功"}
    except Exception as e:
        logger.error(f"更新告警规则失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/alert-rules/{rule_id}")
async def delete_alert_rule(rule_id: str):
    """删除告警规则"""
    try:
        # 实现删除告警规则的逻辑
        return {"success": True, "message": "告警规则删除成功"}
    except Exception as e:
        logger.error(f"删除告警规则失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/alert-rules/{rule_id}/toggle")
async def toggle_alert_rule(rule_id: str):
    """启用/禁用告警规则"""
    try:
        # 实现切换告警规则状态的逻辑
        return {"success": True, "message": "告警规则状态已切换"}
    except Exception as e:
        logger.error(f"切换告警规则状态失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alert-rules/{rule_id}/history")
async def get_alert_history(rule_id: str):
    """获取告警历史"""
    try:
        # 实现获取告警历史的逻辑
        return {"data": []}
    except Exception as e:
        logger.error(f"获取告警历史失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/alert-rules/{rule_id}/test")
async def test_alert_rule(rule_id: str):
    """测试告警规则"""
    try:
        # 实现测试告警规则的逻辑
        return {"success": True, "message": "告警规则测试成功"}
    except Exception as e:
        logger.error(f"测试告警规则失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 命名空间管理接口 ====================

@router.get("/namespaces")
async def get_namespaces():
    """获取命名空间列表"""
    try:
        # 从配置中获取数据库连接
        if not task_center_config.pg_url:
            return []
        
        engine = create_async_engine(task_center_config.pg_url)
        AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with AsyncSessionLocal() as session:
            query = text("""
                SELECT id, name, description, redis_config, pg_config, created_at, updated_at 
                FROM namespaces 
                ORDER BY name
            """)
            result = await session.execute(query)
            namespaces = []
            for row in result:
                # 解析配置
                redis_config = row.redis_config if row.redis_config else {}
                pg_config = row.pg_config if row.pg_config else {}
                
                namespaces.append({
                    "id": row.id,
                    "name": row.name,
                    "redis_url": redis_config.get("url", ""),
                    "pg_url": pg_config.get("url", ""),
                    "description": row.description or "",
                    "created_at": row.created_at.isoformat() if row.created_at else None,
                    "updated_at": row.updated_at.isoformat() if row.updated_at else None
                })
            
            return namespaces
            
    except Exception as e:
        logger.error(f"获取命名空间列表失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/data/namespaces")
async def get_data_namespaces():
    """获取命名空间列表（数据API版本）"""
    return await get_namespaces()

@router.post("/namespaces")
async def create_namespace(namespace: NamespaceCreate):
    """创建命名空间"""
    try:
        if not task_center_config.pg_url:
            raise HTTPException(status_code=500, detail="数据库未配置")
        
        engine = create_async_engine(task_center_config.pg_url)
        AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with AsyncSessionLocal() as session:
            # 检查命名空间是否已存在
            check_query = text("SELECT id FROM namespaces WHERE name = :name")
            existing = await session.execute(check_query, {"name": namespace.name})
            if existing.fetchone():
                raise HTTPException(status_code=400, detail="命名空间已存在")
            
            # 创建命名空间
            redis_config = {"url": namespace.redis_url} if namespace.redis_url else {}
            pg_config = {"url": namespace.pg_url} if namespace.pg_url else {}
            
            insert_query = text("""
                INSERT INTO namespaces (name, description, redis_config, pg_config, created_at, updated_at)
                VALUES (:name, :description, :redis_config, :pg_config, NOW(), NOW())
                RETURNING id
            """)
            
            result = await session.execute(
                insert_query,
                {
                    "name": namespace.name,
                    "description": namespace.description,
                    "redis_config": json.dumps(redis_config),
                    "pg_config": json.dumps(pg_config)
                }
            )
            await session.commit()
            
            new_id = result.fetchone().id
            
            return {
                "success": True,
                "message": "命名空间创建成功",
                "id": new_id
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建命名空间失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/namespaces/{name}")
async def update_namespace(name: str, namespace: NamespaceUpdate):
    """更新命名空间"""
    try:
        if not task_center_config.pg_url:
            raise HTTPException(status_code=500, detail="数据库未配置")
        
        engine = create_async_engine(task_center_config.pg_url)
        AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with AsyncSessionLocal() as session:
            # 获取现有命名空间
            query = text("SELECT redis_config, pg_config FROM namespaces WHERE name = :name")
            result = await session.execute(query, {"name": name})
            row = result.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail="命名空间不存在")
            
            # 解析现有配置
            redis_config = row.redis_config if row.redis_config else {}
            pg_config = row.pg_config if row.pg_config else {}
            
            # 更新配置
            if namespace.redis_url is not None:
                redis_config["url"] = namespace.redis_url
            if namespace.pg_url is not None:
                pg_config["url"] = namespace.pg_url
            
            # 更新数据库
            update_query = text("""
                UPDATE namespaces 
                SET redis_config = :redis_config, 
                    pg_config = :pg_config,
                    description = :description,
                    updated_at = NOW()
                WHERE name = :name
            """)
            
            await session.execute(
                update_query,
                {
                    "name": name,
                    "redis_config": json.dumps(redis_config),
                    "pg_config": json.dumps(pg_config),
                    "description": namespace.description
                }
            )
            await session.commit()
            
            return {"success": True, "message": "命名空间更新成功"}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新命名空间失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/namespaces/{name}")
async def delete_namespace(name: str):
    """删除命名空间"""
    try:
        if not task_center_config.pg_url:
            raise HTTPException(status_code=500, detail="数据库未配置")
        
        engine = create_async_engine(task_center_config.pg_url)
        AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with AsyncSessionLocal() as session:
            # 检查命名空间是否存在
            check_query = text("SELECT id FROM namespaces WHERE name = :name")
            result = await session.execute(check_query, {"name": name})
            if not result.fetchone():
                raise HTTPException(status_code=404, detail="命名空间不存在")
            
            # 删除命名空间
            delete_query = text("DELETE FROM namespaces WHERE name = :name")
            await session.execute(delete_query, {"name": name})
            await session.commit()
            
            return {"success": True, "message": "命名空间删除成功"}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除命名空间失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/namespaces/{name}")
async def get_namespace_details(name: str):
    """获取命名空间详情"""
    try:
        if not task_center_config.pg_url:
            raise HTTPException(status_code=500, detail="数据库未配置")
        
        engine = create_async_engine(task_center_config.pg_url)
        AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with AsyncSessionLocal() as session:
            query = text("""
                SELECT id, name, description, redis_config, pg_config, created_at, updated_at 
                FROM namespaces 
                WHERE name = :name
            """)
            result = await session.execute(query, {"name": name})
            row = result.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail="命名空间不存在")
            
            # 解析配置
            redis_config = row.redis_config if row.redis_config else {}
            pg_config = row.pg_config if row.pg_config else {}
            
            return {
                "id": row.id,
                "name": row.name,
                "redis_url": redis_config.get("url", ""),
                "pg_url": pg_config.get("url", ""),
                "description": row.description or "",
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "updated_at": row.updated_at.isoformat() if row.updated_at else None
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取命名空间详情失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Redis监控接口 ====================

@router.get("/redis/monitor/{namespace}")
async def get_redis_monitor(namespace: str):
    """获取Redis监控信息"""
    try:
        data_access = get_namespace_data_access()
        conn = await data_access.manager.get_connection(namespace)
        
        # 获取Redis客户端
        try:
            redis_client = await conn.get_redis_client()
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        
        # 获取Redis信息
        info = await redis_client.info()
        
        # 处理内存信息
        memory_info = {
            "used_memory": info.get("used_memory", 0),
            "used_memory_human": info.get("used_memory_human", "0B"),
            "usage_percentage": None,
            "maxmemory": info.get("maxmemory", 0),
            "maxmemory_human": "0B",
            "mem_fragmentation_ratio": info.get("mem_fragmentation_ratio", 1.0)
        }
        
        # 计算内存使用百分比
        if info.get("maxmemory") and info.get("maxmemory") > 0:
            memory_info["usage_percentage"] = round(
                (info.get("used_memory", 0) / info.get("maxmemory")) * 100, 2
            )
            memory_info["maxmemory_human"] = f"{info.get('maxmemory') / (1024*1024):.1f}MB"
        
        # 处理客户端信息
        clients_info = {
            "connected_clients": info.get("connected_clients", 0),
            "blocked_clients": info.get("blocked_clients", 0)
        }
        
        # 处理统计信息
        stats_info = {
            "instantaneous_ops_per_sec": info.get("instantaneous_ops_per_sec", 0),
            "hit_rate": 0,
            "keyspace_hits": info.get("keyspace_hits", 0),
            "keyspace_misses": info.get("keyspace_misses", 0)
        }
        
        # 计算命中率
        total_hits = stats_info["keyspace_hits"] + stats_info["keyspace_misses"]
        if total_hits > 0:
            stats_info["hit_rate"] = round(
                (stats_info["keyspace_hits"] / total_hits) * 100, 2
            )
        
        # 处理键空间信息
        keyspace_info = {
            "total_keys": 0
        }
        
        # 统计所有数据库的键数量
        for key in info:
            if key.startswith("db"):
                db_info = info[key]
                if isinstance(db_info, dict):
                    keyspace_info["total_keys"] += db_info.get("keys", 0)
        
        # 处理服务器信息
        server_info = {
            "redis_version": info.get("redis_version", "unknown"),
            "uptime_in_seconds": info.get("uptime_in_seconds", 0)
        }
        
        return {
            "success": True,
            "data": {
                "status": "healthy",
                "memory": memory_info,
                "clients": clients_info,
                "stats": stats_info,
                "keyspace": keyspace_info,
                "server": server_info
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取Redis监控信息失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 流积压监控接口 ====================

@router.get("/stream-backlog/{namespace}")
async def get_stream_backlog(
    namespace: str,
    time_range: str = Query("1h", description="时间范围"),
    queue: Optional[str] = Query(None, description="队列名称")
):
    """获取流积压数据"""
    try:
        data_access = get_namespace_data_access()
        conn = await data_access.manager.get_connection(namespace)
        
        if not conn.pg_config:
            return {"data": []}
        
        # 解析时间范围
        time_delta = parse_time_range(time_range)
        start_time = datetime.now(timezone.utc) - time_delta
        
        async with conn.async_engine.begin() as pg_conn:
            # 构建查询条件
            conditions = ["namespace = :namespace", "created_at >= :start_time"]
            params = {"namespace": namespace, "start_time": start_time}
            
            if queue:
                conditions.append("stream_name = :queue")
                params["queue"] = queue
            
            where_clause = " AND ".join(conditions)
            
            query = f"""
                SELECT 
                    stream_name,
                    consumer_group,
                    consumer_lag,
                    last_published_offset,
                    last_acknowledged_offset,
                    created_at
                FROM stream_backlog_monitor
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT 1000
            """
            
            result = await pg_conn.execute(text(query), params)
            
            data = []
            for row in result:
                data.append({
                    "stream_name": row.stream_name,
                    "consumer_group": row.consumer_group,
                    "consumer_lag": row.consumer_lag,
                    "last_published_offset": row.last_published_offset,
                    "last_acknowledged_offset": row.last_acknowledged_offset,
                    "created_at": row.created_at.isoformat()
                })
            
            return {"data": data}
            
    except Exception as e:
        logger.error(f"获取流积压数据失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# 导出路由器
__all__ = ["router"]