"""
任务批量发送构建器
提供类型安全的批量任务发送接口
"""
from typing import List, Dict, Any, Optional, Union, TYPE_CHECKING
import asyncio
from dataclasses import dataclass, field

if TYPE_CHECKING:
    from .task import Task
    from .app import JetTaskApp


@dataclass
class TaskMessage:
    """单个任务消息"""
    task_name: str
    queue: str
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    delay: Optional[int] = None
    timeout: Optional[int] = None
    max_retries: Optional[int] = None
    retry_delay: Optional[int] = None
    scheduled_task_id: Optional[int] = None
    routing: Optional[dict] = None
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        data = {
            'task_name': self.task_name,
            'args': self.args,
            'kwargs': self.kwargs,
        }
        
        # 只添加非None的可选参数
        optional_fields = ['delay', 'timeout', 'max_retries', 'retry_delay', 
                          'scheduled_task_id', 'routing']
        for field in optional_fields:
            value = getattr(self, field)
            if value is not None:
                data[field] = value
        
        return data


class TaskBatch:
    """
    任务批量构建器
    
    使用示例:
        batch = task.batch()
        batch.add(args=(1,), kwargs={'user': 'alice'})
        batch.add(args=(2,), kwargs={'user': 'bob'}, delay=5)
        results = await batch.send()
    """
    
    def __init__(self, task: 'Task', app: 'JetTaskApp'):
        self.task = task
        self.app = app
        self.messages: List[TaskMessage] = []
        self._queue = task.queue
        
    def add(
        self,
        args: tuple = None,
        kwargs: dict = None,
        queue: str = None,
        delay: int = None,
        timeout: int = None,
        max_retries: int = None,
        retry_delay: int = None,
        scheduled_task_id: int = None,
        routing: dict = None,
    ) -> 'TaskBatch':
        """
        添加一个任务到批量队列
        
        参数签名与 apply_async 完全一致，保证IDE提示
        
        Args:
            args: 位置参数
            kwargs: 关键字参数
            queue: 指定队列（默认使用task的队列）
            delay: 延迟执行时间（秒）
            timeout: 任务超时时间（秒）
            max_retries: 最大重试次数
            retry_delay: 重试间隔（秒）
            scheduled_task_id: 定时任务ID
            routing: 路由信息
            
        Returns:
            self: 支持链式调用
        """
        message = TaskMessage(
            task_name=self.task.name,
            queue=queue or self._queue,
            args=args or (),
            kwargs=kwargs or {},
            delay=delay,
            timeout=timeout,
            max_retries=max_retries,
            retry_delay=retry_delay,
            scheduled_task_id=scheduled_task_id,
            routing=routing,
        )
        self.messages.append(message)
        return self
    
    async def send(self) -> List[str]:
        """
        批量发送所有任务
        
        Returns:
            List[str]: 任务ID列表
        """
        if not self.messages:
            return []
        
        # 转换为批量写入格式
        batch_data = []
        for msg in self.messages:
            batch_data.append({
                'queue': msg.queue,
                'data': msg.to_dict()
            })
        
        # 调用app的批量写入方法
        # 这里假设app有一个内部的批量写入方法
        result = await self.app._bulk_write_messages(batch_data)
        
        # 清空消息列表，允许复用
        self.messages.clear()
        
        return result
    
    def send_sync(self) -> List[str]:
        """
        同步版本的批量发送
        
        Returns:
            List[str]: 任务ID列表
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.send())
    
    def __len__(self) -> int:
        """返回当前批量任务的数量"""
        return len(self.messages)
    
    def clear(self) -> None:
        """清空批量任务列表"""
        self.messages.clear()