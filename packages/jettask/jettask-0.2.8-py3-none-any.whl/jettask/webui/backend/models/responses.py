"""
Response models for JetTask WebUI Backend
"""
from typing import List, Dict, Any, Optional, Generic, TypeVar
from datetime import datetime
from pydantic import BaseModel, Field

T = TypeVar('T')


class BaseResponse(BaseModel, Generic[T]):
    """基础响应模型"""
    success: bool = Field(default=True, description="请求是否成功")
    message: Optional[str] = Field(default=None, description="响应消息")
    data: Optional[T] = Field(default=None, description="响应数据")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间戳")


class PaginatedResponse(BaseResponse[List[T]]):
    """分页响应模型"""
    total: int = Field(description="总记录数")
    page: int = Field(description="当前页码")
    page_size: int = Field(description="每页大小")
    total_pages: int = Field(description="总页数")
    
    @classmethod
    def create(
        cls,
        data: List[T],
        total: int,
        page: int,
        page_size: int,
        message: Optional[str] = None
    ):
        """创建分页响应"""
        total_pages = (total + page_size - 1) // page_size
        return cls(
            data=data,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            message=message
        )


class ErrorResponse(BaseModel):
    """错误响应模型"""
    success: bool = Field(default=False)
    error_code: str = Field(description="错误码")
    message: str = Field(description="错误信息")
    details: Optional[Dict[str, Any]] = Field(default=None, description="错误详情")
    timestamp: datetime = Field(default_factory=datetime.now)


# 队列相关响应模型
class QueueInfo(BaseModel):
    """队列基本信息"""
    name: str = Field(description="队列名称")
    namespace: str = Field(description="命名空间")
    priority: Optional[int] = Field(default=None, description="优先级")
    pending_count: int = Field(default=0, description="待处理任务数")
    running_count: int = Field(default=0, description="运行中任务数") 
    completed_count: int = Field(default=0, description="已完成任务数")
    failed_count: int = Field(default=0, description="失败任务数")
    last_activity: Optional[datetime] = Field(default=None, description="最后活动时间")


class QueueStats(BaseModel):
    """队列统计信息"""
    queue_info: QueueInfo
    consumer_groups: List[Dict[str, Any]] = Field(default_factory=list, description="消费者组信息")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="性能指标")
    trends: Dict[str, Any] = Field(default_factory=dict, description="趋势数据")


class QueueListResponse(BaseResponse[List[QueueInfo]]):
    """队列列表响应"""
    pass


class QueueDetailResponse(BaseResponse[QueueStats]):
    """队列详情响应"""
    pass


# 任务相关响应模型
class TaskInfo(BaseModel):
    """任务基本信息"""
    id: str = Field(description="任务ID")
    stream_id: Optional[str] = Field(default=None, description="流ID")
    queue: str = Field(description="队列名称")
    task_name: Optional[str] = Field(default=None, description="任务名称")
    status: str = Field(description="任务状态")
    created_at: datetime = Field(description="创建时间")
    started_at: Optional[datetime] = Field(default=None, description="开始时间")
    completed_at: Optional[datetime] = Field(default=None, description="完成时间")
    duration: Optional[float] = Field(default=None, description="执行时长(秒)")
    worker_id: Optional[str] = Field(default=None, description="工作者ID")
    consumer_group: Optional[str] = Field(default=None, description="消费者组")
    priority: Optional[int] = Field(default=None, description="优先级")


class TaskDetail(TaskInfo):
    """任务详细信息"""
    task_data: Optional[Dict[str, Any]] = Field(default=None, description="任务数据")
    result: Optional[Dict[str, Any]] = Field(default=None, description="执行结果")
    error_info: Optional[Dict[str, Any]] = Field(default=None, description="错误信息")
    retry_count: int = Field(default=0, description="重试次数")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="元数据")


class TaskListResponse(PaginatedResponse[TaskInfo]):
    """任务列表响应"""
    pass


