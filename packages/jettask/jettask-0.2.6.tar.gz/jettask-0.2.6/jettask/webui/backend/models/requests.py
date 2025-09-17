"""
Request models for JetTask WebUI Backend
"""
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum


class TimeRange(str, Enum):
    """时间范围枚举"""
    FIFTEEN_MINUTES = "15m"
    THIRTY_MINUTES = "30m"
    ONE_HOUR = "1h"
    THREE_HOURS = "3h"
    SIX_HOURS = "6h"
    TWELVE_HOURS = "12h"
    ONE_DAY = "24h"
    THREE_DAYS = "3d"
    ONE_WEEK = "7d"
    ONE_MONTH = "30d"


class SortOrder(str, Enum):
    """排序方向"""
    ASC = "asc"
    DESC = "desc"


class FilterOperator(str, Enum):
    """筛选操作符"""
    EQ = "eq"  # 等于
    NE = "ne"  # 不等于
    GT = "gt"  # 大于
    GTE = "gte"  # 大于等于
    LT = "lt"  # 小于
    LTE = "lte"  # 小于等于
    IN = "in"  # 包含
    NOT_IN = "not_in"  # 不包含
    LIKE = "like"  # 模糊匹配
    REGEX = "regex"  # 正则表达式
    IS_NULL = "is_null"  # 为空
    IS_NOT_NULL = "is_not_null"  # 不为空


class FilterCondition(BaseModel):
    """筛选条件"""
    field: str = Field(description="字段名")
    operator: FilterOperator = Field(description="操作符")
    value: Optional[Any] = Field(default=None, description="筛选值")
    
    @validator('value')
    def validate_value(cls, v, values):
        operator = values.get('operator')
        if operator in [FilterOperator.IS_NULL, FilterOperator.IS_NOT_NULL]:
            return None
        if operator in [FilterOperator.IN, FilterOperator.NOT_IN] and not isinstance(v, list):
            raise ValueError(f"Operator {operator} requires a list value")
        return v


class BaseListRequest(BaseModel):
    """基础列表查询请求"""
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页大小")
    sort_field: Optional[str] = Field(default=None, description="排序字段")
    sort_order: SortOrder = Field(default=SortOrder.DESC, description="排序方向")
    filters: List[FilterCondition] = Field(default_factory=list, description="筛选条件")
    search: Optional[str] = Field(default=None, description="搜索关键词")


class TimeRangeRequest(BaseModel):
    """时间范围查询请求"""
    start_time: Optional[datetime] = Field(default=None, description="开始时间")
    end_time: Optional[datetime] = Field(default=None, description="结束时间")
    time_range: Optional[TimeRange] = Field(default=None, description="预设时间范围")
    granularity: Optional[str] = Field(default=None, description="数据粒度")
    
    @validator('end_time')
    def validate_time_range(cls, v, values):
        start_time = values.get('start_time')
        if start_time and v and start_time >= v:
            raise ValueError("end_time must be after start_time")
        return v


# 队列相关请求模型
class QueueListRequest(BaseListRequest):
    """队列列表查询请求"""
    namespace: str = Field(default="default", description="命名空间")
    status: Optional[str] = Field(default=None, description="队列状态筛选")
    include_stats: bool = Field(default=True, description="是否包含统计信息")


class QueueMetricsRequest(TimeRangeRequest):
    """队列指标查询请求"""
    namespace: str = Field(default="default", description="命名空间")
    queue_name: str = Field(description="队列名称")
    metrics: List[str] = Field(default_factory=lambda: ["pending", "processing", "completed"], description="指标类型")
    include_consumer_groups: bool = Field(default=False, description="是否包含消费者组数据")


class QueueActionRequest(BaseModel):
    """队列操作请求"""
    action: str = Field(description="操作类型")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="操作参数")


# 任务相关请求模型
class TaskListRequest(BaseListRequest, TimeRangeRequest):
    """任务列表查询请求"""
    namespace: str = Field(default="default", description="命名空间")
    queue_name: Optional[str] = Field(default=None, description="队列名称")
    status: Optional[str] = Field(default=None, description="任务状态")
    consumer_group: Optional[str] = Field(default=None, description="消费者组")
    worker_id: Optional[str] = Field(default=None, description="工作者ID")
    task_name: Optional[str] = Field(default=None, description="任务名称")


class TaskActionRequest(BaseModel):
    """任务操作请求"""
    task_ids: List[str] = Field(description="任务ID列表")
    action: str = Field(description="操作类型")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="操作参数")


