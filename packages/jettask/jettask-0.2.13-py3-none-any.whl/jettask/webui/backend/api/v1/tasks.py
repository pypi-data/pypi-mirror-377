"""
Task management API v1
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis

from dependencies import (
    get_validated_namespace, get_pg_connection, get_redis_client,
    validate_page_params, validate_time_range, get_request_metrics, RequestMetrics
)
from models.requests import TaskListRequest, TaskActionRequest
from models.responses import TaskListResponse, TaskDetailResponse, BaseResponse
from core.cache import cache_result, CACHE_CONFIGS
from core.exceptions import TaskNotFoundError, ValidationError
from data_access import JetTaskDataAccess
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/search", response_model=TaskListResponse)
async def search_tasks(
    request: TaskListRequest,
    namespace: str = Depends(get_validated_namespace),
    pg_session: AsyncSession = Depends(get_pg_connection),
    metrics: RequestMetrics = Depends(get_request_metrics)
):
    """搜索任务（支持复杂筛选条件）"""
    metrics.start(namespace, "POST /tasks/search")
    
    try:
        # 创建数据访问实例
        data_access = JetTaskDataAccess()
        
        # 转换筛选条件
        filters = []
        for condition in request.filters:
            filters.append({
                'field': condition.field,
                'operator': condition.operator.value,
                'value': condition.value
            })
        
        # 添加基础筛选条件
        if request.queue_name:
            filters.append({'field': 'queue', 'operator': 'eq', 'value': request.queue_name})
        if request.status:
            filters.append({'field': 'status', 'operator': 'eq', 'value': request.status})
        if request.consumer_group:
            filters.append({'field': 'consumer_group', 'operator': 'eq', 'value': request.consumer_group})
        if request.worker_id:
            filters.append({'field': 'worker_id', 'operator': 'eq', 'value': request.worker_id})
        if request.task_name:
            filters.append({'field': 'task_name', 'operator': 'like', 'value': f"%{request.task_name}%"})
        
        # 执行查询
        result = await data_access.fetch_tasks_with_filters(
            queue_name=request.queue_name or "",
            page=request.page,
            page_size=request.page_size,
            filters=filters,
            start_time=request.start_time,
            end_time=request.end_time,
            sort_field=request.sort_field,
            sort_order=request.sort_order.value if request.sort_order else 'desc',
            search=request.search
        )
        
        return TaskListResponse.create(
            data=result['data'],
            total=result['total'],
            page=request.page,
            page_size=request.page_size
        )
        
    except Exception as e:
        logger.error(f"搜索任务失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        metrics.finish()


@router.get("", response_model=TaskListResponse)
@cache_result(**CACHE_CONFIGS['task_details'])
async def list_tasks(
    namespace: str = Depends(get_validated_namespace),
    queue_name: Optional[str] = Query(None, description="队列名称"),
    status: Optional[str] = Query(None, description="任务状态"),
    consumer_group: Optional[str] = Query(None, description="消费者组"),
    worker_id: Optional[str] = Query(None, description="工作者ID"),
    task_name: Optional[str] = Query(None, description="任务名称"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
    sort_field: Optional[str] = Query("created_at", description="排序字段"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="排序方向"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    time_params: dict = Depends(validate_time_range),
    pg_session: AsyncSession = Depends(get_pg_connection),
    metrics: RequestMetrics = Depends(get_request_metrics)
):
    """获取任务列表（简单查询）"""
    metrics.start(namespace, "GET /tasks")
    
    try:
        # 创建数据访问实例
        data_access = JetTaskDataAccess()
        
        # 构建筛选条件
        filters = []
        if status:
            filters.append({'field': 'status', 'operator': 'eq', 'value': status})
        if consumer_group:
            filters.append({'field': 'consumer_group', 'operator': 'eq', 'value': consumer_group})
        if worker_id:
            filters.append({'field': 'worker_id', 'operator': 'eq', 'value': worker_id})
        if task_name:
            filters.append({'field': 'task_name', 'operator': 'like', 'value': f"%{task_name}%"})
        
        # 执行查询
        result = await data_access.fetch_tasks_with_filters(
            queue_name=queue_name or "",
            page=page,
            page_size=page_size,
            filters=filters,
            start_time=time_params.get('start_time'),
            end_time=time_params.get('end_time'),
            sort_field=sort_field,
            sort_order=sort_order,
            search=search
        )
        
        return TaskListResponse.create(
            data=result['data'],
            total=result['total'],
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        logger.error(f"获取任务列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        metrics.finish()


@router.get("/{task_id}", response_model=TaskDetailResponse)
@cache_result(**CACHE_CONFIGS['task_details'])
async def get_task_detail(
    task_id: str,
    namespace: str = Depends(get_validated_namespace),
    consumer_group: Optional[str] = Query(None, description="消费者组"),
    pg_session: AsyncSession = Depends(get_pg_connection),
    metrics: RequestMetrics = Depends(get_request_metrics)
):
    """获取任务详情"""
    metrics.start(namespace, f"GET /tasks/{task_id}")
    
    try:
        # 创建数据访问实例
        data_access = JetTaskDataAccess()
        
        # 获取任务详情
        task_detail = await data_access.fetch_task_details(task_id, consumer_group)
        
        if not task_detail:
            raise TaskNotFoundError(task_id)
        
        return TaskDetailResponse(data=task_detail)
        
    except TaskNotFoundError:
        raise
    except Exception as e:
        logger.error(f"获取任务详情失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        metrics.finish()


@router.post("/actions", response_model=BaseResponse)
async def execute_task_actions(
    action_request: TaskActionRequest,
    namespace: str = Depends(get_validated_namespace),
    redis_client: redis.Redis = Depends(get_redis_client),
    pg_session: AsyncSession = Depends(get_pg_connection),
    metrics: RequestMetrics = Depends(get_request_metrics)
):
    """批量执行任务操作"""
    metrics.start(namespace, "POST /tasks/actions")
    
    try:
        action = action_request.action.lower()
        task_ids = action_request.task_ids
        parameters = action_request.parameters
        
        if not task_ids:
            raise ValidationError("task_ids cannot be empty")
        
        # 验证任务ID格式
        for task_id in task_ids:
            if not task_id or not isinstance(task_id, str):
                raise ValidationError(f"Invalid task_id: {task_id}")
        
        success_count = 0
        failed_count = 0
        errors = []
        
        if action == "retry":
            # 重试失败任务
            for task_id in task_ids:
                try:
                    # 这里需要实现重试逻辑
                    # 1. 检查任务状态是否为failed
                    # 2. 重新入队任务
                    # 3. 更新任务状态
                    success_count += 1
                except Exception as e:
                    failed_count += 1
                    errors.append(f"Task {task_id}: {str(e)}")
        
        elif action == "cancel":
            # 取消待处理任务
            for task_id in task_ids:
                try:
                    # 这里需要实现取消逻辑
                    # 1. 检查任务状态
                    # 2. 从队列中移除
                    # 3. 更新任务状态为cancelled
                    success_count += 1
                except Exception as e:
                    failed_count += 1
                    errors.append(f"Task {task_id}: {str(e)}")
        
        elif action == "delete":
            # 删除任务记录
            for task_id in task_ids:
                try:
                    # 这里需要实现删除逻辑
                    # 1. 从数据库删除任务记录
                    # 2. 清理相关数据
                    success_count += 1
                except Exception as e:
                    failed_count += 1
                    errors.append(f"Task {task_id}: {str(e)}")
        
        else:
            raise ValidationError(f"Unsupported action: {action}")
        
        # 构造响应消息
        message = f"Action '{action}' executed: {success_count} succeeded"
        if failed_count > 0:
            message += f", {failed_count} failed"
        
        response_data = {
            'action': action,
            'total_tasks': len(task_ids),
            'success_count': success_count,
            'failed_count': failed_count,
            'errors': errors[:10]  # 只返回前10个错误
        }
        
        return BaseResponse(
            message=message,
            data=response_data
        )
        
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"执行任务操作失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        metrics.finish()


@router.get("/{task_id}/logs")
async def get_task_logs(
    task_id: str,
    namespace: str = Depends(get_validated_namespace),
    lines: int = Query(100, ge=1, le=1000, description="日志行数"),
    follow: bool = Query(False, description="是否跟踪日志"),
    pg_session: AsyncSession = Depends(get_pg_connection),
    metrics: RequestMetrics = Depends(get_request_metrics)
):
    """获取任务执行日志"""
    metrics.start(namespace, f"GET /tasks/{task_id}/logs")
    
    try:
        # 这里需要实现日志获取逻辑
        # 1. 从数据库或日志系统获取任务执行日志
        # 2. 支持实时日志跟踪（WebSocket）
        
        # 暂时返回模拟数据
        logs = [
            {"timestamp": "2025-09-08T12:00:00Z", "level": "INFO", "message": "Task started"},
            {"timestamp": "2025-09-08T12:00:01Z", "level": "DEBUG", "message": "Processing data..."},
            {"timestamp": "2025-09-08T12:00:02Z", "level": "INFO", "message": "Task completed successfully"}
        ]
        
        return BaseResponse(
            data={
                "task_id": task_id,
                "logs": logs[-lines:],
                "total_lines": len(logs),
                "truncated": len(logs) > lines
            }
        )
        
    except Exception as e:
        logger.error(f"获取任务日志失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        metrics.finish()


@router.get("/statistics/summary")
async def get_task_statistics(
    namespace: str = Depends(get_validated_namespace),
    queue_name: Optional[str] = Query(None, description="队列名称"),
    time_params: dict = Depends(validate_time_range),
    pg_session: AsyncSession = Depends(get_pg_connection),
    metrics: RequestMetrics = Depends(get_request_metrics)
):
    """获取任务统计摘要"""
    metrics.start(namespace, "GET /tasks/statistics/summary")
    
    try:
        # 这里需要实现统计查询逻辑
        # 1. 按状态统计任务数量
        # 2. 按时间统计任务趋势
        # 3. 按队列统计任务分布
        # 4. 计算成功率、平均执行时间等指标
        
        # 暂时返回模拟数据
        statistics = {
            "total_tasks": 12345,
            "by_status": {
                "pending": 123,
                "running": 45,
                "completed": 11000,
                "failed": 1177
            },
            "by_queue": {
                "shared_queue": 8000,
                "priority_queue": 3000,
                "background_queue": 1345
            },
            "metrics": {
                "success_rate": 0.905,
                "avg_execution_time": 12.34,
                "tasks_per_hour": 234.5
            },
            "trends": {
                "hourly_counts": [],
                "error_rates": []
            }
        }
        
        return BaseResponse(data=statistics)
        
    except Exception as e:
        logger.error(f"获取任务统计失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        metrics.finish()