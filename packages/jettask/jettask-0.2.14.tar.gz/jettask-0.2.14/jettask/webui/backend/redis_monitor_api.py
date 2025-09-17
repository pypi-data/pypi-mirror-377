"""
Redis监控API - 提供Redis性能和负载监控数据
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Optional, List, Any
from datetime import datetime, timedelta
import logging
import asyncio
import time
import psutil
from namespace_data_access import get_namespace_data_access
import traceback

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/redis", tags=["redis-monitor"])


def parse_redis_info(info_str: str) -> Dict[str, Any]:
    """解析Redis INFO命令的输出"""
    sections = {}
    current_section = None
    
    for line in info_str.split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            # 处理节标题
            if line.startswith('#'):
                section_name = line[1:].strip().lower()
                current_section = section_name
                sections[current_section] = {}
            continue
        
        # 解析键值对
        if ':' in line:
            key, value = line.split(':', 1)
            if current_section:
                sections[current_section][key] = value
            else:
                sections[key] = value
    
    return sections


def calculate_metrics(info_data: Dict[str, Any]) -> Dict[str, Any]:
    """从Redis INFO数据计算监控指标"""
    metrics = {
        'timestamp': datetime.now().isoformat(),
        'status': 'healthy',
        'cpu': {},
        'memory': {},
        'stats': {},
        'persistence': {},
        'replication': {},
        'clients': {},
        'keyspace': {},
        'server': {}
    }
    
    # redis.asyncio 返回的是扁平的字典，直接从中提取数据
    # CPU相关指标
    metrics['cpu'] = {
        'used_cpu_sys': float(info_data.get('used_cpu_sys', 0)),
        'used_cpu_user': float(info_data.get('used_cpu_user', 0)),
        'used_cpu_sys_children': float(info_data.get('used_cpu_sys_children', 0)),
        'used_cpu_user_children': float(info_data.get('used_cpu_user_children', 0)),
        'used_cpu_total': float(info_data.get('used_cpu_sys', 0)) + 
                        float(info_data.get('used_cpu_user', 0)),
    }
    
    # 内存相关指标
    used_memory = int(info_data.get('used_memory', 0))
    max_memory = info_data.get('maxmemory', '0')
    max_memory = int(max_memory) if max_memory != '0' else None
    
    metrics['memory'] = {
        'used_memory': used_memory,
        'used_memory_human': info_data.get('used_memory_human', '0B'),
        'used_memory_rss': int(info_data.get('used_memory_rss', 0)),
        'used_memory_rss_human': info_data.get('used_memory_rss_human', '0B'),
        'used_memory_peak': int(info_data.get('used_memory_peak', 0)),
        'used_memory_peak_human': info_data.get('used_memory_peak_human', '0B'),
        'used_memory_overhead': int(info_data.get('used_memory_overhead', 0)),
        'used_memory_dataset': int(info_data.get('used_memory_dataset', 0)),
        'mem_fragmentation_ratio': float(info_data.get('mem_fragmentation_ratio', 1.0)),
        'maxmemory': max_memory,
        'maxmemory_human': info_data.get('maxmemory_human', '0B'),
        'maxmemory_policy': info_data.get('maxmemory_policy', 'noeviction'),
    }
    
    # 计算内存使用率
    if max_memory and max_memory > 0:
        # 如果Redis设置了内存限制，使用配置的限制
        metrics['memory']['usage_percentage'] = round((used_memory / max_memory) * 100, 2)
        metrics['memory']['total_memory'] = max_memory
        metrics['memory']['total_memory_human'] = info_data.get('maxmemory_human', '0B')
    else:
        # 如果Redis没有设置内存限制，使用系统总内存进行计算
        try:
            system_memory = psutil.virtual_memory()
            total_memory = system_memory.total
            metrics['memory']['usage_percentage'] = round((used_memory / total_memory) * 100, 2)
            metrics['memory']['total_memory'] = total_memory
            # 转换为人类可读格式
            def format_bytes(bytes_value):
                for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                    if bytes_value < 1024.0:
                        return f"{bytes_value:.1f}{unit}"
                    bytes_value /= 1024.0
                return f"{bytes_value:.1f}PB"
            metrics['memory']['total_memory_human'] = format_bytes(total_memory)
        except Exception as e:
            logger.warning(f"无法获取系统内存信息: {e}")
            traceback.print_exc()
            metrics['memory']['usage_percentage'] = None
            metrics['memory']['total_memory'] = None
            metrics['memory']['total_memory_human'] = 'Unknown'
    
    # 统计信息
    metrics['stats'] = {
        'total_connections_received': int(info_data.get('total_connections_received', 0)),
        'total_commands_processed': int(info_data.get('total_commands_processed', 0)),
        'instantaneous_ops_per_sec': int(info_data.get('instantaneous_ops_per_sec', 0)),
        'total_net_input_bytes': int(info_data.get('total_net_input_bytes', 0)),
        'total_net_output_bytes': int(info_data.get('total_net_output_bytes', 0)),
        'instantaneous_input_kbps': float(info_data.get('instantaneous_input_kbps', 0)),
        'instantaneous_output_kbps': float(info_data.get('instantaneous_output_kbps', 0)),
        'rejected_connections': int(info_data.get('rejected_connections', 0)),
        'expired_keys': int(info_data.get('expired_keys', 0)),
        'evicted_keys': int(info_data.get('evicted_keys', 0)),
        'keyspace_hits': int(info_data.get('keyspace_hits', 0)),
        'keyspace_misses': int(info_data.get('keyspace_misses', 0)),
    }
    
    # 计算命中率
    hits = metrics['stats']['keyspace_hits']
    misses = metrics['stats']['keyspace_misses']
    if hits + misses > 0:
        metrics['stats']['hit_rate'] = round((hits / (hits + misses)) * 100, 2)
    else:
        metrics['stats']['hit_rate'] = 0
    
    # 持久化信息
    metrics['persistence'] = {
        'rdb_last_save_time': int(info_data.get('rdb_last_save_time', 0)),
        'rdb_changes_since_last_save': int(info_data.get('rdb_changes_since_last_save', 0)),
        'rdb_bgsave_in_progress': int(info_data.get('rdb_bgsave_in_progress', 0)),
        'rdb_last_bgsave_status': info_data.get('rdb_last_bgsave_status', 'ok'),
        'aof_enabled': int(info_data.get('aof_enabled', 0)),
        'aof_rewrite_in_progress': int(info_data.get('aof_rewrite_in_progress', 0)),
        'aof_last_rewrite_time_sec': int(info_data.get('aof_last_rewrite_time_sec', -1)),
    }
    
    # 复制信息
    metrics['replication'] = {
        'role': info_data.get('role', 'master'),
        'connected_slaves': int(info_data.get('connected_slaves', 0)),
        'master_repl_offset': int(info_data.get('master_repl_offset', 0)) if 'master_repl_offset' in info_data else None,
    }
    
    # 客户端连接信息
    metrics['clients'] = {
        'connected_clients': int(info_data.get('connected_clients', 0)),
        'blocked_clients': int(info_data.get('blocked_clients', 0)),
        'tracking_clients': int(info_data.get('tracking_clients', 0)),
    }
    
    # 键空间信息
    total_keys = 0
    total_expires = 0
    db_stats = {}
    
    for key, value in info_data.items():
        if key.startswith('db') and key[2:].isdigit():
            # 解析格式: keys=100,expires=10,avg_ttl=3600
            if isinstance(value, str):
                parts = value.split(',')
                db_info = {}
                for part in parts:
                    if '=' in part:
                        k, v = part.split('=')
                        db_info[k] = int(v) if v.isdigit() else v
            else:
                db_info = value
            
            db_stats[key] = db_info
            total_keys += db_info.get('keys', 0)
            total_expires += db_info.get('expires', 0)
    
    metrics['keyspace'] = {
        'databases': db_stats,
        'total_keys': total_keys,
        'total_expires': total_expires,
    }
    
    # 服务器信息
    metrics['server'] = {
        'redis_version': info_data.get('redis_version', 'unknown'),
        'redis_mode': info_data.get('redis_mode', 'standalone'),
        'uptime_in_seconds': int(info_data.get('uptime_in_seconds', 0)),
        'uptime_in_days': int(info_data.get('uptime_in_days', 0)),
    }
    
    return metrics


@router.get("/monitor/{namespace}")
async def get_redis_monitor(namespace: str) -> Dict[str, Any]:
    """
    获取指定命名空间的Redis监控数据
    
    包括：
    - CPU使用情况
    - 内存使用情况
    - 连接数
    - 命令处理速率
    - 键空间统计
    - 持久化状态
    - 复制状态
    """
    try:
        namespace_data = get_namespace_data_access()
        connection = await namespace_data.manager.get_connection(namespace)
        
        if not connection:
            raise HTTPException(status_code=404, detail=f"命名空间 {namespace} 不存在")
        
        # 获取Redis客户端
        redis_client = await connection.get_redis_client(decode=True)
        
        # 执行INFO命令获取Redis状态信息
        info_data = await redis_client.info()
        
        # 如果返回的是字符串，需要解析；如果已经是字典，直接使用
        if isinstance(info_data, str):
            info_data = parse_redis_info(info_data)
        
        # 计算监控指标
        metrics = calculate_metrics(info_data)
        
        # 添加命名空间信息
        metrics['namespace'] = namespace
        
        # 获取慢查询日志（最近10条）
        try:
            slowlog = await redis_client.slowlog_get(10)
            metrics['slowlog'] = []
            
            for log_entry in slowlog:
                if isinstance(log_entry, dict):
                    # 新版Redis返回字典格式
                    command = log_entry.get('command', '')
                    if isinstance(command, bytes):
                        command = command.decode('utf-8', errors='ignore')
                    
                    # 限制命令长度
                    if len(command) > 100:
                        command = command[:100] + '...'
                    
                    metrics['slowlog'].append({
                        'id': log_entry.get('id', 0),
                        'timestamp': datetime.fromtimestamp(log_entry.get('start_time', 0)).isoformat(),
                        'duration_us': log_entry.get('duration', 0),
                        'command': command,
                    })
                elif isinstance(log_entry, (list, tuple)) and len(log_entry) >= 4:
                    # 旧版Redis返回列表格式 [id, timestamp, duration, command]
                    command_parts = log_entry[3] if len(log_entry) > 3 else []
                    command = ' '.join(str(arg) for arg in command_parts[:5])
                    if len(command_parts) > 5:
                        command += '...'
                    
                    metrics['slowlog'].append({
                        'id': log_entry[0],
                        'timestamp': datetime.fromtimestamp(log_entry[1]).isoformat(),
                        'duration_us': log_entry[2],
                        'command': command,
                    })
                    
        except Exception as e:
            logger.warning(f"获取慢查询日志失败: {e}")
            traceback.print_exc()
            metrics['slowlog'] = []
        
        return {
            'success': True,
            'data': metrics
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取Redis监控数据失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"获取Redis监控数据失败: {str(e)}")


@router.get("/config/{namespace}")
async def get_redis_config(namespace: str) -> Dict[str, Any]:
    """
    获取Redis配置信息
    """
    try:
        namespace_data = get_namespace_data_access()
        connection = await namespace_data.manager.get_connection(namespace)
        
        if not connection:
            raise HTTPException(status_code=404, detail=f"命名空间 {namespace} 不存在")
        
        # 获取Redis客户端
        redis_client = await connection.get_redis_client(decode=True)
        
        # 获取所有配置
        config = await redis_client.config_get()
        
        # 组织配置信息
        important_configs = {
            'maxmemory': config.get('maxmemory', '0'),
            'maxmemory-policy': config.get('maxmemory-policy', 'noeviction'),
            'timeout': config.get('timeout', '0'),
            'tcp-keepalive': config.get('tcp-keepalive', '0'),
            'databases': config.get('databases', '16'),
            'save': config.get('save', ''),
            'appendonly': config.get('appendonly', 'no'),
            'appendfsync': config.get('appendfsync', 'everysec'),
            'slowlog-log-slower-than': config.get('slowlog-log-slower-than', '10000'),
            'slowlog-max-len': config.get('slowlog-max-len', '128'),
        }
        
        return {
            'success': True,
            'data': {
                'namespace': namespace,
                'important_configs': important_configs,
                'all_configs': config
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取Redis配置失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"获取Redis配置失败: {str(e)}")


@router.post("/command/{namespace}")
async def execute_redis_command(
    namespace: str,
    command: str,
    args: List[str] = None
) -> Dict[str, Any]:
    """
    执行Redis命令（仅限安全的只读命令）
    """
    # 允许的安全命令白名单
    SAFE_COMMANDS = {
        'ping', 'info', 'dbsize', 'lastsave', 'type', 'ttl', 'pttl',
        'exists', 'keys', 'scan', 'get', 'mget', 'strlen', 'getrange',
        'llen', 'lrange', 'lindex', 'scard', 'smembers', 'sismember',
        'zcard', 'zrange', 'zrevrange', 'zrank', 'zrevrank', 'zscore',
        'hlen', 'hkeys', 'hvals', 'hget', 'hmget', 'hgetall', 'hexists',
        'memory', 'client', 'config', 'slowlog'
    }
    
    command_lower = command.lower()
    
    # 检查命令是否在白名单中
    if command_lower not in SAFE_COMMANDS:
        raise HTTPException(
            status_code=403, 
            detail=f"命令 {command} 不被允许。仅支持只读命令。"
        )
    
    try:
        namespace_data = get_namespace_data_access()
        connection = await namespace_data.manager.get_connection(namespace)
        
        if not connection:
            raise HTTPException(status_code=404, detail=f"命名空间 {namespace} 不存在")
        
        # 获取Redis客户端
        redis_client = await connection.get_redis_client(decode=True)
        
        # 执行命令
        if args:
            result = await redis_client.execute_command(command, *args)
        else:
            result = await redis_client.execute_command(command)
        
        # 处理不同类型的返回值
        if isinstance(result, bytes):
            result = result.decode('utf-8')
        elif isinstance(result, (list, tuple)):
            result = [r.decode('utf-8') if isinstance(r, bytes) else r for r in result]
        
        return {
            'success': True,
            'data': {
                'command': f"{command} {' '.join(args or [])}".strip(),
                'result': result
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"执行Redis命令失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"执行Redis命令失败: {str(e)}")


@router.get("/performance/{namespace}")
async def get_redis_performance(
    namespace: str,
    duration_seconds: int = 5
) -> Dict[str, Any]:
    """
    获取Redis性能测试数据
    通过执行多次PING命令来测试延迟
    """
    try:
        namespace_data = get_namespace_data_access()
        connection = await namespace_data.manager.get_connection(namespace)
        
        if not connection:
            raise HTTPException(status_code=404, detail=f"命名空间 {namespace} 不存在")
        
        # 获取Redis客户端
        redis_client = await connection.get_redis_client(decode=True)
        
        # 性能测试
        latencies = []
        test_count = 100
        
        for _ in range(test_count):
            start_time = time.perf_counter()
            await redis_client.ping()
            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000
            latencies.append(latency_ms)
            await asyncio.sleep(duration_seconds / test_count)
        
        # 计算统计数据
        latencies.sort()
        avg_latency = sum(latencies) / len(latencies)
        min_latency = latencies[0]
        max_latency = latencies[-1]
        p50_latency = latencies[int(len(latencies) * 0.5)]
        p95_latency = latencies[int(len(latencies) * 0.95)]
        p99_latency = latencies[int(len(latencies) * 0.99)]
        
        return {
            'success': True,
            'data': {
                'namespace': namespace,
                'test_count': test_count,
                'duration_seconds': duration_seconds,
                'latency_ms': {
                    'avg': round(avg_latency, 3),
                    'min': round(min_latency, 3),
                    'max': round(max_latency, 3),
                    'p50': round(p50_latency, 3),
                    'p95': round(p95_latency, 3),
                    'p99': round(p99_latency, 3),
                },
                'timestamp': datetime.now().isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Redis性能测试失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Redis性能测试失败: {str(e)}")