"""
统一的定时任务调度管理器
自动识别单命名空间和多命名空间模式
"""
import asyncio
import logging
import multiprocessing
import re
from typing import Dict, Set, Optional, List
import aiohttp
import traceback

from jettask import Jettask
from jettask.webui.task_center import TaskCenter
from .scheduler import TaskScheduler
from .manager import ScheduledTaskManager

logger = logging.getLogger(__name__)


class UnifiedSchedulerManager:
    """
    统一的调度器管理器
    根据task_center_url自动判断是单命名空间还是多命名空间模式
    """
    
    def __init__(self, 
                 task_center_url: str,
                 scan_interval: float = 0.1,
                 batch_size: int = 100,
                 check_interval: int = 30,
                 debug: bool = False):
        """
        初始化统一调度器管理器
        
        Args:
            task_center_url: 任务中心URL
                - 单命名空间: http://localhost:8001/api/namespaces/{name}
                - 多命名空间: http://localhost:8001 或 http://localhost:8001/api
            scan_interval: 调度器扫描间隔（秒）
            batch_size: 每批处理的最大任务数
            check_interval: 命名空间检测间隔（秒），仅多命名空间模式使用
            debug: 是否启用调试模式
        """
        self.task_center_url = task_center_url.rstrip('/')
        self.scan_interval = scan_interval
        self.batch_size = batch_size
        self.check_interval = check_interval
        self.debug = debug
        
        # 判断模式
        self.namespace_name: Optional[str] = None
        self.is_single_namespace = self._detect_mode()
        
        # 单命名空间模式：直接管理TaskScheduler
        self.scheduler_instance: Optional[TaskScheduler] = None
        
        # 多命名空间模式：管理多个进程
        self.scheduler_processes: Dict[str, multiprocessing.Process] = {}
        
        self.running = False
        
        # 设置日志
        if debug:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)
    
    def _detect_mode(self) -> bool:
        """
        检测是单命名空间还是多命名空间模式
        
        Returns:
            True: 单命名空间模式
            False: 多命名空间模式
        """
        # 检查URL格式
        # 单命名空间: /api/namespaces/{name}
        # 多命名空间: 不包含 /api/namespaces/ 或以 /api 结尾
        
        if '/api/namespaces/' in self.task_center_url:
            # 提取命名空间名称
            match = re.search(r'/api/namespaces/([^/]+)/?$', self.task_center_url)
            if match:
                self.namespace_name = match.group(1)
                logger.info(f"检测到单命名空间模式: {self.namespace_name}")
                return True
        
        # 多命名空间模式
        logger.info("检测到多命名空间模式")
        return False
    
    async def run(self):
        """运行调度器管理器（统一处理单/多命名空间）"""
        self.running = True
        
        logger.info(f"启动调度器管理器")
        logger.info(f"任务中心: {self.task_center_url}")
        logger.info(f"模式: {'单命名空间' if self.is_single_namespace else '多命名空间'}")
        if not self.is_single_namespace:
            logger.info(f"命名空间检测间隔: {self.check_interval} 秒")
        logger.info(f"调度器扫描间隔: {self.scan_interval} 秒")
        logger.info(f"批处理大小: {self.batch_size}")
        
        # 初始检查和启动
        await self._check_and_update_schedulers()
        
        # 如果是单命名空间，不需要定期检查
        if self.is_single_namespace:
            # 等待直到停止
            while self.running:
                await asyncio.sleep(1)
        else:
            # 多命名空间模式：定期检查命名空间变化
            while self.running:
                try:
                    await asyncio.sleep(self.check_interval)
                    await self._check_and_update_schedulers()
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"检查命名空间时出错: {e}")
                    if self.debug:
                        traceback.print_exc()
    
    async def _get_active_namespaces(self) -> Set[str]:
        """获取所有活跃的命名空间"""
        # 单命名空间模式：直接返回指定的命名空间
        if self.is_single_namespace:
            return {self.namespace_name} if self.namespace_name else set()
        
        # 多命名空间模式：从API获取
        try:
            # 构建API URL
            if self.task_center_url.endswith('/api'):
                url = f"{self.task_center_url}/namespaces"
            else:
                url = f"{self.task_center_url}/api/namespaces"
            
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
    
    async def _check_and_update_schedulers(self):
        """检查并更新调度器（添加新的，停止已删除的）"""
        # 获取当前活跃的命名空间
        active_namespaces = await self._get_active_namespaces()
        current_namespaces = set(self.scheduler_processes.keys())
        
        # 找出需要添加的命名空间
        to_add = active_namespaces - current_namespaces
        # 找出需要删除的命名空间
        to_remove = current_namespaces - active_namespaces
        
        # 启动新的调度器
        for namespace in to_add:
            logger.info(f"检测到新命名空间: {namespace}")
            self._start_scheduler_for_namespace(namespace)
        
        # 停止已删除的调度器
        for namespace in to_remove:
            logger.info(f"检测到命名空间已删除: {namespace}")
            self._stop_scheduler_for_namespace(namespace)
        
        # 检查现有进程的健康状态
        for namespace in active_namespaces & current_namespaces:
            process = self.scheduler_processes.get(namespace)
            if process and not process.is_alive():
                logger.warning(f"调度器进程 {namespace} 已停止，重新启动")
                del self.scheduler_processes[namespace]
                self._start_scheduler_for_namespace(namespace)
    
    def _start_scheduler_for_namespace(self, namespace: str):
        """为指定命名空间启动调度器"""
        # 单命名空间模式：直接在当前进程运行
        if self.is_single_namespace:
            # 构建命名空间URL（单命名空间已经有完整URL）
            namespace_url = self.task_center_url
            
            # 创建异步任务运行调度器
            async def run_single_scheduler():
                await _run_scheduler_async(
                    namespace=namespace,
                    task_center_url=namespace_url,
                    scan_interval=self.scan_interval,
                    batch_size=self.batch_size,
                    debug=self.debug
                )
            
            # 创建任务
            task = asyncio.create_task(run_single_scheduler())
            # 保存任务引用（使用相同的字典结构，方便统一管理）
            self.scheduler_processes[namespace] = task
            logger.info(f"启动命名空间 {namespace} 的调度器（同进程）")
            return
        
        # 多命名空间模式：创建独立进程
        if namespace in self.scheduler_processes:
            process = self.scheduler_processes[namespace]
            if isinstance(process, multiprocessing.Process) and process.is_alive():
                return
            else:
                logger.info(f"清理已停止的调度器: {namespace}")
                if isinstance(process, multiprocessing.Process):
                    process.terminate()
                    process.join(timeout=5)
                del self.scheduler_processes[namespace]
        
        # 构建命名空间URL
        if self.task_center_url.endswith('/api'):
            namespace_url = f"{self.task_center_url}/namespaces/{namespace}"
        else:
            namespace_url = f"{self.task_center_url}/api/namespaces/{namespace}"
        
        # 创建新进程
        process = multiprocessing.Process(
            target=_run_scheduler_in_process,
            args=(
                namespace,
                namespace_url,
                self.scan_interval,
                self.batch_size,
                self.debug
            ),
            name=f"scheduler_{namespace}"
        )
        
        process.start()
        self.scheduler_processes[namespace] = process
        logger.info(f"启动命名空间 {namespace} 的调度器进程, PID: {process.pid}")
    
    def _stop_scheduler_for_namespace(self, namespace: str):
        """停止指定命名空间的调度器"""
        if namespace in self.scheduler_processes:
            scheduler = self.scheduler_processes[namespace]
            
            # 处理异步任务（单命名空间模式）
            if isinstance(scheduler, asyncio.Task):
                if not scheduler.done():
                    logger.info(f"停止命名空间 {namespace} 的调度器任务")
                    scheduler.cancel()
            
            # 处理进程（多命名空间模式）
            elif isinstance(scheduler, multiprocessing.Process):
                if scheduler.is_alive():
                    logger.info(f"停止命名空间 {namespace} 的调度器进程")
                    scheduler.terminate()
                    scheduler.join(timeout=10)
                    
                    if scheduler.is_alive():
                        logger.warning(f"强制停止命名空间 {namespace} 的调度器进程")
                        scheduler.kill()
                        scheduler.join(timeout=5)
            
            del self.scheduler_processes[namespace]
    
    def stop(self):
        """停止管理器"""
        logger.info("停止调度器管理器")
        self.running = False
        
        # 统一处理：停止所有调度器（不管是任务还是进程）
        for namespace in list(self.scheduler_processes.keys()):
            self._stop_scheduler_for_namespace(namespace)
        
        logger.info("调度器管理器已停止")
    
    def add_scheduler(self, namespace: str, scheduler: TaskScheduler):
        """
        添加TaskScheduler实例（预留接口）
        
        Args:
            namespace: 命名空间名称
            scheduler: TaskScheduler实例
        """
        # 这个方法预留给未来可能的扩展
        # 比如动态添加调度器而不需要重启
        pass


