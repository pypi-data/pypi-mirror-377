"""
初始化任务中心元数据库
这个脚本用于创建任务中心自己的数据库和表结构
"""
import psycopg2
import sys
from config import task_center_config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_meta_database():
    """创建任务中心元数据库"""
    # 连接到postgres数据库来创建新数据库
    conn = psycopg2.connect(
        host=task_center_config.meta_db_host,
        port=task_center_config.meta_db_port,
        user=task_center_config.meta_db_user,
        password=task_center_config.meta_db_password,
        database='postgres'
    )
    conn.autocommit = True
    cur = conn.cursor()
    
    try:
        # 检查数据库是否存在
        cur.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (task_center_config.meta_db_name,)
        )
        
        if not cur.fetchone():
            # 创建数据库
            cur.execute(f"CREATE DATABASE {task_center_config.meta_db_name}")
            logger.info(f"Created database: {task_center_config.meta_db_name}")
        else:
            logger.info(f"Database already exists: {task_center_config.meta_db_name}")
    
    finally:
        cur.close()
        conn.close()


def init_meta_tables():
    """初始化元数据表"""
    conn = psycopg2.connect(task_center_config.sync_meta_database_url)
    cur = conn.cursor()
    
    try:
        # 创建命名空间表
        cur.execute("""
            CREATE TABLE IF NOT EXISTS namespaces (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name VARCHAR(255) NOT NULL UNIQUE,
                description TEXT,
                -- JetTask应用使用的Redis配置
                redis_config JSONB NOT NULL COMMENT 'JetTask应用的Redis配置',
                -- JetTask应用使用的PostgreSQL配置
                pg_config JSONB NOT NULL COMMENT 'JetTask应用的PostgreSQL配置',
                is_active BOOLEAN DEFAULT true,
                version INTEGER DEFAULT 1,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # 创建索引
        cur.execute("CREATE INDEX IF NOT EXISTS idx_namespaces_name ON namespaces(name);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_namespaces_is_active ON namespaces(is_active);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_namespaces_version ON namespaces(version);")
        
        # 创建更新时间触发器
        cur.execute("""
            CREATE OR REPLACE FUNCTION update_namespaces_updated_at()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """)
        
        cur.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_trigger 
                    WHERE tgname = 'update_namespaces_updated_at'
                ) THEN
                    CREATE TRIGGER update_namespaces_updated_at
                        BEFORE UPDATE ON namespaces
                        FOR EACH ROW
                        EXECUTE FUNCTION update_namespaces_updated_at();
                END IF;
            END;
            $$;
        """)
        
        # 插入默认命名空间
        cur.execute("""
            INSERT INTO namespaces (id, name, description, redis_config, pg_config)
            VALUES (
                'a8f10720-068b-4264-bcbb-e00ceba370e9',
                'default',
                '默认命名空间 - JetTask应用使用此配置',
                '{"host": "localhost", "port": 6379, "password": null, "db": 0}',
                '{"host": "localhost", "port": 5432, "user": "jettask", "password": "123456", "database": "jettask"}'
            )
            ON CONFLICT (name) DO NOTHING;
        """)
        
        conn.commit()
        logger.info("Initialized meta tables successfully")
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to initialize meta tables: {e}")
        raise
    finally:
        cur.close()
        conn.close()


def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("任务中心元数据库初始化")
    logger.info("=" * 60)
    logger.info(f"元数据库地址: {task_center_config.meta_db_host}:{task_center_config.meta_db_port}")
    logger.info(f"元数据库名称: {task_center_config.meta_db_name}")
    logger.info(f"元数据库用户: {task_center_config.meta_db_user}")
    logger.info("-" * 60)
    
    try:
        # 1. 创建数据库
        create_meta_database()
        
        # 2. 初始化表结构
        init_meta_tables()
        
        logger.info("-" * 60)
        logger.info("✅ 元数据库初始化完成！")
        logger.info("")
        logger.info("说明：")
        logger.info("1. 任务中心元数据库用于存储命名空间配置")
        logger.info("2. 每个命名空间定义了JetTask应用使用的Redis和PostgreSQL配置")
        logger.info("3. JetTask应用通过命名空间ID获取其专用的数据库配置")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"初始化失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()