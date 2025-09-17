#!/usr/bin/env python
"""
JetTask CLI - 命令行接口
"""
import click
import sys
import os
import importlib
import importlib.util
import json
from pathlib import Path

# 处理相对导入和直接运行的情况
try:
    from .app_importer import import_app, AppImporter
except ImportError:
    # 如果相对导入失败，添加父目录到路径并尝试绝对导入
    parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    from jettask.core.app_importer import import_app, AppImporter

@click.group()
@click.version_option(version='0.1.0', prog_name='JetTask')
def cli():
    """JetTask - 高性能分布式任务队列系统"""
    pass

@cli.command()
@click.option('--host', default='0.0.0.0', help='服务器监听地址')
@click.option('--port', default=8001, type=int, help='服务器监听端口')
@click.option('--reload', is_flag=True, default=False, help='启用自动重载')
@click.option('--log-level', default='info', 
              type=click.Choice(['debug', 'info', 'warning', 'error']),
              help='日志级别')
@click.option('--unified', is_flag=True, default=False, help='使用统一的API路由器（实验性）')
def api(host, port, reload, log_level, unified):
    """启动 API 服务和监控界面
    
    示例:
    \b
      # 使用默认配置启动
      jettask api
      
      # 指定端口和主机
      jettask api --host 0.0.0.0 --port 8080
      
      # 启用开发模式（自动重载）
      jettask api --reload --log-level debug
      
      # 使用旧版API（不推荐）
      jettask api --no-unified
    """
    import os
    import uvicorn
    
    # 设置环境变量（如果需要）
    if not os.getenv('JETTASK_PG_URL'):
        os.environ['JETTASK_PG_URL'] = 'postgresql://jettask:123456@localhost:5432/jettask'
    
    if not os.getenv('JETTASK_CENTER_URL'):
        os.environ['JETTASK_CENTER_URL'] = f'http://localhost:{port}/api/namespaces/default'
    
    # 选择使用的应用模块
    if unified:
        app_module = "jettask.webui.backend.main_unified:app"
        click.echo(f"Starting JetTask API Server (Unified Mode - Experimental) on {host}:{port}")
        click.echo("All API endpoints are consolidated in unified_api_router.py")
        click.echo("NOTE: This mode requires specific database schema. Use --no-unified for production.")
    else:
        app_module = "jettask.webui.backend.main:app"
        click.echo(f"Starting JetTask API Server on {host}:{port}")
    
    # 显示配置信息
    click.echo("=" * 60)
    click.echo("API Server Configuration")
    click.echo("=" * 60)
    click.echo(f"Host:        {host}")
    click.echo(f"Port:        {port}")
    click.echo(f"API Mode:    {'Unified' if unified else 'Legacy'}")
    click.echo(f"Auto-reload: {reload}")
    click.echo(f"Log level:   {log_level}")
    click.echo(f"Database:    {os.getenv('JETTASK_PG_URL', 'Not configured')}")
    click.echo("=" * 60)
    
    # 启动服务器
    try:
        uvicorn.run(
            app_module,
            host=host,
            port=port,
            log_level=log_level,
            reload=reload
        )
    except KeyboardInterrupt:
        click.echo("\nShutting down API Server...")
    except Exception as e:
        click.echo(f"Error starting API Server: {e}", err=True)
        sys.exit(1)


def load_module_from_path(module_path: str):
    """从文件路径加载 Python 模块"""
    path = Path(module_path).resolve()
    
    if not path.exists():
        raise FileNotFoundError(f"Module file not found: {module_path}")
    
    # 获取模块名
    module_name = path.stem
    
    # 加载模块
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None:
        raise ImportError(f"Cannot load module from {module_path}")
    
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    
    return module

def find_jettask_app(module):
    """在模块中查找 Jettask 实例"""
    from jettask import Jettask
    
    # 查找模块中的 Jettask 实例
    for name in dir(module):
        obj = getattr(module, name)
        if isinstance(obj, Jettask):
            return obj
    
    # 如果没有找到，尝试查找名为 'app' 的变量
    if hasattr(module, 'app'):
        obj = getattr(module, 'app')
        if isinstance(obj, Jettask):
            return obj
    
    return None

@cli.command()
@click.argument('app_str', required=False, default=None)
@click.option('--queues', '-q', help='队列名称（逗号分隔，如: queue1,queue2）')
@click.option('--executor', '-e', 
              type=click.Choice(['asyncio', 'multi_asyncio']),
              default='asyncio',
              help='执行器类型')
