"""
Monitoring and analytics API v1
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis

from dependencies import (
    get_validated_namespace, get_pg_connection, get_redis_client,
    get_namespace_connection, validate_time_range, get_request_metrics, RequestMetrics
)
from models.requests import MonitoringRequest, BacklogTrendRequest, AnalyticsRequest
from models.responses import MonitoringResponse, AnalyticsResponse, BaseResponse
from core.cache import cache_result, CACHE_CONFIGS
from queue_backlog_api import get_backlog_trend
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/backlog-trends", response_model=MonitoringResponse)
@cache_result(**CACHE_CONFIGS['monitoring_data'])
async def get_queue_backlog_trends(
    request: BacklogTrendRequest,
    namespace: str = Depends(get_validated_namespace),
    metrics: RequestMetrics = Depends(get_request_metrics)
):
    """获取队列积压趋势（统一接口）"""
    metrics.start(namespace, "POST /monitoring/backlog-trends")
    
    try:
        # 直接调用现有的积压趋势API
        backlog_response = await get_backlog_trend(request)
        
        # 转换为标准监控响应格式
        monitoring_data = {
            'series': [],
            'granularity': backlog_response.granularity,
            'time_range': backlog_response.time_range
        }
        
        # 按系列分组数据
        series_data = {}
        for item in backlog_response.data:
            series_name = item.get('group') or item['queue']
            if series_name not in series_data:
                series_data[series_name] = []
            
            series_data[series_name].append({
                'timestamp': item['time'],
                'value': item['backlog'],
                'metadata': {
                    'queue': item['queue'],
                    'consumer_group': item.get('group'),
                    'published': item.get('published'),
                    'delivered': item.get('delivered'),
                    'pending': item.get('pending')
                }
            })
        
        # 转换为时间序列格式
        for series_name, data_points in series_data.items():
            monitoring_data['series'].append({
                'name': series_name,
                'data_points': data_points,
                'unit': 'tasks'
            })
        
        return MonitoringResponse(data=monitoring_data)
        
    except Exception as e:
        logger.error(f"获取积压趋势失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        metrics.finish()


@router.get("/queue-flow-rates/{queue_name}", response_model=MonitoringResponse)
@cache_result(**CACHE_CONFIGS['monitoring_data'])
async def get_queue_flow_rates(
    queue_name: str,
    namespace: str = Depends(get_validated_namespace),
    time_params: dict = Depends(validate_time_range),
    granularity: Optional[str] = Query(None, description="数据粒度"),
    redis_client: redis.Redis = Depends(get_redis_client),
    pg_session: AsyncSession = Depends(get_pg_connection),
    metrics: RequestMetrics = Depends(get_request_metrics)
):
    """获取队列流量速率"""
    metrics.start(namespace, f"GET /monitoring/queue-flow-rates/{queue_name}")
    print(f'{get_queue_flow_rates=}')
    try:
        # 使用现有的data_access来获取流量速率
        from ...data_access import JetTaskDataAccess
        
        data_access = JetTaskDataAccess()
        
        flow_data, returned_granularity = await data_access.fetch_queue_flow_rates(
            queue_name=queue_name,
            start_time=time_params.get('start_time'),
            end_time=time_params.get('end_time'),
            filters=[]
        )
        
        # 转换为监控响应格式
        series_data = {
            'enqueued': [],
            'started': [],
            'completed': []
        }
        
        for item in flow_data:
            timestamp = item['time']
            series_data['enqueued'].append({
                'timestamp': timestamp,
                'value': item.get('enqueued', 0),
                'metadata': {'queue': queue_name, 'type': 'enqueued'}
            })
            series_data['started'].append({
                'timestamp': timestamp,
                'value': item.get('started', 0),
                'metadata': {'queue': queue_name, 'type': 'started'}
            })
            series_data['completed'].append({
                'timestamp': timestamp,
                'value': item.get('completed', 0),
                'metadata': {'queue': queue_name, 'type': 'completed'}
            })
        
        monitoring_data = {
            'series': [
                {
                    'name': 'Enqueued',
                    'data_points': series_data['enqueued'],
                    'unit': 'tasks/min'
                },
                {
                    'name': 'Started',
                    'data_points': series_data['started'],
                    'unit': 'tasks/min'
                },
                {
                    'name': 'Completed',
                    'data_points': series_data['completed'],
                    'unit': 'tasks/min'
                }
            ],
            'granularity': returned_granularity,
            'time_range': {
                'start': time_params.get('start_time'),
                'end': time_params.get('end_time')
            }
        }
        
        return MonitoringResponse(data=monitoring_data)
        
    except Exception as e:
        logger.error(f"获取队列流量速率失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        metrics.finish()


@router.get("/system-health")
async def get_system_health(
    namespace: str = Depends(get_validated_namespace),
    redis_client: redis.Redis = Depends(get_redis_client),
    pg_session: AsyncSession = Depends(get_pg_connection),
    metrics: RequestMetrics = Depends(get_request_metrics)
):
    """获取系统健康状态"""
    metrics.start(namespace, "GET /monitoring/system-health")
    
    try:
        health_data = {
            'status': 'healthy',
            'version': '1.0.0',
            'uptime': 3600.0,  # 示例运行时间
            'components': {},
            'metrics': {}
        }
        
        # 检查Redis连接
        try:
            await redis_client.ping()
            health_data['components']['redis'] = 'healthy'
        except Exception as e:
            health_data['components']['redis'] = f'unhealthy: {str(e)}'
            health_data['status'] = 'degraded'
        
        # 检查PostgreSQL连接
        try:
            result = await pg_session.execute("SELECT 1")
            health_data['components']['postgresql'] = 'healthy'
        except Exception as e:
            health_data['components']['postgresql'] = f'unhealthy: {str(e)}'
            health_data['status'] = 'degraded'
        
        # 获取系统指标
        try:
            import psutil
            import time
            
            health_data['metrics'] = {
                'cpu_usage': psutil.cpu_percent(interval=1),
                'memory_usage': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent,
                'process_count': len(psutil.pids()),
                'uptime': time.time() - psutil.boot_time()
            }
        except ImportError:
            health_data['metrics'] = {
                'note': 'psutil not available for system metrics'
            }
        
        return BaseResponse(data=health_data)
        
    except Exception as e:
        logger.error(f"获取系统健康状态失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        metrics.finish()


@router.post("/analytics", response_model=AnalyticsResponse)
@cache_result(ttl=600, key_prefix="analytics")  # 10分钟缓存
async def get_analytics_data(
    request: AnalyticsRequest,
    namespace: str = Depends(get_validated_namespace),
    pg_session: AsyncSession = Depends(get_pg_connection),
    metrics: RequestMetrics = Depends(get_request_metrics)
):
    """获取分析数据"""
    metrics.start(namespace, "POST /monitoring/analytics")
    
    try:
        analysis_type = request.analysis_type.lower()
        
        if analysis_type == "queue_performance":
            # 队列性能分析
            analytics_data = await _analyze_queue_performance(
                pg_session, request.dimensions, request.metrics,
                request.start_time, request.end_time
            )
        
        elif analysis_type == "task_distribution":
            # 任务分布分析
            analytics_data = await _analyze_task_distribution(
                pg_session, request.dimensions, request.metrics,
                request.start_time, request.end_time
            )
        
        elif analysis_type == "error_patterns":
            # 错误模式分析
            analytics_data = await _analyze_error_patterns(
                pg_session, request.dimensions, request.metrics,
                request.start_time, request.end_time
            )
        
        elif analysis_type == "resource_utilization":
            # 资源利用率分析
            analytics_data = await _analyze_resource_utilization(
                pg_session, request.dimensions, request.metrics,
                request.start_time, request.end_time
            )
        
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported analysis type: {analysis_type}"
            )
        
        return AnalyticsResponse(data=analytics_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取分析数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        metrics.finish()


@router.get("/alerts/active")
async def get_active_alerts(
    namespace: str = Depends(get_validated_namespace),
    severity: Optional[str] = Query(None, description="告警级别筛选"),
    metrics: RequestMetrics = Depends(get_request_metrics)
):
    """获取活跃告警"""
    metrics.start(namespace, "GET /monitoring/alerts/active")
    
    try:
        # 这里需要实现告警查询逻辑
        # 1. 从告警存储中获取活跃告警
        # 2. 根据严重程度筛选
        # 3. 返回告警详情
        
        # 暂时返回模拟数据
        alerts = [
            {
                "id": "alert_001",
                "rule_name": "High Queue Backlog",
                "severity": "warning",
                "status": "firing",
                "queue_name": "shared_queue",
                "trigger_value": 1200,
                "threshold": 1000,
                "started_at": "2025-09-08T12:00:00Z",
                "description": "Queue backlog exceeds threshold"
            },
            {
                "id": "alert_002", 
                "rule_name": "High Error Rate",
                "severity": "critical",
                "status": "firing",
                "queue_name": "priority_queue",
                "trigger_value": 0.15,
                "threshold": 0.10,
                "started_at": "2025-09-08T11:30:00Z",
                "description": "Error rate exceeds 10%"
            }
        ]
        
        # 应用严重程度筛选
        if severity:
            alerts = [alert for alert in alerts if alert['severity'] == severity]
        
        return BaseResponse(
            data={
                "alerts": alerts,
                "total_count": len(alerts),
                "counts_by_severity": {
                    "critical": len([a for a in alerts if a['severity'] == 'critical']),
                    "warning": len([a for a in alerts if a['severity'] == 'warning']),
                    "info": len([a for a in alerts if a['severity'] == 'info'])
                }
            }
        )
        
    except Exception as e:
        logger.error(f"获取活跃告警失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        metrics.finish()


# 辅助分析函数

async def _analyze_queue_performance(pg_session, dimensions, metrics, start_time, end_time):
    """分析队列性能"""
    # 这里实现队列性能分析逻辑
    return {
        "chart_data": [
            {"queue": "shared_queue", "avg_processing_time": 12.5, "throughput": 234.5},
            {"queue": "priority_queue", "avg_processing_time": 8.2, "throughput": 156.3}
        ],
        "summary": {
            "total_queues": 2,
            "avg_processing_time": 10.35,
            "total_throughput": 390.8
        },
        "insights": [
            "shared_queue has higher processing time but better throughput",
            "priority_queue shows good processing efficiency"
        ]
    }


async def _analyze_task_distribution(pg_session, dimensions, metrics, start_time, end_time):
    """分析任务分布"""
    # 这里实现任务分布分析逻辑
    return {
        "chart_data": [
            {"hour": 0, "task_count": 45, "queue": "shared_queue"},
            {"hour": 1, "task_count": 52, "queue": "shared_queue"},
            {"hour": 2, "task_count": 38, "queue": "shared_queue"}
        ],
        "summary": {
            "total_tasks": 135,
            "peak_hour": 1,
            "lowest_hour": 2
        },
        "insights": [
            "Task load is relatively stable with slight peak at hour 1"
        ]
    }


async def _analyze_error_patterns(pg_session, dimensions, metrics, start_time, end_time):
    """分析错误模式"""
    # 这里实现错误模式分析逻辑
    return {
        "chart_data": [
            {"error_type": "TimeoutError", "count": 25, "percentage": 45.5},
            {"error_type": "ConnectionError", "count": 18, "percentage": 32.7},
            {"error_type": "ValidationError", "count": 12, "percentage": 21.8}
        ],
        "summary": {
            "total_errors": 55,
            "most_common_error": "TimeoutError",
            "error_rate": 0.044
        },
        "insights": [
            "TimeoutError is the most common error type",
            "Consider increasing timeout values for better reliability"
        ]
    }


async def _analyze_resource_utilization(pg_session, dimensions, metrics, start_time, end_time):
    """分析资源利用率"""
    # 这里实现资源利用率分析逻辑
    return {
        "chart_data": [
            {"timestamp": "2025-09-08T12:00:00Z", "cpu": 45.2, "memory": 62.1, "disk": 23.4},
            {"timestamp": "2025-09-08T12:15:00Z", "cpu": 52.8, "memory": 65.3, "disk": 23.5}
        ],
        "summary": {
            "avg_cpu": 49.0,
            "avg_memory": 63.7,
            "avg_disk": 23.45
        },
        "insights": [
            "CPU utilization is moderate",
            "Memory usage is within acceptable range",
            "Disk usage is low"
        ]
    }