# 监控相关请求模型
class MonitoringRequest(TimeRangeRequest):
    """监控数据请求"""
    namespace: str = Field(default="default", description="命名空间")
    queues: Optional[List[str]] = Field(default=None, description="队列列表")
    metrics: List[str] = Field(default_factory=list, description="指标类型")
    include_groups: bool = Field(default=False, description="是否包含消费者组")


class BacklogTrendRequest(TimeRangeRequest):
    """队列积压趋势请求"""
    namespace: str = Field(default="default", description="命名空间")
    queues: Optional[List[str]] = Field(default=None, description="队列列表")
    include_groups: bool = Field(default=False, description="是否包含消费者组级别数据")


# 分析相关请求模型
class AnalyticsRequest(TimeRangeRequest):
    """分析查询请求"""
    namespace: str = Field(default="default", description="命名空间")
    analysis_type: str = Field(description="分析类型")
    dimensions: List[str] = Field(default_factory=list, description="分析维度")
    metrics: List[str] = Field(default_factory=list, description="分析指标")
    filters: List[FilterCondition] = Field(default_factory=list, description="筛选条件")


# 定时任务相关请求模型
class ScheduleConfig(BaseModel):
    """调度配置"""
    cron_expression: Optional[str] = Field(default=None, description="Cron表达式")
    interval_seconds: Optional[int] = Field(default=None, description="间隔秒数")
    interval_minutes: Optional[int] = Field(default=None, description="间隔分钟数")
    interval_hours: Optional[int] = Field(default=None, description="间隔小时数")
    start_date: Optional[datetime] = Field(default=None, description="开始时间")
    end_date: Optional[datetime] = Field(default=None, description="结束时间")
    max_runs: Optional[int] = Field(default=None, description="最大运行次数")
    
    @validator('interval_seconds')
    def validate_interval_seconds(cls, v):
        if v is not None and v < 1:
            raise ValueError("interval_seconds must be at least 1")
        return v


class ScheduledTaskCreateRequest(BaseModel):
    """创建定时任务请求"""
    name: str = Field(description="任务名称")
    namespace: str = Field(default="default", description="命名空间")
    queue_name: str = Field(description="队列名称")
    task_name: str = Field(description="任务函数名")
    task_data: Dict[str, Any] = Field(default_factory=dict, description="任务数据")
    schedule_type: str = Field(description="调度类型")
    schedule_config: ScheduleConfig = Field(description="调度配置")
    is_active: bool = Field(default=True, description="是否启用")
    description: Optional[str] = Field(default=None, description="任务描述")
    max_retry: int = Field(default=3, ge=0, description="最大重试次数")
    timeout: Optional[int] = Field(default=None, ge=1, description="超时时间(秒)")


class ScheduledTaskUpdateRequest(ScheduledTaskCreateRequest):
    """更新定时任务请求"""
    pass


class ScheduledTaskListRequest(BaseListRequest):
    """定时任务列表查询请求"""
    namespace: str = Field(default="default", description="命名空间")
    is_active: Optional[bool] = Field(default=None, description="是否启用")
    schedule_type: Optional[str] = Field(default=None, description="调度类型")


# 命名空间相关请求模型
class NamespaceCreateRequest(BaseModel):
    """创建命名空间请求"""
    name: str = Field(description="命名空间名称", pattern="^[a-zA-Z0-9_-]+$")
    display_name: str = Field(description="显示名称")
    description: Optional[str] = Field(default=None, description="描述")
    redis_url: str = Field(description="Redis连接URL")
    pg_url: Optional[str] = Field(default=None, description="PostgreSQL连接URL")
    redis_prefix: str = Field(default="jettask", description="Redis键前缀")


class NamespaceUpdateRequest(BaseModel):
    """更新命名空间请求"""
    display_name: Optional[str] = Field(default=None, description="显示名称")
    description: Optional[str] = Field(default=None, description="描述")
    redis_url: Optional[str] = Field(default=None, description="Redis连接URL")
    pg_url: Optional[str] = Field(default=None, description="PostgreSQL连接URL")
    is_active: Optional[bool] = Field(default=None, description="是否启用")


class NamespaceListRequest(BaseListRequest):
    """命名空间列表查询请求"""
    is_active: Optional[bool] = Field(default=None, description="是否启用")


# 系统管理相关请求模型
class SystemConfigUpdateRequest(BaseModel):
    """系统配置更新请求"""
    config_key: str = Field(description="配置键")
    config_value: Any = Field(description="配置值")
    description: Optional[str] = Field(default=None, description="配置描述")


class BatchOperationRequest(BaseModel):
    """批量操作请求"""
    operation: str = Field(description="操作类型")
    target_type: str = Field(description="目标类型")
    target_ids: List[str] = Field(description="目标ID列表")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="操作参数")