@click.option('--concurrency', '-c', type=int, default=4, help='并发数')
@click.option('--prefetch', '-p', type=int, default=100, help='预取倍数')
@click.option('--reload', '-r', is_flag=True, help='自动重载')
@click.option('--config', help='配置文件 (JSON格式)')
def worker(app_str, queues, executor, concurrency, prefetch, reload, config):
    """启动任务处理 Worker
    
    示例:
    \b
      # 显式指定 app
      jettask worker main:app --queues async_queue
      jettask worker tasks.py:app --queues queue1,queue2
      jettask worker myapp.tasks --queues high,normal,low
      
      # 自动发现 app（从当前目录的 app.py 或 main.py）
      jettask worker --queues async_queue
      
      # 使用环境变量
      export JETTASK_APP=myapp:app
      jettask worker --queues async_queue
    """
    
    # 如果提供了配置文件，从中加载配置
    if config:
        click.echo(f"Loading configuration from {config}")
        with open(config, 'r') as f:
            config_data = json.load(f)
        
        # 从配置文件读取参数（命令行参数优先）
        queues = queues or ','.join(config_data.get('queues', [])) if config_data.get('queues') else None
        executor = executor or config_data.get('executor', 'asyncio')
        concurrency = concurrency if concurrency != 4 else config_data.get('concurrency', 4)
        prefetch = prefetch if prefetch != 100 else config_data.get('prefetch', 100)
        reload = reload or config_data.get('reload', False)
    
    # 加载应用
    try:
        if app_str:
            click.echo(f"Loading app from: {app_str}")
            app = import_app(app_str)
        else:
            click.echo("Auto-discovering Jettask app...")
            click.echo("Searching in: app.py, main.py, server.py, worker.py")
            app = import_app()  # 自动发现
        
        # 显示应用信息
        app_info = AppImporter.get_app_info(app)
        click.echo(f"\nFound Jettask app:")
        click.echo(f"  Tasks: {app_info['tasks']} registered")
        if app_info.get('task_names') and app_info['tasks'] > 0:
            task_preview = app_info['task_names'][:3]
            click.echo(f"  Names: {', '.join(task_preview)}" + 
                      (f" (+{app_info['tasks'] - 3} more)" if app_info['tasks'] > 3 else ""))
    except ImportError as e:
        import traceback
        click.echo(f"Error: Failed to import app: {e}", err=True)
        
        # 始终显示完整的堆栈跟踪，帮助用户定位问题
        click.echo("\n" + "=" * 60, err=True)
        click.echo("Full traceback:", err=True)
        click.echo("=" * 60, err=True)
        traceback.print_exc()
        click.echo("=" * 60, err=True)
        
        click.echo("\nTips:", err=True)
        click.echo("  - Check if there are syntax errors in your code", err=True)
        click.echo("  - Verify all imports in your module are available", err=True)
        click.echo("  - Specify app location: jettask worker myapp:app", err=True)
        click.echo("  - Or set environment variable: export JETTASK_APP=myapp:app", err=True)
        click.echo("  - Or ensure app.py or main.py exists in current directory", err=True)
        sys.exit(1)
    except Exception as e:
        import traceback
        click.echo(f"Error loading app: {e}", err=True)
        
        # 对于所有异常都显示堆栈信息
        click.echo("\n" + "=" * 60, err=True)
        click.echo("Full traceback:", err=True)
        click.echo("=" * 60, err=True)
        traceback.print_exc()
        click.echo("=" * 60, err=True)
        
        click.echo("\nThis might be a bug in JetTask or your application.", err=True)
        click.echo("Please check the traceback above for details.", err=True)
        sys.exit(1)
    
    # 处理队列参数
    if queues:
        # 解析队列列表（支持逗号分隔）
        queue_list = [q.strip() for q in queues.split(',') if q.strip()]
    else:
        # 如果没有指定队列，尝试从 app 获取
        if hasattr(app, 'ep') and hasattr(app.ep, 'queues'):
            queue_list = list(app.ep.queues)
            if queue_list:
                click.echo(f"Using queues from app: {', '.join(queue_list)}")
        else:
            queue_list = []
    
    if not queue_list:
        click.echo("Error: No queues specified", err=True)
        click.echo("  Use --queues to specify queues, e.g.: --queues queue1,queue2", err=True)
        click.echo("  Or define queues in your app configuration", err=True)
        sys.exit(1)
    
    # 从 app 实例中获取实际配置
    redis_url = app.redis_url if hasattr(app, 'redis_url') else 'Not configured'
    redis_prefix = app.redis_prefix if hasattr(app, 'redis_prefix') else 'jettask'
    consumer_strategy = app.consumer_strategy if hasattr(app, 'consumer_strategy') else 'heartbeat'
    
    # 显示配置信息
    click.echo("=" * 60)
    click.echo("JetTask Worker Configuration")
    click.echo("=" * 60)
    click.echo(f"App:          {app_str}")
    click.echo(f"Redis URL:    {redis_url}")
    click.echo(f"Redis Prefix: {redis_prefix}")
    click.echo(f"Strategy:     {consumer_strategy}")
    click.echo(f"Queues:       {', '.join(queue_list)}")
    click.echo(f"Executor:     {executor}")
    click.echo(f"Concurrency:  {concurrency}")
    click.echo(f"Prefetch:     {prefetch}")
    click.echo(f"Auto-reload:  {reload}")
    click.echo("=" * 60)
    
    # 启动 Worker
    try:
        click.echo(f"Starting {executor} worker...")
        app.start(
            execute_type=executor,
            queues=queue_list,
            concurrency=concurrency,
            prefetch_multiplier=prefetch,
            reload=reload
        )
    except KeyboardInterrupt:
        click.echo("\nShutting down worker...")
    except Exception as e:
        click.echo(f"Error starting worker: {e}", err=True)
        sys.exit(1)