async def _run_scheduler_async(namespace: str,
                              task_center_url: str,
                              scan_interval: float,
                              batch_size: int,
                              debug: bool):
    """异步运行指定命名空间的调度器（用于单命名空间模式）"""
    scheduler_instance = None
    try:
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
        logger.info(f"  间隔: {scan_interval} 秒")
        logger.info(f"  批大小: {batch_size}")
        
        # 创建调度器实例
        db_manager = ScheduledTaskManager(app)
        scheduler_instance = TaskScheduler(
            app=app,
            db_manager=db_manager,
            scan_interval=scan_interval,
            batch_size=batch_size
        )
        
        # 运行调度器
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
        if scheduler_instance:
            scheduler_instance.stop()
        logger.info(f"调度器 {namespace} 已停止")


def _run_scheduler_in_process(namespace: str, 
                             task_center_url: str,
                             scan_interval: float,
                             batch_size: int,
                             debug: bool):
    """在独立进程中运行指定命名空间的调度器（用于多命名空间模式）"""
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
            logger.info(f"  间隔: {scan_interval} 秒")
            logger.info(f"  批大小: {batch_size}")
            
            # 创建调度器实例
            db_manager = ScheduledTaskManager(app)
            scheduler_instance = TaskScheduler(
                app=app,
                db_manager=db_manager,
                scan_interval=scan_interval,
                batch_size=batch_size
            )
            
            # 运行调度器
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
            if scheduler_instance:
                scheduler_instance.stop()
            logger.info(f"调度器 {namespace} 已停止")
    
    # 设置信号处理
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