class TaskDetailResponse(BaseResponse[TaskDetail]):
    """任务详情响应"""
    pass


# 监控相关响应模型
class MetricPoint(BaseModel):
    """指标数据点"""
    timestamp: datetime = Field(description="时间戳")
    value: float = Field(description="指标值")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="元数据")


class TimeSeries(BaseModel):
    """时间序列数据"""
    name: str = Field(description="序列名称")
    data_points: List[MetricPoint] = Field(description="数据点")
    unit: Optional[str] = Field(default=None, description="单位")


class MonitoringMetrics(BaseModel):
    """监控指标"""
    series: List[TimeSeries] = Field(description="时间序列数据")
    granularity: str = Field(description="数据粒度")
    time_range: Dict[str, datetime] = Field(description="时间范围")


class MonitoringResponse(BaseResponse[MonitoringMetrics]):
    """监控数据响应"""
    pass


# 分析相关响应模型
class AnalyticsData(BaseModel):
    """分析数据"""
    chart_data: List[Dict[str, Any]] = Field(description="图表数据")
    summary: Dict[str, Any] = Field(description="汇总信息")
    insights: List[str] = Field(default_factory=list, description="分析洞察")


class AnalyticsResponse(BaseResponse[AnalyticsData]):
    """分析响应"""
    pass


# 定时任务相关响应模型
class ScheduledTaskInfo(BaseModel):
    """定时任务信息"""
    id: str = Field(description="任务ID")
    name: str = Field(description="任务名称")
    namespace: str = Field(description="命名空间")
    queue_name: str = Field(description="队列名称")
    task_name: str = Field(description="任务函数名")
    schedule_type: str = Field(description="调度类型")
    schedule_config: Dict[str, Any] = Field(description="调度配置")
    is_active: bool = Field(description="是否启用")
    created_at: datetime = Field(description="创建时间")
    updated_at: Optional[datetime] = Field(default=None, description="更新时间")
    last_run_at: Optional[datetime] = Field(default=None, description="最后运行时间")
    next_run_at: Optional[datetime] = Field(default=None, description="下次运行时间")
    run_count: int = Field(default=0, description="运行次数")
    success_count: int = Field(default=0, description="成功次数")
    failure_count: int = Field(default=0, description="失败次数")


class ScheduledTaskListResponse(PaginatedResponse[ScheduledTaskInfo]):
    """定时任务列表响应"""
    pass


class ScheduledTaskResponse(BaseResponse[ScheduledTaskInfo]):
    """定时任务响应"""
    pass


# 命名空间相关响应模型
class NamespaceInfo(BaseModel):
    """命名空间信息"""
    id: str = Field(description="命名空间ID")
    name: str = Field(description="命名空间名称")
    display_name: str = Field(description="显示名称")
    description: Optional[str] = Field(default=None, description="描述")
    redis_url: str = Field(description="Redis连接URL")
    pg_url: Optional[str] = Field(default=None, description="PostgreSQL连接URL")
    created_at: datetime = Field(description="创建时间")
    is_active: bool = Field(default=True, description="是否启用")
    queue_count: int = Field(default=0, description="队列数量")
    task_count: int = Field(default=0, description="任务数量")


class NamespaceListResponse(BaseResponse[List[NamespaceInfo]]):
    """命名空间列表响应"""
    pass


class NamespaceResponse(BaseResponse[NamespaceInfo]):
    """命名空间响应"""
    pass


# 系统状态响应模型
class SystemHealth(BaseModel):
    """系统健康状态"""
    status: str = Field(description="系统状态")
    version: str = Field(description="系统版本")
    uptime: float = Field(description="运行时间(秒)")
    components: Dict[str, str] = Field(description="组件状态")
    metrics: Dict[str, Any] = Field(description="系统指标")


class HealthResponse(BaseResponse[SystemHealth]):
    """健康检查响应"""
    pass