@cli.command('webui-consumer')
@click.option('--task-center', '-tc', envvar='JETTASK_CENTER_URL', required=True,
              help='任务中心URL，如: http://localhost:8001 或 http://localhost:8001/api/namespaces/default')
@click.option('--check-interval', type=int, default=30,
              help='命名空间检测间隔（秒），默认30秒')
@click.option('--debug', is_flag=True, help='启用调试模式')
def webui_consumer(task_center, check_interval, debug):
    """启动数据消费者（自动识别单/多命名空间）
    
    根据URL格式自动判断运行模式:
    - 单命名空间: http://localhost:8001/api/namespaces/{name}
    - 多命名空间: http://localhost:8001 或 http://localhost:8001/api
    
    示例:
    \b
      # 为所有命名空间启动消费者（自动检测）
      jettask webui-consumer --task-center http://localhost:8001
      jettask webui-consumer --task-center http://localhost:8001/api
      
      # 为单个命名空间启动消费者
      jettask webui-consumer --task-center http://localhost:8001/api/namespaces/default
      
      # 自定义检测间隔
      jettask webui-consumer --task-center http://localhost:8001 --check-interval 60
      
      # 使用环境变量
      export JETTASK_CENTER_URL=http://localhost:8001
      jettask webui-consumer
    """
    import asyncio
    from jettask.webui.unified_consumer_manager import UnifiedConsumerManager
    
    # 运行消费者管理器
    async def run_manager():
        """运行统一的消费者管理器"""
        manager = UnifiedConsumerManager(
            task_center_url=task_center,
            check_interval=check_interval,
            debug=debug
        )
        await manager.run()
    
    try:
        asyncio.run(run_manager())
    except KeyboardInterrupt:
        click.echo("\nShutdown complete")

@cli.command()
def monitor():
    """启动系统监控器"""
    click.echo("Starting JetTask Monitor")
    from jettask.webui.run_monitor import main as monitor_main
    monitor_main()

@cli.command()
@click.option('--task-center', '-tc', envvar='JETTASK_CENTER_URL',
              help='任务中心URL，如: http://localhost:8001/api/namespaces/default')
