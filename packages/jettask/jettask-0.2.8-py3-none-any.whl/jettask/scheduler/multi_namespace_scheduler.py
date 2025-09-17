"""
多命名空间调度器管理器
自动检测和管理多个命名空间的调度器实例
"""
import asyncio
import logging
import multiprocessing
import traceback
from typing import Dict, Set

from jettask import Jettask
from jettask.webui.task_center import TaskCenter
from jettask.scheduler.scheduler import TaskScheduler
from jettask.scheduler.manager import ScheduledTaskManager

logger = logging.getLogger(__name__)


class MultiNamespaceSchedulerManager:
    """多命名空间调度器管理器"""
    
    def __init__(self, 
                 task_center_base_url: str,
                 check_interval: int = 30,
                 scheduler_interval: float = 0.1,
                 batch_size: int = 100,
                 debug: bool = False):
        """
        初始化多命名空间调度器管理器
        
        Args:
            task_center_base_url: 任务中心基础URL (如 http://localhost:8001)
            check_interval: 命名空间检测间隔（秒）
            scheduler_interval: 调度器扫描间隔（秒）
            batch_size: 每批处理的最大任务数
            debug: 是否启用调试模式
        """
        self.task_center_base_url = task_center_base_url.rstrip('/')
        self.check_interval = check_interval
        self.scheduler_interval = scheduler_interval
        self.batch_size = batch_size
        self.debug = debug
        
        # 存储每个命名空间的进程
        self.scheduler_processes: Dict[str, multiprocessing.Process] = {}
        self.running = False
        
        # 设置日志级别
        if debug:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)
    
    async def get_active_namespaces(self) -> Set[str]:
        """获取所有活跃的命名空间"""
        import aiohttp
        
        try:
            # 直接调用API获取命名空间列表
            url = f"{self.task_center_base_url}/api/namespaces"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        namespaces = await response.json()
                        if namespaces:
                            active_names = {ns['name'] for ns in namespaces if ns.get('name')}
                            logger.info(f"发现 {len(active_names)} 个活跃的命名空间: {active_names}")
                            return active_names
                        else:
                            logger.warning("没有找到任何命名空间")
                            return set()
                    else:
                        logger.error(f"获取命名空间列表失败，状态码: {response.status}")
                        return set()
                        
        except Exception as e:
            logger.error(f"获取命名空间列表失败: {e}")
            return set()
    
    def start_scheduler_for_namespace(self, namespace: str):
        """为指定命名空间启动调度器进程"""
        if namespace in self.scheduler_processes:
            # 检查进程是否还在运行
            if self.scheduler_processes[namespace].is_alive():
                return
            else:
                # 清理已停止的进程
                logger.info(f"清理已停止的调度器进程: {namespace}")
                self.scheduler_processes[namespace].terminate()
                self.scheduler_processes[namespace].join(timeout=5)
                del self.scheduler_processes[namespace]
        
        # 创建新进程
        process = multiprocessing.Process(
            target=run_scheduler_for_namespace,
            args=(
                namespace,
                self.task_center_base_url,
                self.scheduler_interval,
                self.batch_size,
                self.debug
            ),
            name=f"scheduler_{namespace}"
        )
        
        process.start()
        self.scheduler_processes[namespace] = process
        logger.info(f"启动命名空间 {namespace} 的调度器进程, PID: {process.pid}")
    
    def stop_scheduler_for_namespace(self, namespace: str):
        """停止指定命名空间的调度器进程"""
        if namespace in self.scheduler_processes:
            process = self.scheduler_processes[namespace]
            if process.is_alive():
                logger.info(f"停止命名空间 {namespace} 的调度器进程")
                process.terminate()
                process.join(timeout=10)
                
                if process.is_alive():
                    logger.warning(f"强制停止命名空间 {namespace} 的调度器进程")
                    process.kill()
                    process.join(timeout=5)
            
            del self.scheduler_processes[namespace]
    
    async def check_and_update_schedulers(self):
        """检查并更新调度器（添加新的，停止已删除的）"""
        # 获取当前活跃的命名空间
        active_namespaces = await self.get_active_namespaces()
        current_namespaces = set(self.scheduler_processes.keys())
        
        # 找出需要添加的命名空间
        to_add = active_namespaces - current_namespaces
        # 找出需要删除的命名空间
        to_remove = current_namespaces - active_namespaces
        
        # 启动新的调度器
        for namespace in to_add:
            logger.info(f"检测到新命名空间: {namespace}")
            self.start_scheduler_for_namespace(namespace)
        
        # 停止已删除的调度器
        for namespace in to_remove:
            logger.info(f"检测到命名空间已删除: {namespace}")
            self.stop_scheduler_for_namespace(namespace)
        
        # 检查现有进程的健康状态
        for namespace in active_namespaces & current_namespaces:
            process = self.scheduler_processes.get(namespace)
            if process and not process.is_alive():
                logger.warning(f"调度器进程 {namespace} 已停止，重新启动")
                del self.scheduler_processes[namespace]
                self.start_scheduler_for_namespace(namespace)
    
    async def run(self):
        """运行多命名空间调度器管理器"""
        self.running = True
        logger.info(f"启动多命名空间调度器管理器")
        logger.info(f"任务中心: {self.task_center_base_url}")
        logger.info(f"命名空间检测间隔: {self.check_interval} 秒")
        logger.info(f"调度器扫描间隔: {self.scheduler_interval} 秒")
        logger.info(f"批处理大小: {self.batch_size}")
        
        # 初始检查和启动
        await self.check_and_update_schedulers()
        
        # 定期检查命名空间变化
        while self.running:
            try:
                await asyncio.sleep(self.check_interval)
                await self.check_and_update_schedulers()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"检查命名空间时出错: {e}")
                if self.debug:
                    traceback.print_exc()
    
    def stop(self):
        """停止管理器和所有调度器"""
        logger.info("停止多命名空间调度器管理器")
        self.running = False
        
        # 停止所有调度器进程
        for namespace in list(self.scheduler_processes.keys()):
            self.stop_scheduler_for_namespace(namespace)
        
        logger.info("所有调度器已停止")


