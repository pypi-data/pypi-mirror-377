"""
Namespace management API v1
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import (
    get_database_manager, get_request_metrics, RequestMetrics,
    validate_page_params
)
from models.requests import NamespaceCreateRequest, NamespaceUpdateRequest, NamespaceListRequest
from models.responses import NamespaceListResponse, NamespaceResponse, BaseResponse
from core.cache import cache_result, invalidate_cache, CACHE_CONFIGS
from core.exceptions import NamespaceNotFoundError, ValidationError
from namespace_data_access import get_namespace_data_access
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("", response_model=NamespaceListResponse)
@cache_result(**CACHE_CONFIGS['namespace_config'])
async def list_namespaces(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
    is_active: Optional[bool] = Query(None, description="是否启用"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    metrics: RequestMetrics = Depends(get_request_metrics)
):
    """获取命名空间列表"""
    metrics.start("system", "GET /namespaces")
    
    try:
        namespace_data_access = get_namespace_data_access()
        
        # 获取所有命名空间配置
        all_namespaces = await namespace_data_access.list_namespaces()
        
        # 转换为响应格式
        namespace_list = []
        for ns_config in all_namespaces:
            namespace_info = {
                'id': ns_config.get('id', ns_config['name']),
                'name': ns_config['name'],
                'display_name': ns_config.get('display_name', ns_config['name']),
                'description': ns_config.get('description'),
                'redis_url': ns_config['redis_url'],
                'pg_url': ns_config.get('pg_url'),
                'created_at': ns_config.get('created_at'),
                'is_active': ns_config.get('is_active', True),
                'queue_count': 0,  # 可以后续查询实际数量
                'task_count': 0   # 可以后续查询实际数量
            }
            
            # 应用搜索筛选
            if search:
                if (search.lower() not in namespace_info['name'].lower() and 
                    search.lower() not in (namespace_info['display_name'] or '').lower()):
                    continue
            
            # 应用状态筛选
            if is_active is not None and namespace_info['is_active'] != is_active:
                continue
            
            namespace_list.append(namespace_info)
        
        # 分页
        total = len(namespace_list)
        start = (page - 1) * page_size
        end = start + page_size
        paginated_namespaces = namespace_list[start:end]
        
        return NamespaceListResponse.create(
            data=paginated_namespaces,
            total=total,
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        logger.error(f"获取命名空间列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        metrics.finish()


@router.get("/{namespace_name}", response_model=NamespaceResponse)
@cache_result(**CACHE_CONFIGS['namespace_config'])
async def get_namespace_detail(
    namespace_name: str,
    metrics: RequestMetrics = Depends(get_request_metrics)
):
    """获取命名空间详情"""
    metrics.start("system", f"GET /namespaces/{namespace_name}")
    
    try:
        namespace_data_access = get_namespace_data_access()
        
        # 获取命名空间配置
        ns_config = await namespace_data_access.get_namespace_config(namespace_name)
        if not ns_config:
            raise NamespaceNotFoundError(namespace_name)
        
        # 获取连接以检查状态和统计信息
        try:
            conn = await namespace_data_access.manager.get_connection(namespace_name)
            
            # 获取队列统计
            queue_count = 0
            task_count = 0
            
            try:
                # 从Redis获取队列数量
                redis_client = await conn.get_redis_client(decode=False)
                try:
                    # 查询所有队列键
                    pattern = f"{conn.redis_prefix}:QUEUE:*"
                    keys = await redis_client.keys(pattern)
                    
                    # 去重基础队列名
                    base_queues = set()
                    for key in keys:
                        key_str = key.decode('utf-8') if isinstance(key, bytes) else key
                        parts = key_str.split(':')
                        if len(parts) >= 3:
                            queue_part = ':'.join(parts[2:])
                            # 去除优先级后缀
                            if ':' in queue_part:
                                base_part = queue_part.rsplit(':', 1)
                                if base_part[1].isdigit():
                                    base_queues.add(base_part[0])
                                else:
                                    base_queues.add(queue_part)
                            else:
                                base_queues.add(queue_part)
                    
                    queue_count = len(base_queues)
                finally:
                    await redis_client.aclose()
                
                # 从PostgreSQL获取任务数量
                if conn.AsyncSessionLocal:
                    async with conn.AsyncSessionLocal() as session:
                        result = await session.execute("SELECT COUNT(*) FROM tasks")
                        row = result.fetchone()
                        if row:
                            task_count = row[0]
            
            except Exception as e:
                logger.warning(f"获取命名空间 {namespace_name} 统计信息失败: {e}")
        
        except Exception as e:
            logger.warning(f"连接命名空间 {namespace_name} 失败: {e}")
        
        # 构造响应
        namespace_detail = {
            'id': ns_config.get('id', namespace_name),
            'name': namespace_name,
            'display_name': ns_config.get('display_name', namespace_name),
            'description': ns_config.get('description'),
            'redis_url': ns_config['redis_url'],
            'pg_url': ns_config.get('pg_url'),
            'created_at': ns_config.get('created_at'),
            'is_active': ns_config.get('is_active', True),
            'queue_count': queue_count,
            'task_count': task_count
        }
        
        return NamespaceResponse(data=namespace_detail)
        
    except NamespaceNotFoundError:
        raise
    except Exception as e:
        logger.error(f"获取命名空间详情失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        metrics.finish()


@router.post("", response_model=NamespaceResponse)
@invalidate_cache("namespace_config")
async def create_namespace(
    request: NamespaceCreateRequest,
    metrics: RequestMetrics = Depends(get_request_metrics)
):
    """创建命名空间"""
    metrics.start("system", "POST /namespaces")
    
    try:
        namespace_data_access = get_namespace_data_access()
        
        # 检查命名空间是否已存在
        existing_config = await namespace_data_access.get_namespace_config(request.name)
        if existing_config:
            raise ValidationError(f"Namespace '{request.name}' already exists")
        
        # 验证连接配置
        await _validate_connection_config(request.redis_url, request.pg_url)
        
        # 创建命名空间配置
        ns_config = {
            'name': request.name,
            'display_name': request.display_name,
            'description': request.description,
            'redis_url': request.redis_url,
            'pg_url': request.pg_url,
            'redis_prefix': request.redis_prefix,
            'is_active': True
        }
        
        created_config = await namespace_data_access.create_namespace(ns_config)
        
        # 构造响应
        namespace_detail = {
            'id': created_config.get('id', request.name),
            'name': request.name,
            'display_name': request.display_name,
            'description': request.description,
            'redis_url': request.redis_url,
            'pg_url': request.pg_url,
            'created_at': created_config.get('created_at'),
            'is_active': True,
            'queue_count': 0,
            'task_count': 0
        }
        
        return NamespaceResponse(
            data=namespace_detail,
            message="Namespace created successfully"
        )
        
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"创建命名空间失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        metrics.finish()


@router.put("/{namespace_name}", response_model=NamespaceResponse)
@invalidate_cache("namespace_config")
async def update_namespace(
    namespace_name: str,
    request: NamespaceUpdateRequest,
    metrics: RequestMetrics = Depends(get_request_metrics)
):
    """更新命名空间"""
    metrics.start("system", f"PUT /namespaces/{namespace_name}")
    
    try:
        namespace_data_access = get_namespace_data_access()
        
        # 检查命名空间是否存在
        existing_config = await namespace_data_access.get_namespace_config(namespace_name)
        if not existing_config:
            raise NamespaceNotFoundError(namespace_name)
        
        # 构造更新数据
        update_data = {}
        if request.display_name is not None:
            update_data['display_name'] = request.display_name
        if request.description is not None:
            update_data['description'] = request.description
        if request.is_active is not None:
            update_data['is_active'] = request.is_active
        
        # 验证连接配置更新
        if request.redis_url or request.pg_url:
            redis_url = request.redis_url or existing_config['redis_url']
            pg_url = request.pg_url or existing_config.get('pg_url')
            await _validate_connection_config(redis_url, pg_url)
            
            if request.redis_url:
                update_data['redis_url'] = request.redis_url
            if request.pg_url:
                update_data['pg_url'] = request.pg_url
        
        # 执行更新
        updated_config = await namespace_data_access.update_namespace(namespace_name, update_data)
        
        # 构造响应
        namespace_detail = {
            'id': updated_config.get('id', namespace_name),
            'name': namespace_name,
            'display_name': updated_config.get('display_name', namespace_name),
            'description': updated_config.get('description'),
            'redis_url': updated_config['redis_url'],
            'pg_url': updated_config.get('pg_url'),
            'created_at': updated_config.get('created_at'),
            'is_active': updated_config.get('is_active', True),
            'queue_count': 0,  # 可以后续查询实际数量
            'task_count': 0   # 可以后续查询实际数量
        }
        
        return NamespaceResponse(
            data=namespace_detail,
            message="Namespace updated successfully"
        )
        
    except NamespaceNotFoundError:
        raise
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"更新命名空间失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        metrics.finish()


@router.delete("/{namespace_name}", response_model=BaseResponse)
@invalidate_cache("namespace_config")
async def delete_namespace(
    namespace_name: str,
    force: bool = Query(False, description="是否强制删除"),
    metrics: RequestMetrics = Depends(get_request_metrics)
):
    """删除命名空间"""
    metrics.start("system", f"DELETE /namespaces/{namespace_name}")
    
    try:
        if namespace_name == "default":
            raise ValidationError("Cannot delete the default namespace")
        
        namespace_data_access = get_namespace_data_access()
        
        # 检查命名空间是否存在
        existing_config = await namespace_data_access.get_namespace_config(namespace_name)
        if not existing_config:
            raise NamespaceNotFoundError(namespace_name)
        
        # 检查是否有活跃的队列或任务（如果不是强制删除）
        if not force:
            try:
                conn = await namespace_data_access.manager.get_connection(namespace_name)
                
                # 检查Redis中是否有队列
                redis_client = await conn.get_redis_client(decode=False)
                try:
                    pattern = f"{conn.redis_prefix}:QUEUE:*"
                    keys = await redis_client.keys(pattern)
                    if keys:
                        raise ValidationError(
                            f"Namespace has {len(keys)} active queues. Use force=true to delete anyway."
                        )
                finally:
                    await redis_client.aclose()
                
                # 检查PostgreSQL中是否有任务
                if conn.AsyncSessionLocal:
                    async with conn.AsyncSessionLocal() as session:
                        result = await session.execute("SELECT COUNT(*) FROM tasks")
                        row = result.fetchone()
                        if row and row[0] > 0:
                            raise ValidationError(
                                f"Namespace has {row[0]} tasks. Use force=true to delete anyway."
                            )
            
            except ValidationError:
                raise
            except Exception as e:
                logger.warning(f"检查命名空间 {namespace_name} 资源失败: {e}")
        
        # 执行删除
        success = await namespace_data_access.delete_namespace(namespace_name)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete namespace")
        
        return BaseResponse(
            message=f"Namespace '{namespace_name}' deleted successfully"
        )
        
    except NamespaceNotFoundError:
        raise
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"删除命名空间失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        metrics.finish()


@router.post("/{namespace_name}/test-connection", response_model=BaseResponse)
async def test_namespace_connection(
    namespace_name: str,
    metrics: RequestMetrics = Depends(get_request_metrics)
):
    """测试命名空间连接"""
    metrics.start("system", f"POST /namespaces/{namespace_name}/test-connection")
    
    try:
        namespace_data_access = get_namespace_data_access()
        
        # 获取命名空间配置
        ns_config = await namespace_data_access.get_namespace_config(namespace_name)
        if not ns_config:
            raise NamespaceNotFoundError(namespace_name)
        
        # 测试连接
        connection_results = await _test_connections(
            ns_config['redis_url'],
            ns_config.get('pg_url')
        )
        
        overall_status = "healthy" if all(r['status'] == 'healthy' for r in connection_results.values()) else "unhealthy"
        
        return BaseResponse(
            data={
                'namespace': namespace_name,
                'overall_status': overall_status,
                'connections': connection_results
            },
            message=f"Connection test completed for namespace '{namespace_name}'"
        )
        
    except NamespaceNotFoundError:
        raise
    except Exception as e:
        logger.error(f"测试命名空间连接失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        metrics.finish()


# 辅助函数

async def _validate_connection_config(redis_url: str, pg_url: Optional[str] = None):
    """验证连接配置"""
    connection_results = await _test_connections(redis_url, pg_url)
    
    failed_connections = [
        name for name, result in connection_results.items()
        if result['status'] != 'healthy'
    ]
    
    if failed_connections:
        raise ValidationError(
            f"Connection validation failed for: {', '.join(failed_connections)}"
        )


async def _test_connections(redis_url: str, pg_url: Optional[str] = None) -> dict:
    """测试数据库连接"""
    results = {}
    
    # 测试Redis连接
    try:
        import redis.asyncio as redis
        redis_client = redis.from_url(redis_url, decode_responses=False)
        await redis_client.ping()
        await redis_client.aclose()
        results['redis'] = {
            'status': 'healthy',
            'url': redis_url,
            'message': 'Connection successful'
        }
    except Exception as e:
        results['redis'] = {
            'status': 'unhealthy',
            'url': redis_url,
            'message': f'Connection failed: {str(e)}'
        }
    
    # 测试PostgreSQL连接（如果提供）
    if pg_url:
        try:
            import asyncpg
            
            # 解析连接字符串
            if pg_url.startswith('postgresql://'):
                connection_string = pg_url.replace('postgresql://', '')
            elif pg_url.startswith('postgresql+asyncpg://'):
                connection_string = pg_url.replace('postgresql+asyncpg://', '')
            else:
                connection_string = pg_url
            
            auth, host_info = connection_string.split('@')
            user, password = auth.split(':')
            host_port, database = host_info.split('/')
            host, port = host_port.split(':')
            
            conn = await asyncpg.connect(
                host=host, port=int(port), user=user, password=password, database=database
            )
            await conn.execute("SELECT 1")
            await conn.close()
            
            results['postgresql'] = {
                'status': 'healthy',
                'url': pg_url,
                'message': 'Connection successful'
            }
        except Exception as e:
            results['postgresql'] = {
                'status': 'unhealthy', 
                'url': pg_url,
                'message': f'Connection failed: {str(e)}'
            }
    
    return results