def init(task_center):
    """初始化数据库和配置
    
    示例:
    \b
      # 使用任务中心初始化
      jettask init --task-center http://localhost:8001/api/namespaces/default
      jettask init -tc http://localhost:8001/api/namespaces/production
      
      # 使用环境变量
      export JETTASK_CENTER_URL=http://localhost:8001/api/namespaces/default
      jettask init
      
      # 不使用任务中心（仅使用本地环境变量）
      jettask init
    """
    click.echo("Initializing JetTask...")
    
    import os
    
    # 如果提供了任务中心URL，尝试从任务中心获取配置
    if task_center:
        os.environ['JETTASK_CENTER_URL'] = task_center
        click.echo(f"Using Task Center: {task_center}")
        
        # 尝试从任务中心获取数据库配置
        try:
            from jettask.webui.task_center import TaskCenter
            tc = TaskCenter(task_center)
            if tc._connect_sync():
                p_config = tc.pg_config
                # 从任务中心获取的配置中提取数据库连接参数
                os.environ['JETTASK_PG_HOST'] = p_config['host']
                os.environ['JETTASK_PG_PORT'] = str(p_config['port'])
                os.environ['JETTASK_PG_DATABASE'] = p_config['database']
                os.environ['JETTASK_PG_USER'] = p_config['user']
                os.environ['JETTASK_PG_PASSWORD'] = p_config['password']
            else:
                click.echo("⚠ Failed to connect to Task Center, using local configuration", err=True)
        except Exception as e:
            click.echo(f"⚠ Could not get configuration from Task Center: {e}", err=True)
            click.echo("  Falling back to local environment variables")
    
    # 初始化数据库
    from jettask.webui.db_init import init_database
    click.echo("\nInitializing database...")
    init_database()
    
    click.echo("\n✓ JetTask initialized successfully!")

@cli.command()
def status():
    """显示系统状态"""
    click.echo("JetTask System Status")
    click.echo("=" * 50)
    
    # 检查 Redis 连接
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        click.echo("✓ Redis: Connected")
    except:
        click.echo("✗ Redis: Not connected")
    
    # 检查 PostgreSQL 连接
    try:
        import psycopg2
        conn = psycopg2.connect(
            dbname=os.getenv('JETTASK_PG_DB', 'jettask'),
            user=os.getenv('JETTASK_PG_USER', 'jettask'),
            password=os.getenv('JETTASK_PG_PASSWORD', '123456'),
            host=os.getenv('JETTASK_PG_HOST', 'localhost'),
            port=os.getenv('JETTASK_PG_PORT', '5432')
        )
        conn.close()
        click.echo("✓ PostgreSQL: Connected")
    except:
        click.echo("✗ PostgreSQL: Not connected")
    
    click.echo("=" * 50)

@cli.command()
@click.option('--task-center', '-tc', envvar='JETTASK_CENTER_URL', required=True,
              help='任务中心URL，如: http://localhost:8001 或 http://localhost:8001/api/namespaces/default')
@click.option('--interval', '-i', type=float, default=0.1, 
              help='调度器扫描间隔（秒），默认0.1秒')
@click.option('--batch-size', '-b', type=int, default=100,
              help='每批处理的最大任务数，默认100')
@click.option('--check-interval', type=int, default=30,
              help='命名空间检测间隔（秒），仅多命名空间模式使用，默认30秒')
@click.option('--debug', is_flag=True, help='启用调试模式')
def scheduler(task_center, interval, batch_size, check_interval, debug):
    """启动定时任务调度器（自动识别单/多命名空间）
    
    根据URL格式自动判断运行模式:
    - 单命名空间: http://localhost:8001/api/namespaces/{name}
    - 多命名空间: http://localhost:8001 或 http://localhost:8001/api
    
    示例:
    \b
      # 为所有命名空间启动调度器（自动检测）
      jettask scheduler --task-center http://localhost:8001
      jettask scheduler --task-center http://localhost:8001/api
      
      # 为单个命名空间启动调度器
      jettask scheduler --task-center http://localhost:8001/api/namespaces/default
      
      # 自定义配置
      jettask scheduler --task-center http://localhost:8001 --check-interval 60 --interval 0.5
      
      # 使用环境变量
      export JETTASK_CENTER_URL=http://localhost:8001
      jettask scheduler
    """
    import asyncio
    from jettask.scheduler.unified_scheduler_manager import UnifiedSchedulerManager
    
    # 运行调度器管理器
    async def run_manager():
        """运行统一的调度器管理器"""
        manager = UnifiedSchedulerManager(
            task_center_url=task_center,
            scan_interval=interval,
            batch_size=batch_size,
            check_interval=check_interval,
            debug=debug
        )
        await manager.run()
    
    try:
        asyncio.run(run_manager())
    except KeyboardInterrupt:
        click.echo("\nShutdown complete")

def main():
    """主入口函数"""
    try:
        cli()
    except KeyboardInterrupt:
        click.echo("\nOperation cancelled by user")
        sys.exit(0)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

if __name__ == '__main__':
    main()