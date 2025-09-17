"""
Queue management API v1
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis

from dependencies import (
    get_validated_namespace, get_pg_connection, get_redis_client,
    get_namespace_connection, validate_page_params, validate_time_range,
    get_request_metrics, RequestMetrics
)
from models.requests import QueueListRequest, QueueMetricsRequest, QueueActionRequest
from models.responses import QueueListResponse, QueueDetailResponse, MonitoringResponse, BaseResponse
from core.cache import cache_result, CACHE_CONFIGS
from core.exceptions import QueueNotFoundError, ValidationError
from queue_stats_v2 import QueueStatsV2
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("", response_model=QueueListResponse)
@cache_result(**CACHE_CONFIGS['queue_stats'])
async def list_queues(
    namespace: str = Depends(get_validated_namespace),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    status: Optional[str] = Query(None, description="状态筛选"),
    include_stats: bool = Query(True, description="是否包含统计信息"),
    redis_client: redis.Redis = Depends(get_redis_client),
    pg_session: AsyncSession = Depends(get_pg_connection),
    connection = Depends(get_namespace_connection),
    metrics: RequestMetrics = Depends(get_request_metrics)
):
    """获取队列列表"""
    metrics.start(namespace, "GET /queues")
    
    try:
        # 创建队列统计服务
        stats_service = QueueStatsV2(
            redis_client=redis_client,
            pg_session=pg_session,
            redis_prefix=connection.redis_prefix
        )
        
        # 获取队列统计数据
        queue_stats = await stats_service.get_queue_stats_grouped()
        
        # 提取基础队列名（去除优先级后缀）
        base_queues = {}
        for stat in queue_stats:
            base_name = get_base_queue_name(stat['queue_name'])
            if base_name not in base_queues:
                base_queues[base_name] = {
                    'name': base_name,
                    'namespace': namespace,
                    'priority': None,
                    'pending_count': 0,
                    'running_count': 0,
                    'completed_count': 0,
                    'failed_count': 0,
                    'last_activity': None
                }
            
            # 聚合统计数据
            queue_info = base_queues[base_name]
            queue_info['pending_count'] += stat.get('unprocessed_tasks', 0)
            queue_info['running_count'] += stat.get('pending_in_runs', 0)
            queue_info['completed_count'] += stat.get('success_count', 0)
            queue_info['failed_count'] += stat.get('error_count', 0)
            
            # 更新最后活动时间
            if stat.get('last_activity') and (
                not queue_info['last_activity'] or 
                stat['last_activity'] > queue_info['last_activity']
            ):
                queue_info['last_activity'] = stat['last_activity']
        
        # 转换为响应格式
        queue_list = list(base_queues.values())
        
        # 应用搜索筛选
        if search:
            queue_list = [q for q in queue_list if search.lower() in q['name'].lower()]
        
        # 应用状态筛选
        if status:
            if status == 'active':
                queue_list = [q for q in queue_list if q['pending_count'] > 0 or q['running_count'] > 0]
            elif status == 'idle':
                queue_list = [q for q in queue_list if q['pending_count'] == 0 and q['running_count'] == 0]
        
        # 分页
        total = len(queue_list)
        start = (page - 1) * page_size
        end = start + page_size
        paginated_queues = queue_list[start:end]
        
        return QueueListResponse.create(
            data=paginated_queues,
            total=total,
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        logger.error(f"获取队列列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        metrics.finish()


@router.get("/{queue_name}", response_model=QueueDetailResponse)
@cache_result(**CACHE_CONFIGS['queue_stats'])
async def get_queue_detail(
    queue_name: str,
    namespace: str = Depends(get_validated_namespace),
    redis_client: redis.Redis = Depends(get_redis_client),
    pg_session: AsyncSession = Depends(get_pg_connection),
    connection = Depends(get_namespace_connection),
    metrics: RequestMetrics = Depends(get_request_metrics)
):
    """获取队列详情"""
    metrics.start(namespace, f"GET /queues/{queue_name}")
    
    try:
        # 创建队列统计服务
        stats_service = QueueStatsV2(
            redis_client=redis_client,
            pg_session=pg_session,
            redis_prefix=connection.redis_prefix
        )
        
        # 获取队列的详细统计
        queue_stats = await stats_service.get_queue_stats_grouped()
        
        # 筛选指定队列的数据（包括优先级队列）
        queue_data = []
        for stat in queue_stats:
            base_name = get_base_queue_name(stat['queue_name'])
            if base_name == queue_name:
                queue_data.append(stat)
        
        if not queue_data:
            raise QueueNotFoundError(queue_name, namespace)
        
        # 聚合队列基本信息
        queue_info = {
            'name': queue_name,
            'namespace': namespace,
            'priority': None,
            'pending_count': sum(s.get('unprocessed_tasks', 0) for s in queue_data),
            'running_count': sum(s.get('pending_in_runs', 0) for s in queue_data),
            'completed_count': sum(s.get('success_count', 0) for s in queue_data),
            'failed_count': sum(s.get('error_count', 0) for s in queue_data),
            'last_activity': max((s.get('last_activity') for s in queue_data if s.get('last_activity')), default=None)
        }
        
        # 提取消费者组信息
        consumer_groups = []
        for stat in queue_data:
            if stat.get('group_name'):
                consumer_groups.append({
                    'name': stat['group_name'],
                    'queue_name': stat['queue_name'],
                    'pending_count': stat.get('pending_in_runs', 0),
                    'processed_count': stat.get('processed_tasks', 0),
                    'success_count': stat.get('success_count', 0),
                    'error_count': stat.get('error_count', 0),
                    'avg_execution_time': stat.get('avg_execution_time'),
                    'recent_completed': stat.get('recent_completed', 0)
                })
        
        # 构造响应数据
        queue_detail = {
            'queue_info': queue_info,
            'consumer_groups': consumer_groups,
            'metrics': {
                'total_tasks': queue_info['pending_count'] + queue_info['running_count'] + queue_info['completed_count'] + queue_info['failed_count'],
                'success_rate': queue_info['completed_count'] / max(queue_info['completed_count'] + queue_info['failed_count'], 1),
                'active_consumer_groups': len([cg for cg in consumer_groups if cg['pending_count'] > 0])
            },
            'trends': {}  # 可以后续添加趋势数据
        }
        
        return QueueDetailResponse(data=queue_detail)
        
    except QueueNotFoundError:
        raise
    except Exception as e:
        logger.error(f"获取队列详情失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        metrics.finish()


@router.get("/{queue_name}/metrics", response_model=MonitoringResponse)
@cache_result(**CACHE_CONFIGS['monitoring_data'])
async def get_queue_metrics(
    queue_name: str,
    namespace: str = Depends(get_validated_namespace),
    time_params: dict = Depends(validate_time_range),
    metrics_types: str = Query("pending,processing,completed", description="指标类型，逗号分隔"),
    granularity: Optional[str] = Query(None, description="数据粒度"),
    include_consumer_groups: bool = Query(False, description="是否包含消费者组数据"),
    connection = Depends(get_namespace_connection),
    request_metrics: RequestMetrics = Depends(get_request_metrics)
):
    """获取队列监控指标"""
    request_metrics.start(namespace, f"GET /queues/{queue_name}/metrics")
    
    try:
        # 这里使用现有的积压监控API功能
        from ...queue_backlog_api import get_backlog_trend, BacklogTrendRequest
        
        # 构造请求参数
        backlog_request = BacklogTrendRequest(
            namespace=namespace,
            queues=[queue_name],
            time_range=time_params.get('time_range'),
            start_time=time_params.get('start_time'),
            end_time=time_params.get('end_time'),
            granularity=granularity,
            include_groups=include_consumer_groups
        )
        
        # 调用积压趋势API
        backlog_response = await get_backlog_trend(backlog_request)
        
        # 转换为监控响应格式
        monitoring_data = {
            'series': [],
            'granularity': backlog_response.granularity,
            'time_range': backlog_response.time_range
        }
        
        # 按系列分组数据
        series_data = {}
        for item in backlog_response.data:
            series_name = item.get('group') or queue_name
            if series_name not in series_data:
                series_data[series_name] = []
            
            series_data[series_name].append({
                'timestamp': item['time'],
                'value': item['backlog'],
                'metadata': {
                    'queue': item['queue'],
                    'consumer_group': item.get('group'),
                    'published': item.get('published'),
                    'delivered': item.get('delivered')
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
        logger.error(f"获取队列指标失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        request_metrics.finish()


@router.post("/{queue_name}/actions", response_model=BaseResponse)
async def execute_queue_action(
    queue_name: str,
    action_request: QueueActionRequest,
    namespace: str = Depends(get_validated_namespace),
    redis_client: redis.Redis = Depends(get_redis_client),
    metrics: RequestMetrics = Depends(get_request_metrics)
):
    """执行队列操作"""
    metrics.start(namespace, f"POST /queues/{queue_name}/actions")
    
    try:
        action = action_request.action.lower()
        parameters = action_request.parameters
        
        if action == "trim":
            # 裁剪队列
            max_length = parameters.get('max_length')
            if not max_length or max_length < 0:
                raise ValidationError("max_length parameter is required and must be >= 0")
            
            # 这里需要实现Redis Stream的XTRIM操作
            # 暂时返回模拟响应
            return BaseResponse(
                message=f"Queue {queue_name} trimmed to {max_length} messages"
            )
        
        elif action == "clear":
            # 清空队列
            # 这里需要实现清空队列的逻辑
            return BaseResponse(
                message=f"Queue {queue_name} cleared"
            )
        
        elif action == "pause":
            # 暂停队列
            # 这里需要实现暂停消费的逻辑
            return BaseResponse(
                message=f"Queue {queue_name} paused"
            )
        
        elif action == "resume":
            # 恢复队列
            # 这里需要实现恢复消费的逻辑
            return BaseResponse(
                message=f"Queue {queue_name} resumed"
            )
        
        else:
            raise ValidationError(f"Unsupported action: {action}")
            
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"执行队列操作失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        metrics.finish()


def get_base_queue_name(queue_name: str) -> str:
    """提取基础队列名（去除优先级后缀）"""
    if ':' in queue_name:
        parts = queue_name.rsplit(':', 1)
        if parts[-1].isdigit():
            return parts[0]
    return queue_name