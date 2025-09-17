"""
JetTask Monitor 独立后端API服务
完全脱离gradio和integrated_gradio_app依赖

数据库说明：
1. 任务中心元数据库：通过环境变量配置（TASK_CENTER_DB_*）
   - 存储命名空间配置等管理数据
   - 由任务中心自己使用
   
2. JetTask应用数据库：在WebUI中为每个命名空间配置
   - Redis：任务队列存储
   - PostgreSQL：任务结果存储
   - 由JetTask worker使用
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
from pydantic import BaseModel
from sqlalchemy import text
import logging
import traceback

import sys
import os
# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_access import JetTaskDataAccess
from namespace_data_access import get_namespace_data_access
from data_api import router as data_router
from namespace_api import router as namespace_router
from queue_stats_v2 import QueueStatsV2
from queue_backlog_api import router as backlog_router
from redis_monitor_api import router as redis_monitor_router

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建数据访问实例（保留旧的实例，用于兼容）
data_access = JetTaskDataAccess()
# 新的命名空间数据访问
namespace_data_access = get_namespace_data_access()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    try:
        # 1. 初始化JetTask数据访问（用于查询任务数据）
        await data_access.initialize()
        
        # 2. 记录任务中心配置
        from jettask.webui.backend.config import task_center_config
        logger.info("=" * 60)
        logger.info("任务中心配置:")
        logger.info(f"  元数据库: {task_center_config.meta_db_host}:{task_center_config.meta_db_port}/{task_center_config.meta_db_name}")
        logger.info(f"  API服务: {task_center_config.api_host}:{task_center_config.api_port}")
        logger.info(f"  基础URL: {task_center_config.base_url}")
        logger.info("=" * 60)
        
        logger.info("JetTask Monitor API 启动成功")
    except Exception as e:
        logger.error(f"启动失败: {e}")
        traceback.print_exc()
        raise
    
    yield
    
    # 关闭时清理资源
    try:
        await data_access.close()
        logger.info("JetTask Monitor API 关闭完成")
    except Exception as e:
        logger.error(f"关闭时出错: {e}")
        traceback.print_exc()


app = FastAPI(
    title="JetTask Monitor API", 
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该配置具体的前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TimeRangeQuery(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    time_range: Optional[str] = "15m"  # 默认15分钟
    queues: Optional[List[str]] = None
    filters: Optional[List[Dict]] = None  # 筛选条件


class QueueTimelineResponse(BaseModel):
    data: List[Dict]
    granularity: str


class TrimQueueRequest(BaseModel):
    max_length: int


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "JetTask Monitor API",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    
def get_base_queue_name(queue_name: str) -> str:
    """提取基础队列名（去除优先级后缀）"""
    # 检查是否包含优先级后缀（格式: queue_name:priority）
    if ':' in queue_name:
        parts = queue_name.rsplit(':', 1)
        # 检查最后一部分是否是数字（优先级）
        if parts[-1].isdigit():
            return parts[0]
    return queue_name


@app.get("/api/queues/{namespace}")
async def get_queues(namespace: str):
    """获取指定命名空间的队列列表"""
    try:
        # 使用命名空间数据访问
        namespace_access = get_namespace_data_access()
        # 获取指定命名空间的队列信息
        queues_data = await namespace_access.get_queue_stats(namespace)
        return {
            "success": True,
            "data": list(set([get_base_queue_name(q['queue_name']) for q in queues_data]))
        }
    except Exception as e:
        logger.error(f"获取队列列表失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/queue-flow-rates")
async def get_queue_flow_rates(query: TimeRangeQuery):
    """获取单个队列的流量速率（入队、开始执行、完成）"""
    try:
        # 处理时间范围
        now = datetime.now(timezone.utc)
        
        if query.start_time and query.end_time:
            # 使用提供的时间范围
            start_time = query.start_time
            end_time = query.end_time
            logger.info(f"使用自定义时间范围: {start_time} 到 {end_time}")
        else:
            # 根据time_range参数计算时间范围
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
            
            delta = time_range_map.get(query.time_range, timedelta(minutes=15))
            
            # 获取队列的最新任务时间，确保图表包含最新数据
            queue_name = query.queues[0] if query.queues else None
            if queue_name:
                latest_time = await data_access.get_latest_task_time(queue_name)
                if latest_time:
                    # 使用最新任务时间作为结束时间
                    end_time = latest_time.replace(second=59, microsecond=999999)  # 包含整分钟
                    logger.info(f"使用最新任务时间: {latest_time}")
                else:
                    # 如果没有任务，使用当前时间
                    end_time = now.replace(second=0, microsecond=0)
            else:
                end_time = now.replace(second=0, microsecond=0)
            
            start_time = end_time - delta
            logger.info(f"使用预设时间范围 {query.time_range}: {start_time} 到 {end_time}, delta: {delta}")
        
        # 确保有队列名称
        if not query.queues or len(query.queues) == 0:
            return {"data": [], "granularity": "minute"}
        
        # 获取第一个队列的流量速率
        queue_name = query.queues[0]
        data, granularity = await data_access.fetch_queue_flow_rates(
            queue_name, start_time, end_time, query.filters
        )
        
        return {"data": data, "granularity": granularity}
        
    except Exception as e:
        logger.error(f"获取队列流量速率失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# 删除了旧的 /api/queue-timeline 接口，使用 data_api.py 中的新接口


@app.get("/api/stats")
async def get_global_stats():
    """获取全局统计信息"""
    try:
        stats_data = await data_access.fetch_global_stats()
        return {
            "success": True,
            "data": stats_data
        }
    except Exception as e:
        logger.error(f"获取全局统计信息失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/queues/detail")
async def get_queues_detail():
    """获取队列详细信息"""
    try:
        queues_data = await data_access.fetch_queues_data()
        return {
            "success": True,
            "data": queues_data
        }
    except Exception as e:
        logger.error(f"获取队列详细信息失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# 删除了旧的 /api/queue-details 接口，使用 data_api.py 中的新接口


@app.delete("/api/queue/{queue_name}")
async def delete_queue(queue_name: str):
    """删除队列"""
    try:
        # 这里需要实现删除队列的逻辑
        # 暂时返回模拟响应
        logger.info(f"删除队列请求: {queue_name}")
        return {
            "success": True,
            "message": f"队列 {queue_name} 已删除"
        }
    except Exception as e:
        logger.error(f"删除队列失败: {e}")
        traceback.print_exc()
        return {
            "success": False,
            "message": str(e)
        }


@app.post("/api/queue/{queue_name}/trim")
async def trim_queue(queue_name: str, request: TrimQueueRequest):
    """裁剪队列到指定长度"""
    try:
        # 这里需要实现裁剪队列的逻辑
        # 暂时返回模拟响应
        logger.info(f"裁剪队列请求: {queue_name}, 保留 {request.max_length} 条消息")
        return {
            "success": True,
            "message": f"队列 {queue_name} 已裁剪至 {request.max_length} 条消息"
        }
    except Exception as e:
        logger.error(f"裁剪队列失败: {e}")
        traceback.print_exc()
        return {
            "success": False,
            "message": str(e)
        }


@app.post("/api/tasks")
async def get_tasks(request: Request):
    """获取队列的任务列表（支持灵活筛选和时间范围）"""
    try:
        # 解析请求体
        body = await request.json()
        queue_name = body.get('queue_name')
        page = body.get('page', 1)
        page_size = body.get('page_size', 20)
        filters = body.get('filters', [])
        
        # 处理时间范围参数（与 /api/queue-flow-rates 保持一致）
        start_time = body.get('start_time')
        end_time = body.get('end_time')
        time_range = body.get('time_range')
        
        if not queue_name:
            raise HTTPException(status_code=400, detail="queue_name is required")
        
        # 如果提供了时间范围，计算起止时间
        if not start_time or not end_time:
            if time_range:
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
                    # 获取队列的最新任务时间，确保包含最新数据
                    latest_time = await data_access.get_latest_task_time(queue_name)
                    if latest_time:
                        end_time = latest_time.replace(second=59, microsecond=999999)
                    else:
                        end_time = now
                    start_time = end_time - delta
                    logger.info(f"使用时间范围 {time_range}: {start_time} 到 {end_time}")
        
        # 如果有时间范围，将其转换为datetime对象
        if start_time and isinstance(start_time, str):
            start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        if end_time and isinstance(end_time, str):
            end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        
        logger.info(f"获取队列 {queue_name} 的任务列表, 页码: {page}, 每页: {page_size}, 筛选条件: {filters}, 时间范围: {start_time} - {end_time}")
        
        # 调用数据访问层获取真实数据
        result = await data_access.fetch_tasks_with_filters(
            queue_name=queue_name,
            page=page,
            page_size=page_size,
            filters=filters,
            start_time=start_time,
            end_time=end_time
        )
        
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error(f"获取任务列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/task/{task_id}/details")
async def get_task_details(task_id: str, consumer_group: Optional[str] = None):
    """获取单个任务的详细数据（包括task_data和result）
    
    Args:
        task_id: 任务ID (stream_id)
        consumer_group: 消费者组名称（可选，用于精确定位）
    """
    try:
        logger.info(f"获取任务 {task_id} 的详细数据, consumer_group={consumer_group}")
        
        # 调用数据访问层获取任务详细数据
        task_details = await data_access.fetch_task_details(task_id, consumer_group)
        
        if not task_details:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return {
            "success": True,
            "data": task_details
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取任务详细数据失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tasks")
async def get_tasks_legacy(
    queue_name: str,
    page: int = 1,
    page_size: int = 20,
    status: Optional[str] = None,
    task_id: Optional[str] = None,
    worker_id: Optional[str] = None
):
    """获取队列的任务列表（向后兼容旧版本）"""
    try:
        # 构建筛选条件
        filters = []
        if status:
            filters.append({'field': 'status', 'operator': 'eq', 'value': status})
        if task_id:
            filters.append({'field': 'id', 'operator': 'eq', 'value': task_id})
        if worker_id:
            filters.append({'field': 'worker_id', 'operator': 'eq', 'value': worker_id})
        
        logger.info(f"获取队列 {queue_name} 的任务列表, 页码: {page}, 每页: {page_size}")
        
        # 调用数据访问层获取真实数据
        result = await data_access.fetch_tasks_with_filters(
            queue_name=queue_name,
            page=page,
            page_size=page_size,
            filters=filters
        )
        
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error(f"获取任务列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


# ============= 定时任务管理API =============

class ScheduledTaskRequest(BaseModel):
    """定时任务请求模型"""
    namespace: str  # 命名空间
    name: str
    queue_name: str
    task_data: dict
    schedule_type: str  # cron, interval, daily, weekly, monthly
    schedule_config: dict  # 根据schedule_type的不同配置
    is_active: bool = True
    description: Optional[str] = None
    max_retry: int = 3
    timeout: Optional[int] = None


@app.get("/api/scheduled-tasks")
async def get_scheduled_tasks(
    page: int = 1,
    page_size: int = 20,
    search: Optional[str] = None,
    is_active: Optional[bool] = None
):
    """获取定时任务列表（兼容旧版本）"""
    try:
        # 使用真实的数据库操作
        async with data_access.get_session() as session:
            tasks, total = await data_access.fetch_scheduled_tasks(
                session=session,
                page=page,
                page_size=page_size,
                search=search,
                is_active=is_active
            )
        
        return {
            "success": True,
            "data": tasks,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    except Exception as e:
        logger.error(f"获取定时任务列表失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/scheduled-tasks/statistics/{namespace}")
async def get_scheduled_tasks_statistics(namespace: str):
    """获取定时任务统计数据"""
    try:
        async with data_access.AsyncSessionLocal() as session:
            # 获取统计数据，传递命名空间参数
            stats = await data_access.get_scheduled_tasks_statistics(session, namespace)
            return stats
    except Exception as e:
        logger.error(f"获取定时任务统计失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/scheduled-tasks/list")
async def get_scheduled_tasks_with_filters(request: Request):
    """获取定时任务列表（支持高级筛选）"""
    try:
        # 解析请求体
        body = await request.json()
        
        page = body.get('page', 1)
        page_size = body.get('page_size', 20)
        search = body.get('search')
        is_active = body.get('is_active')
        filters = body.get('filters', [])
        time_range = body.get('time_range')
        start_time = body.get('start_time')
        end_time = body.get('end_time')
        
        print(f'{filters=}')
        # 使用真实的数据库操作
        async with data_access.get_session() as session:
            tasks, total = await data_access.fetch_scheduled_tasks(
                session=session,
                page=page,
                page_size=page_size,
                search=search,
                is_active=is_active,
                filters=filters,
                time_range=time_range,
                start_time=start_time,
                end_time=end_time
            )
        
        return {
            "success": True,
            "data": tasks,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    except Exception as e:
        logger.error(f"获取定时任务列表失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


def validate_schedule_config(schedule_type: str, schedule_config: dict):
    """验证调度配置"""
    if schedule_type == 'interval':
        if 'seconds' in schedule_config:
            seconds = schedule_config.get('seconds')
            if seconds is None or seconds <= 0:
                raise ValueError(f"间隔时间必须大于0秒，当前值: {seconds}")
            if seconds < 1:
                raise ValueError(f"间隔时间不能小于1秒，当前值: {seconds}秒。小于1秒的高频任务可能影响系统性能")
        elif 'minutes' in schedule_config:
            minutes = schedule_config.get('minutes')
            if minutes is None or minutes <= 0:
                raise ValueError(f"间隔时间必须大于0分钟，当前值: {minutes}")
        else:
            raise ValueError("interval类型的任务必须指定seconds或minutes")
    elif schedule_type == 'cron':
        if 'cron_expression' not in schedule_config:
            raise ValueError("cron类型的任务必须指定cron_expression")
        # 可以添加cron表达式格式验证

@app.post("/api/scheduled-tasks")
async def create_scheduled_task(request: ScheduledTaskRequest):
    """创建定时任务"""
    try:
        # 验证调度配置
        validate_schedule_config(request.schedule_type, request.schedule_config)
        
        # 使用真实的数据库操作
        task_data = {
            "namespace": request.namespace,
            "name": request.name,
            "queue_name": request.queue_name,
            "task_data": request.task_data,
            "schedule_type": request.schedule_type,
            "schedule_config": request.schedule_config,
            "is_active": request.is_active,
            "description": request.description,
            "max_retry": request.max_retry,
            "timeout": request.timeout
        }
        
        async with data_access.get_session() as session:
            task = await data_access.create_scheduled_task(session, task_data)
        
        return {
            "success": True,
            "data": task,
            "message": "定时任务创建成功"
        }
    except Exception as e:
        logger.error(f"创建定时任务失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/scheduled-tasks/{task_id}")
async def update_scheduled_task(task_id: str, request: ScheduledTaskRequest):
    """更新定时任务"""
    try:
        # 验证调度配置
        validate_schedule_config(request.schedule_type, request.schedule_config)
        
        # 使用真实的数据库操作
        task_data = {
            "namespace": request.namespace,
            "name": request.name,
            "queue_name": request.queue_name,
            "task_data": request.task_data,
            "schedule_type": request.schedule_type,
            "schedule_config": request.schedule_config,
            "is_active": request.is_active,
            "description": request.description,
            "max_retry": request.max_retry,
            "timeout": request.timeout
        }
        
        async with data_access.get_session() as session:
            task = await data_access.update_scheduled_task(session, task_id, task_data)
        
        return {
            "success": True,
            "data": task,
            "message": "定时任务更新成功"
        }
    except Exception as e:
        logger.error(f"更新定时任务失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/scheduled-tasks/{task_id}")
async def delete_scheduled_task(task_id: str):
    """删除定时任务"""
    try:
        # 使用真实的数据库操作
        async with data_access.get_session() as session:
            success = await data_access.delete_scheduled_task(session, task_id)
        
        if success:
            return {
                "success": True,
                "message": f"定时任务 {task_id} 已删除"
            }
        else:
            raise HTTPException(status_code=404, detail="定时任务不存在")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除定时任务失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/scheduled-tasks/{task_id}/toggle")
async def toggle_scheduled_task(task_id: str):
    """启用/禁用定时任务"""
    try:
        # 使用真实的数据库操作
        async with data_access.get_session() as session:
            task = await data_access.toggle_scheduled_task(session, task_id)
        
        if task:
            return {
                "success": True,
                "data": {
                    "id": task["id"],
                    "is_active": task["enabled"]  # 映射 enabled 到 is_active
                },
                "message": "定时任务状态已更新"
            }
        else:
            raise HTTPException(status_code=404, detail="定时任务不存在")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"切换定时任务状态失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/scheduled-tasks/{scheduled_task_id}/execute")
async def execute_scheduled_task_now(scheduled_task_id: str):
    """立即执行定时任务"""
    try:
        # 使用真实的数据库操作获取任务信息
        async with data_access.get_session() as session:
            # 获取定时任务详情
            task = await data_access.get_scheduled_task_by_id(session, scheduled_task_id)
            
            if not task:
                raise HTTPException(status_code=404, detail=f"定时任务 {scheduled_task_id} 不存在")
            
            # 检查任务是否启用
            if not task.get('enabled', False):
                raise HTTPException(status_code=400, detail="任务已禁用，无法执行")
            
            # 复用现有的任务发送机制
            import sys
            import os
            # 添加jettask到Python路径
            jettask_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            if jettask_path not in sys.path:
                sys.path.insert(0, jettask_path)
            

            from jettask import Jettask
            
            # 获取任务的命名空间
            namespace = task.get('namespace', 'default')
            
            # 从命名空间数据访问获取该命名空间的配置
            from namespace_data_access import get_namespace_data_access
            namespace_access = get_namespace_data_access()
            conn = await namespace_access.manager.get_connection(namespace)
            
            # 获取该命名空间的Redis和PostgreSQL URL
            redis_url = conn.redis_config.get('url') if conn.redis_config else None
            pg_url = conn.pg_config.get('url') if conn.pg_config else None
            
            if not redis_url:
                raise HTTPException(status_code=500, detail=f"命名空间 {namespace} 没有配置Redis")
            
            # 创建Jettask实例，使用正确的命名空间
            jettask_app = Jettask(
                redis_url=redis_url,
                pg_url=pg_url,
                redis_prefix=namespace  # 使用命名空间作为Redis前缀
            )
            
            print(f"触发定时任务 {scheduled_task_id} (命名空间: {namespace}), 任务信息: {task}")
            # 准备任务参数
            task_args = task.get('task_args', [])
            task_kwargs = task.get('task_kwargs', {})
            
            # 使用TaskMessage和send_tasks发送任务
            from jettask.core.message import TaskMessage
            
            # 添加_task_name到kwargs中用于路由
            task_kwargs['_task_name'] = task['task_name']
            
            # 创建TaskMessage
            task_msg = TaskMessage(
                queue=task['queue_name'],
                args=task_args,
                kwargs=task_kwargs,
                scheduled_task_id=scheduled_task_id
            )
            
            # 发送任务
            event_ids = await jettask_app.send_tasks([task_msg])
            event_id = event_ids[0] if event_ids else None
    
            
            # 记录执行历史
            logger.info(f"定时任务 {scheduled_task_id} (命名空间: {namespace}) 已手动触发，event_id: {event_id}")
            
            return {
                "success": True,
                "message": f"任务已成功触发",
                "event_id": str(event_id) if event_id else None,
                "task_name": task['task_name'],
                "queue_name": task['queue_name'],
                "namespace": namespace
            }
            
    except HTTPException:
        raise
    except Exception as e:
        import traceback    
        traceback.print_exc()
        logger.error(f"执行定时任务失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/scheduled-tasks/{task_id}/history")
async def get_scheduled_task_history(
    task_id: str,
    page: int = 1,
    page_size: int = 20
):
    """获取定时任务执行历史"""
    try:
        # 使用真实的数据库操作
        async with data_access.get_session() as session:
            history, total = await data_access.fetch_task_execution_history(
                session=session,
                task_id=task_id,
                page=page,
                page_size=page_size
            )
        
        return {
            "success": True,
            "data": history,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    except Exception as e:
        logger.error(f"获取定时任务执行历史失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/scheduled-tasks/{task_id}/execution-trend")
async def get_scheduled_task_execution_trend(
    task_id: str,
    time_range: str = "7d"
):
    """获取定时任务执行趋势"""
    try:
        # 使用真实的数据库操作
        async with data_access.get_session() as session:
            data = await data_access.fetch_task_execution_trend(
                session=session,
                task_id=task_id,
                time_range=time_range
            )
        
        return {
            "success": True,
            "data": data,
            "time_range": time_range
        }
    except Exception as e:
        logger.error(f"获取定时任务执行趋势失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ============= 命名空间管理API (任务中心) =============

# 导入命名空间API路由
from jettask.webui.backend.namespace_api import router as namespace_router

# 注册命名空间路由
app.include_router(namespace_router)
app.include_router(data_router)
app.include_router(backlog_router)
app.include_router(redis_monitor_router)







# ============= 告警管理API =============

class AlertRuleRequest(BaseModel):
    """告警规则请求模型"""
    name: str
    rule_type: str  # queue_size, error_rate, response_time, custom
    target_queues: List[str]  # 监控的队列列表
    condition: dict  # 触发条件配置
    action_type: str  # webhook, email, sms
    action_config: dict  # 通知配置
    is_active: bool = True
    description: Optional[str] = None
    check_interval: int = 60  # 检查间隔（秒）


@app.get("/api/alert-rules")
async def get_alert_rules(
    page: int = 1,
    page_size: int = 20,
    is_active: Optional[bool] = None
):
    """获取告警规则列表"""
    try:
        # 模拟数据
        rules = [
            {
                "id": "rule_001",
                "name": "队列积压告警",
                "rule_type": "queue_size",
                "target_queues": ["order_queue", "payment_queue"],
                "condition": {"threshold": 1000, "operator": ">"},
                "action_type": "webhook",
                "action_config": {"url": "https://example.com/webhook"},
                "is_active": True,
                "last_triggered": "2025-08-31T14:30:00Z",
                "created_at": "2025-08-01T10:00:00Z",
                "description": "当队列积压超过1000时触发告警"
            },
            {
                "id": "rule_002",
                "name": "高错误率告警",
                "rule_type": "error_rate",
                "target_queues": ["*"],  # 所有队列
                "condition": {"threshold": 0.1, "operator": ">", "window": 300},
                "action_type": "email",
                "action_config": {"recipients": ["admin@example.com"]},
                "is_active": True,
                "last_triggered": None,
                "created_at": "2025-08-15T14:00:00Z",
                "description": "5分钟内错误率超过10%时告警"
            },
            {
                "id": "rule_003",
                "name": "响应时间告警",
                "rule_type": "response_time",
                "target_queues": ["api_queue"],
                "condition": {"threshold": 5000, "operator": ">", "percentile": 95},
                "action_type": "webhook",
                "action_config": {"url": "https://slack.com/webhook"},
                "is_active": False,
                "last_triggered": "2025-08-30T09:00:00Z",
                "created_at": "2025-07-01T08:00:00Z",
                "description": "95分位响应时间超过5秒时告警"
            }
        ]
        
        # 过滤
        if is_active is not None:
            rules = [r for r in rules if r["is_active"] == is_active]
        
        # 分页
        total = len(rules)
        start = (page - 1) * page_size
        end = start + page_size
        paginated_rules = rules[start:end]
        
        return {
            "success": True,
            "data": paginated_rules,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    except Exception as e:
        logger.error(f"获取告警规则列表失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/alert-rules")
async def create_alert_rule(request: AlertRuleRequest):
    """创建告警规则"""
    try:
        rule = {
            "id": f"rule_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "name": request.name,
            "rule_type": request.rule_type,
            "target_queues": request.target_queues,
            "condition": request.condition,
            "action_type": request.action_type,
            "action_config": request.action_config,
            "is_active": request.is_active,
            "description": request.description,
            "check_interval": request.check_interval,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        return {
            "success": True,
            "data": rule,
            "message": "告警规则创建成功"
        }
    except Exception as e:
        logger.error(f"创建告警规则失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/alert-rules/{rule_id}")
async def update_alert_rule(rule_id: str, request: AlertRuleRequest):
    """更新告警规则"""
    try:
        rule = {
            "id": rule_id,
            "name": request.name,
            "rule_type": request.rule_type,
            "target_queues": request.target_queues,
            "condition": request.condition,
            "action_type": request.action_type,
            "action_config": request.action_config,
            "is_active": request.is_active,
            "description": request.description,
            "check_interval": request.check_interval,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        return {
            "success": True,
            "data": rule,
            "message": "告警规则更新成功"
        }
    except Exception as e:
        logger.error(f"更新告警规则失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/alert-rules/{rule_id}")
async def delete_alert_rule(rule_id: str):
    """删除告警规则"""
    try:
        return {
            "success": True,
            "message": f"告警规则 {rule_id} 已删除"
        }
    except Exception as e:
        logger.error(f"删除告警规则失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/alert-rules/{rule_id}/toggle")
async def toggle_alert_rule(rule_id: str):
    """启用/禁用告警规则"""
    try:
        return {
            "success": True,
            "data": {
                "id": rule_id,
                "is_active": True  # 切换后的状态
            },
            "message": "告警规则状态已更新"
        }
    except Exception as e:
        logger.error(f"切换告警规则状态失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/alert-rules/{rule_id}/history")
async def get_alert_history(
    rule_id: str,
    page: int = 1,
    page_size: int = 20
):
    """获取告警触发历史"""
    try:
        # 模拟告警历史数据
        history = [
            {
                "id": f"alert_{i}",
                "rule_id": rule_id,
                "triggered_at": (datetime.now(timezone.utc) - timedelta(hours=i*2)).isoformat(),
                "resolved_at": (datetime.now(timezone.utc) - timedelta(hours=i*2-1)).isoformat() if i % 2 == 0 else None,
                "status": "resolved" if i % 2 == 0 else "active",
                "trigger_value": 1200 + i * 100,
                "notification_sent": True,
                "notification_response": {"status": "success"}
            }
            for i in range(1, 11)
        ]
        
        # 分页
        total = len(history)
        start = (page - 1) * page_size
        end = start + page_size
        paginated_history = history[start:end]
        
        return {
            "success": True,
            "data": paginated_history,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    except Exception as e:
        logger.error(f"获取告警历史失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/alert-rules/{rule_id}/test")
async def test_alert_rule(rule_id: str):
    """测试告警规则（发送测试通知）"""
    try:
        # 模拟测试告警
        return {
            "success": True,
            "message": "测试通知已发送",
            "data": {
                "rule_id": rule_id,
                "test_time": datetime.now(timezone.utc).isoformat(),
                "notification_result": {
                    "status": "success",
                    "response": {"code": 200, "message": "OK"}
                }
            }
        }
    except Exception as e:
        logger.error(f"测试告警规则失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ===== 新增API v2: 支持消费者组和优先级队列 =====

# 新的简洁路径
@app.get("/api/data/queue-stats")
async def get_queue_stats_simplified(
    namespace: str = "default",
    queue: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    time_range: Optional[str] = None
):
    """
    获取队列统计信息 - 简化的API路径
    
    参数:
    - namespace: 命名空间，默认为'default'
    - queue: 可选，筛选特定队列
    - start_time: 开始时间
    - end_time: 结束时间
    - time_range: 时间范围（如'15m', '1h', '24h'）
    """
    # 直接调用原有的函数
    return await get_queue_stats_v2(namespace, queue, start_time, end_time, time_range)

# 保留原有路径以保证兼容性
@app.get("/api/v2/namespaces/{namespace}/queues/stats")
async def get_queue_stats_v2(
    namespace: str,
    queue: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    time_range: Optional[str] = None
):
    """
    获取队列统计信息v2 - 支持消费者组详情和优先级队列
    
    参数:
    - queue: 可选，筛选特定队列
    - start_time: 开始时间
    - end_time: 结束时间
    - time_range: 时间范围（如'15m', '1h', '24h'）
    """
    try:
        # 获取命名空间连接
        conn = await namespace_data_access.manager.get_connection(namespace)
        
        # 获取Redis客户端
        redis_client = await conn.get_redis_client(decode=False)
        
        # 获取PostgreSQL会话（可选）
        pg_session = None
        if conn.AsyncSessionLocal:
            pg_session = conn.AsyncSessionLocal()
        
        try:
            # 创建统计服务实例
            stats_service = QueueStatsV2(
                redis_client=redis_client,
                pg_session=pg_session,
                redis_prefix=conn.redis_prefix
            )
            
            # 处理时间筛选参数
            time_filter = None
            if time_range or start_time or end_time:
                time_filter = {}
                
                # 如果提供了time_range，计算开始和结束时间
                if time_range and time_range != 'custom':
                    now = datetime.now(timezone.utc)
                    if time_range.endswith('m'):
                        minutes = int(time_range[:-1])
                        time_filter['start_time'] = now - timedelta(minutes=minutes)
                        time_filter['end_time'] = now
                    elif time_range.endswith('h'):
                        hours = int(time_range[:-1])
                        time_filter['start_time'] = now - timedelta(hours=hours)
                        time_filter['end_time'] = now
                    elif time_range.endswith('d'):
                        days = int(time_range[:-1])
                        time_filter['start_time'] = now - timedelta(days=days)
                        time_filter['end_time'] = now
                else:
                    # 使用提供的start_time和end_time
                    if start_time:
                        time_filter['start_time'] = start_time
                    if end_time:
                        time_filter['end_time'] = end_time
            
            # 获取队列统计（使用分组格式）
            stats = await stats_service.get_queue_stats_grouped(time_filter)
            
            # 如果指定了队列筛选，则过滤结果
            if queue:
                stats = [s for s in stats if s['queue_name'] == queue]
            
            return {
                "success": True,
                "data": stats
            }
            
        finally:
            if pg_session:
                await pg_session.close()
            await redis_client.aclose()
            
    except Exception as e:
        logger.error(f"获取队列统计v2失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v2/namespaces/{namespace}/tasks")
async def get_tasks_v2(namespace: str, request: Request):
    """
    获取任务列表v2 - 支持tasks和task_runs表连表查询
    """
    try:
        # 解析请求体
        body = await request.json()
        queue_name = body.get('queue_name')
        page = body.get('page', 1)
        page_size = body.get('page_size', 20)
        filters = body.get('filters', [])
        
        if not queue_name:
            raise HTTPException(status_code=400, detail="queue_name is required")
        
        # 获取命名空间连接
        conn = await namespace_data_access.manager.get_connection(namespace)
        
        if not conn.AsyncSessionLocal:
            raise HTTPException(status_code=400, detail="PostgreSQL not configured for this namespace")
        
        # async with conn.AsyncSessionLocal() as session:
        #     result = await get_task_details_v2(
        #         pg_session=session,
        #         queue_name=queue_name,
        #         page=page,
        #         page_size=page_size,
        #         filters=filters
        #     )
            
        return {
            "success": True,
            "data": {"error": "get_task_details_v2 not implemented"}
        }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取任务列表v2失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v2/namespaces/{namespace}/consumer-groups/{group_name}/stats")
async def get_consumer_group_stats(namespace: str, group_name: str):
    """
    获取特定消费者组的详细统计
    """
    try:
        # 获取命名空间连接
        conn = await namespace_data_access.manager.get_connection(namespace)
        
        # 获取PostgreSQL会话
        if not conn.AsyncSessionLocal:
            raise HTTPException(status_code=400, detail="PostgreSQL not configured for this namespace")
        
        async with conn.AsyncSessionLocal() as session:
            # 查询消费者组的执行统计
            query = text("""
                WITH group_stats AS (
                    SELECT 
                        tr.consumer_group,
                        tr.task_name,
                        COUNT(*) as total_tasks,
                        COUNT(CASE WHEN tr.status = 'success' THEN 1 END) as success_count,
                        COUNT(CASE WHEN tr.status = 'failed' THEN 1 END) as failed_count,
                        COUNT(CASE WHEN tr.status = 'running' THEN 1 END) as running_count,
                        AVG(tr.execution_time) as avg_execution_time,
                        MIN(tr.execution_time) as min_execution_time,
                        MAX(tr.execution_time) as max_execution_time,
                        AVG(tr.duration) as avg_duration,
                        MIN(tr.started_at) as first_task_time,
                        MAX(tr.completed_at) as last_task_time
                    FROM task_runs tr
                    WHERE tr.consumer_group = :group_name
                        AND tr.started_at > NOW() - INTERVAL '24 hours'
                    GROUP BY tr.consumer_group, tr.task_name
                ),
                hourly_stats AS (
                    SELECT 
                        DATE_TRUNC('hour', tr.started_at) as hour,
                        COUNT(*) as task_count,
                        AVG(tr.execution_time) as avg_exec_time
                    FROM task_runs tr
                    WHERE tr.consumer_group = :group_name
                        AND tr.started_at > NOW() - INTERVAL '24 hours'
                    GROUP BY DATE_TRUNC('hour', tr.started_at)
                    ORDER BY hour
                )
                SELECT 
                    (SELECT row_to_json(gs) FROM group_stats gs) as summary,
                    (SELECT json_agg(hs) FROM hourly_stats hs) as hourly_trend
            """)
            
            result = await session.execute(query, {'group_name': group_name})
            row = result.fetchone()
            
            if not row or not row.summary:
                return {
                    "success": True,
                    "data": {
                        "group_name": group_name,
                        "summary": {},
                        "hourly_trend": []
                    }
                }
            
            return {
                "success": True,
                "data": {
                    "group_name": group_name,
                    "summary": row.summary,
                    "hourly_trend": row.hourly_trend or []
                }
            }
            
    except Exception as e:
        logger.error(f"获取消费者组统计失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ============= Stream积压监控API =============

@app.get("/api/stream-backlog/{namespace}")
async def get_stream_backlog(
    namespace: str,
    stream_name: Optional[str] = None,
    hours: int = 24
):
    """
    获取Stream积压监控数据
    
    Args:
        namespace: 命名空间
        stream_name: 可选，指定stream名称
        hours: 查询最近多少小时的数据（默认24小时）
    """
    try:
        from datetime import datetime, timedelta, timezone
        
        # 计算时间范围
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=hours)
        
        async with data_access.AsyncSessionLocal() as session:
            # 构建查询
            if stream_name:
                query = text("""
                    SELECT 
                        stream_name,
                        consumer_group,
                        last_published_offset,
                        last_delivered_offset,
                        last_acked_offset,
                        pending_count,
                        backlog_undelivered,
                        backlog_unprocessed,
                        created_at
                    FROM stream_backlog_monitor
                    WHERE namespace = :namespace
                        AND stream_name = :stream_name
                        AND created_at >= :start_time
                        AND created_at <= :end_time
                    ORDER BY created_at DESC
                    LIMIT 1000
                """)
                params = {
                    'namespace': namespace,
                    'stream_name': stream_name,
                    'start_time': start_time,
                    'end_time': end_time
                }
            else:
                # 获取最新的所有stream数据
                query = text("""
                    SELECT DISTINCT ON (stream_name, consumer_group)
                        stream_name,
                        consumer_group,
                        last_published_offset,
                        last_delivered_offset,
                        last_acked_offset,
                        pending_count,
                        backlog_undelivered,
                        backlog_unprocessed,
                        created_at
                    FROM stream_backlog_monitor
                    WHERE namespace = :namespace
                        AND created_at >= :start_time
                    ORDER BY stream_name, consumer_group, created_at DESC
                """)
                params = {
                    'namespace': namespace,
                    'start_time': start_time
                }
            
            result = await session.execute(query, params)
            rows = result.fetchall()
            
            # 格式化数据
            data = []
            for row in rows:
                data.append({
                    'stream_name': row.stream_name,
                    'consumer_group': row.consumer_group,
                    'last_published_offset': row.last_published_offset,
                    'last_delivered_offset': row.last_delivered_offset,
                    'last_acked_offset': row.last_acked_offset,
                    'pending_count': row.pending_count,
                    'backlog_undelivered': row.backlog_undelivered,
                    'backlog_unprocessed': row.backlog_unprocessed,
                    'created_at': row.created_at.isoformat() if row.created_at else None
                })
            
            return {
                'success': True,
                'data': data,
                'total': len(data)
            }
            
    except Exception as e:
        logger.error(f"获取Stream积压监控数据失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stream-backlog/{namespace}/summary")
async def get_stream_backlog_summary(namespace: str):
    """
    获取Stream积压监控汇总数据
    
    Args:
        namespace: 命名空间
    """
    try:
        async with data_access.AsyncSessionLocal() as session:
            # 获取最新的汇总数据
            query = text("""
                WITH latest_data AS (
                    SELECT DISTINCT ON (stream_name, consumer_group)
                        stream_name,
                        consumer_group,
                        backlog_undelivered,
                        backlog_unprocessed,
                        pending_count
                    FROM stream_backlog_monitor
                    WHERE namespace = :namespace
                        AND created_at >= NOW() - INTERVAL '1 hour'
                    ORDER BY stream_name, consumer_group, created_at DESC
                )
                SELECT 
                    COUNT(DISTINCT stream_name) as total_streams,
                    COUNT(DISTINCT consumer_group) as total_groups,
                    SUM(backlog_unprocessed) as total_backlog,
                    SUM(pending_count) as total_pending,
                    MAX(backlog_unprocessed) as max_backlog
                FROM latest_data
            """)
            
            result = await session.execute(query, {'namespace': namespace})
            row = result.fetchone()
            
            if row:
                return {
                    'success': True,
                    'data': {
                        'total_streams': row.total_streams or 0,
                        'total_groups': row.total_groups or 0,
                        'total_backlog': row.total_backlog or 0,
                        'total_pending': row.total_pending or 0,
                        'max_backlog': row.max_backlog or 0
                    }
                }
            else:
                return {
                    'success': True,
                    'data': {
                        'total_streams': 0,
                        'total_groups': 0,
                        'total_backlog': 0,
                        'total_pending': 0,
                        'max_backlog': 0
                    }
                }
                
    except Exception as e:
        logger.error(f"获取Stream积压监控汇总失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


def run_server():
    """运行 Web UI 服务器"""
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8001,
        log_level="info",
        reload=False
    )

if __name__ == "__main__":
    run_server()