def run_scheduler_for_namespace(namespace: str, 
                               task_center_base_url: str,
                               interval: float,
                               batch_size: int,
                               debug: bool):
    """在独立进程中运行指定命名空间的调度器"""
    import asyncio
    import logging
    import signal
    import sys
    
    # 设置进程标题（如果可用）
    try:
        import setproctitle  # type: ignore
        setproctitle.setproctitle(f"jettask-scheduler-{namespace}")
    except ImportError:
        pass
    
    # 配置日志
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format=f'%(asctime)s - %(levelname)s - [{namespace}] %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    async def run_scheduler():
        """运行调度器的异步函数"""
        scheduler_instance = None
        try:
            # 构建命名空间特定的URL
            task_center_url = f"{task_center_base_url}/api/namespaces/{namespace}"
            logger.info(f"连接到任务中心: {task_center_url}")
            
            # 连接任务中心
            tc = TaskCenter(task_center_url)
            if not tc._connect_sync():
                logger.error(f"无法连接到任务中心: {namespace}")
                return
            
            logger.info(f"成功连接到命名空间: {tc.namespace_name}")
            
            # 创建app实例
            app = Jettask(task_center=tc)
            
            if not app.redis_url or not app.pg_url:
                logger.error(f"任务中心配置不完整: {namespace}")
                return
            
            # 显示配置信息
            logger.info(f"命名空间 {namespace} 的调度器配置:")
            logger.info(f"  Redis: {app.redis_url}")
            logger.info(f"  PostgreSQL: {app.pg_url}")
            logger.info(f"  间隔: {interval} 秒")
            logger.info(f"  批大小: {batch_size}")
            
            # 创建调度器实例
            manager = ScheduledTaskManager(app)
            scheduler_instance = TaskScheduler(
                app=app,
                db_manager=manager,
                scan_interval=interval,
                batch_size=batch_size
            )
            
            # 运行调度器（run方法内部会处理连接）
            logger.info(f"启动命名空间 {namespace} 的调度器...")
            await scheduler_instance.run()
            
        except asyncio.CancelledError:
            logger.info(f"调度器 {namespace} 收到取消信号")
        except KeyboardInterrupt:
            logger.info(f"调度器 {namespace} 收到中断信号")
        except Exception as e:
            logger.error(f"调度器 {namespace} 运行错误: {e}")
            if debug:
                traceback.print_exc()
        finally:
            # 清理资源
            if scheduler_instance:
                scheduler_instance.stop()
            
            logger.info(f"调度器 {namespace} 已停止")
    
    # 设置信号处理
    import signal
    import sys
    
    def signal_handler(signum, frame):
        logger.info(f"调度器 {namespace} 收到信号 {signum}")
        sys.exit(0)
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    # 运行调度器
    try:
        asyncio.run(run_scheduler())
    except (KeyboardInterrupt, SystemExit):
        logger.info(f"调度器 {namespace} 正常退出")
    except Exception as e:
        logger.error(f"调度器 {namespace} 异常退出: {e}")
        if debug:
            traceback.print_exc()