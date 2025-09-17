-- JetTask 数据库初始化脚本
-- 包含所有表结构、索引、函数和分区设置

-- ========================================
-- 1. 创建更新时间触发器函数
-- ========================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ========================================
-- 2. 创建 namespaces 表
-- ========================================
CREATE TABLE IF NOT EXISTS namespaces (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    connection_url TEXT NOT NULL,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 插入默认命名空间
INSERT INTO namespaces (name, description, connection_url, is_default)
VALUES ('default', 'Default namespace', 'redis://localhost:6379/0', true)
ON CONFLICT (name) DO NOTHING;

-- ========================================
-- 3. 创建 scheduled_tasks 表
-- ========================================
CREATE TABLE IF NOT EXISTS scheduled_tasks (
    id BIGSERIAL PRIMARY KEY,
    scheduler_id VARCHAR(255) UNIQUE NOT NULL,
    task_name VARCHAR(255) NOT NULL,
    task_type VARCHAR(50) NOT NULL,
    queue_name VARCHAR(100) NOT NULL,
    task_args JSONB DEFAULT '[]'::jsonb,
    task_kwargs JSONB DEFAULT '{}'::jsonb,
    cron_expression VARCHAR(100),
    interval_seconds NUMERIC(10,2),
    next_run_time TIMESTAMPTZ,
    last_run_time TIMESTAMPTZ,
    enabled BOOLEAN DEFAULT true,
    max_retries INTEGER DEFAULT 3,
    retry_delay INTEGER DEFAULT 60,
    timeout INTEGER DEFAULT 300,
    description TEXT,
    tags JSONB DEFAULT '[]'::jsonb,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    execution_count INTEGER DEFAULT 0,
    namespace VARCHAR(255) DEFAULT 'default',
    priority INTEGER
);

-- 创建优化后的索引
CREATE INDEX IF NOT EXISTS idx_scheduled_tasks_next_run 
ON scheduled_tasks (next_run_time) 
INCLUDE (scheduler_id, task_name, queue_name, enabled)
WHERE enabled = true;

CREATE INDEX IF NOT EXISTS idx_scheduled_tasks_enabled_ns
ON scheduled_tasks (namespace, enabled)
WHERE enabled = true;

-- 创建触发器
CREATE TRIGGER update_scheduled_tasks_updated_at 
BEFORE UPDATE ON scheduled_tasks 
FOR EACH ROW 
EXECUTE FUNCTION update_updated_at_column();

-- ========================================
-- 4. 创建 tasks 分区表
-- ========================================
CREATE TABLE IF NOT EXISTS tasks (
    stream_id TEXT NOT NULL,
    queue TEXT NOT NULL,
    namespace TEXT NOT NULL DEFAULT 'default',
    scheduled_task_id TEXT,
    payload JSONB NOT NULL,
    priority INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    source TEXT NOT NULL DEFAULT 'redis_stream',
    metadata JSONB DEFAULT '{}',
    PRIMARY KEY (stream_id, created_at)
) PARTITION BY RANGE (created_at);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_tasks_created 
ON tasks (created_at DESC);

CREATE INDEX IF NOT EXISTS idx_tasks_ns_created 
ON tasks (namespace, created_at DESC)
INCLUDE (queue, priority);

CREATE INDEX IF NOT EXISTS idx_tasks_queue_time
ON tasks (queue, created_at DESC)
WHERE namespace = 'default';

CREATE INDEX IF NOT EXISTS idx_tasks_scheduled_id
ON tasks (scheduled_task_id, created_at DESC)
WHERE scheduled_task_id IS NOT NULL;

-- ========================================
-- 5. 创建 task_runs 分区表
-- ========================================
CREATE TABLE IF NOT EXISTS task_runs (
    id BIGSERIAL,
    stream_id TEXT NOT NULL,
    task_name TEXT NOT NULL,
    consumer_group TEXT NOT NULL,
    consumer_name TEXT,
    worker_id TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    start_time TIMESTAMPTZ,
    end_time TIMESTAMPTZ,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    error_message TEXT,
    error_details JSONB,
    result JSONB,
    logs TEXT[],
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    duration DOUBLE PRECISION,
    execution_time DOUBLE PRECISION,
    PRIMARY KEY (id, created_at),
    UNIQUE (stream_id, consumer_group, created_at)
) PARTITION BY RANGE (created_at);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_task_runs_stream_covering 
ON task_runs (stream_id, created_at) 
INCLUDE (status, execution_time, end_time, start_time);

CREATE INDEX IF NOT EXISTS idx_task_runs_status_created
ON task_runs (status, created_at);

CREATE INDEX IF NOT EXISTS idx_task_runs_success_time
ON task_runs (end_time DESC, created_at) 
WHERE status = 'success';

CREATE INDEX IF NOT EXISTS idx_task_runs_consumer_created 
ON task_runs (consumer_group, created_at DESC);

-- 创建触发器
CREATE TRIGGER update_task_runs_updated_at 
BEFORE UPDATE ON task_runs 
FOR EACH ROW 
EXECUTE FUNCTION update_updated_at_column();

-- ========================================
-- 6. 创建 stream_backlog_monitor 分区表
-- ========================================
CREATE TABLE IF NOT EXISTS stream_backlog_monitor (
    id BIGSERIAL,
    namespace TEXT NOT NULL DEFAULT 'default',
    stream_name TEXT NOT NULL,
    consumer_group TEXT,
    priority INTEGER,
    last_published_offset TEXT,
    last_consumed_offset TEXT,
    last_delivered_offset BIGINT DEFAULT 0,  -- 最后投递的偏移量
    last_acked_offset BIGINT DEFAULT 0,      -- 最后确认的偏移量
    consumer_lag BIGINT,
    pending_count BIGINT DEFAULT 0,          -- 待处理任务数
    backlog_undelivered BIGINT DEFAULT 0,    -- 未投递的积压数
    backlog_unprocessed BIGINT DEFAULT 0,    -- 未处理的积压数
    task_count BIGINT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    collected_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}',
    PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_stream_backlog_namespace_stream 
ON stream_backlog_monitor (namespace, stream_name, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_stream_backlog_created 
ON stream_backlog_monitor (created_at DESC);

-- ========================================
-- 7. 创建 alert_rules 表
-- ========================================
CREATE TABLE IF NOT EXISTS alert_rules (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    rule_type VARCHAR(50) NOT NULL,
    metric VARCHAR(100) NOT NULL,
    condition VARCHAR(20) NOT NULL,
    threshold DOUBLE PRECISION NOT NULL,
    duration_seconds INTEGER DEFAULT 60,
    enabled BOOLEAN DEFAULT true,
    alert_channels JSONB DEFAULT '[]'::jsonb,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_alert_rules_enabled 
ON alert_rules (enabled) WHERE enabled = true;

-- 创建触发器
CREATE TRIGGER update_alert_rules_updated_at 
BEFORE UPDATE ON alert_rules 
FOR EACH ROW 
EXECUTE FUNCTION update_updated_at_column();

-- ========================================
-- 8. 创建 alert_history 表
-- ========================================
CREATE TABLE IF NOT EXISTS alert_history (
    id BIGSERIAL PRIMARY KEY,
    rule_id BIGINT REFERENCES alert_rules(id),
    alert_time TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    metric_value DOUBLE PRECISION,
    threshold_value DOUBLE PRECISION,
    alert_message TEXT,
    alert_level VARCHAR(20),
    resolved BOOLEAN DEFAULT false,
    resolved_time TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_alert_history_rule_id 
ON alert_history (rule_id, alert_time DESC);

CREATE INDEX IF NOT EXISTS idx_alert_history_unresolved 
ON alert_history (resolved, alert_time DESC) WHERE resolved = false;

-- ========================================
-- 9. 分区管理函数
-- ========================================

-- tasks 表分区管理
CREATE OR REPLACE FUNCTION create_tasks_partition()
RETURNS void AS $$
DECLARE
    start_date date;
    end_date date;
    partition_name text;
BEGIN
    -- 创建当前月分区
    start_date := date_trunc('month', CURRENT_DATE);
    end_date := start_date + interval '1 month';
    partition_name := 'tasks_' || to_char(start_date, 'YYYY_MM');
    
    IF NOT EXISTS (
        SELECT 1 FROM pg_class WHERE relname = partition_name
    ) THEN
        EXECUTE format(
            'CREATE TABLE %I PARTITION OF tasks 
            FOR VALUES FROM (%L) TO (%L)',
            partition_name, start_date, end_date
        );
        RAISE NOTICE 'Created partition: %', partition_name;
    END IF;
    
    -- 创建下月分区
    start_date := date_trunc('month', CURRENT_DATE + interval '1 month');
    end_date := start_date + interval '1 month';
    partition_name := 'tasks_' || to_char(start_date, 'YYYY_MM');
    
    IF NOT EXISTS (
        SELECT 1 FROM pg_class WHERE relname = partition_name
    ) THEN
        EXECUTE format(
            'CREATE TABLE %I PARTITION OF tasks 
            FOR VALUES FROM (%L) TO (%L)',
            partition_name, start_date, end_date
        );
        RAISE NOTICE 'Created partition: %', partition_name;
    END IF;
    
    -- 创建上月分区
    start_date := date_trunc('month', CURRENT_DATE - interval '1 month');
    end_date := start_date + interval '1 month';
    partition_name := 'tasks_' || to_char(start_date, 'YYYY_MM');
    
    IF NOT EXISTS (
        SELECT 1 FROM pg_class WHERE relname = partition_name
    ) THEN
        EXECUTE format(
            'CREATE TABLE %I PARTITION OF tasks 
            FOR VALUES FROM (%L) TO (%L)',
            partition_name, start_date, end_date
        );
        RAISE NOTICE 'Created partition: %', partition_name;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- task_runs 表分区管理
CREATE OR REPLACE FUNCTION create_task_runs_partition()
RETURNS void AS $$
DECLARE
    start_date date;
    end_date date;
    partition_name text;
BEGIN
    -- 创建当前月份分区
    start_date := date_trunc('month', CURRENT_DATE);
    end_date := start_date + interval '1 month';
    partition_name := 'task_runs_' || to_char(start_date, 'YYYY_MM');
    
    IF NOT EXISTS (
        SELECT 1 FROM pg_class WHERE relname = partition_name
    ) THEN
        EXECUTE format(
            'CREATE TABLE %I PARTITION OF task_runs 
            FOR VALUES FROM (%L) TO (%L)',
            partition_name, start_date, end_date
        );
        RAISE NOTICE 'Created partition: %', partition_name;
    END IF;
    
    -- 创建下个月分区
    start_date := date_trunc('month', CURRENT_DATE + interval '1 month');
    end_date := start_date + interval '1 month';
    partition_name := 'task_runs_' || to_char(start_date, 'YYYY_MM');
    
    IF NOT EXISTS (
        SELECT 1 FROM pg_class WHERE relname = partition_name
    ) THEN
        EXECUTE format(
            'CREATE TABLE %I PARTITION OF task_runs 
            FOR VALUES FROM (%L) TO (%L)',
            partition_name, start_date, end_date
        );
        RAISE NOTICE 'Created partition: %', partition_name;
    END IF;
    
    -- 创建前一个月分区
    start_date := date_trunc('month', CURRENT_DATE - interval '1 month');
    end_date := start_date + interval '1 month';
    partition_name := 'task_runs_' || to_char(start_date, 'YYYY_MM');
    
    IF NOT EXISTS (
        SELECT 1 FROM pg_class WHERE relname = partition_name
    ) THEN
        EXECUTE format(
            'CREATE TABLE %I PARTITION OF task_runs 
            FOR VALUES FROM (%L) TO (%L)',
            partition_name, start_date, end_date
        );
        RAISE NOTICE 'Created partition: %', partition_name;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- stream_backlog_monitor 表分区管理
CREATE OR REPLACE FUNCTION create_stream_backlog_partition()
RETURNS void AS $$
DECLARE
    start_date date;
    end_date date;
    partition_name text;
BEGIN
    -- 创建最近3个月的分区
    FOR i IN -1..1 LOOP
        start_date := date_trunc('month', CURRENT_DATE + (i || ' month')::interval);
        end_date := start_date + interval '1 month';
        partition_name := 'stream_backlog_monitor_' || to_char(start_date, 'YYYY_MM');
        
        IF NOT EXISTS (
            SELECT 1 FROM pg_class WHERE relname = partition_name
        ) THEN
            EXECUTE format(
                'CREATE TABLE %I PARTITION OF stream_backlog_monitor 
                FOR VALUES FROM (%L) TO (%L)',
                partition_name, start_date, end_date
            );
            RAISE NOTICE 'Created partition: %', partition_name;
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- ========================================
-- 10. 分区维护函数
-- ========================================

-- tasks 表维护
CREATE OR REPLACE FUNCTION maintain_tasks_partitions()
RETURNS void AS $$
DECLARE
    partition_date date;
    partition_name text;
    old_partition_date date;
    old_partition_name text;
BEGIN
    -- 创建未来分区
    PERFORM create_tasks_partition();
    
    -- 删除超过2个月的旧分区
    old_partition_date := date_trunc('month', CURRENT_DATE - interval '2 months');
    old_partition_name := 'tasks_' || to_char(old_partition_date, 'YYYY_MM');
    
    IF EXISTS (
        SELECT 1 FROM pg_class WHERE relname = old_partition_name
    ) THEN
        EXECUTE format('DROP TABLE IF EXISTS %I CASCADE', old_partition_name);
        RAISE NOTICE 'Dropped old partition: %', old_partition_name;
    END IF;
    
    -- 对活跃分区执行 VACUUM ANALYZE
    FOR partition_date IN 
        SELECT generate_series(
            date_trunc('month', CURRENT_DATE - interval '1 month'),
            date_trunc('month', CURRENT_DATE),
            interval '1 month'
        )::date
    LOOP
        partition_name := 'tasks_' || to_char(partition_date, 'YYYY_MM');
        IF EXISTS (
            SELECT 1 FROM pg_class WHERE relname = partition_name
        ) THEN
            EXECUTE format('VACUUM ANALYZE %I', partition_name);
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- task_runs 表维护
CREATE OR REPLACE FUNCTION maintain_task_runs_partitions()
RETURNS void AS $$
DECLARE
    partition_date date;
    partition_name text;
    old_partition_date date;
    old_partition_name text;
BEGIN
    -- 创建未来分区
    PERFORM create_task_runs_partition();
    
    -- 删除超过3个月的旧分区
    old_partition_date := date_trunc('month', CURRENT_DATE - interval '3 months');
    old_partition_name := 'task_runs_' || to_char(old_partition_date, 'YYYY_MM');
    
    IF EXISTS (
        SELECT 1 FROM pg_class WHERE relname = old_partition_name
    ) THEN
        EXECUTE format('DROP TABLE IF EXISTS %I', old_partition_name);
        RAISE NOTICE 'Dropped old partition: %', old_partition_name;
    END IF;
    
    -- 对活跃分区执行 VACUUM ANALYZE
    FOR partition_date IN 
        SELECT generate_series(
            date_trunc('month', CURRENT_DATE - interval '1 month'),
            date_trunc('month', CURRENT_DATE + interval '1 month'),
            interval '1 month'
        )::date
    LOOP
        partition_name := 'task_runs_' || to_char(partition_date, 'YYYY_MM');
        IF EXISTS (
            SELECT 1 FROM pg_class WHERE relname = partition_name
        ) THEN
            EXECUTE format('VACUUM ANALYZE %I', partition_name);
            RAISE NOTICE 'Vacuumed partition: %', partition_name;
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- scheduled_tasks 表维护
CREATE OR REPLACE FUNCTION maintain_scheduled_tasks()
RETURNS void AS $$
BEGIN
    -- 重置长时间未执行的任务
    UPDATE scheduled_tasks
    SET next_run_time = CURRENT_TIMESTAMP
    WHERE enabled = true
      AND next_run_time < CURRENT_TIMESTAMP - interval '1 hour';
    
    -- 记录维护日志
    RAISE NOTICE 'Scheduled tasks maintenance completed at %', CURRENT_TIMESTAMP;
    
    -- 更新统计信息
    ANALYZE scheduled_tasks;
END;
$$ LANGUAGE plpgsql;

-- ========================================
-- 11. 创建初始分区
-- ========================================
SELECT create_tasks_partition();
SELECT create_task_runs_partition();
SELECT create_stream_backlog_partition();

-- ========================================
-- 12. 批量操作优化函数
-- ========================================

-- task_runs批量UPSERT函数
CREATE OR REPLACE FUNCTION batch_upsert_task_runs(
    p_records jsonb
) RETURNS INTEGER AS $$
DECLARE
    v_count INTEGER := 0;
    v_record jsonb;
BEGIN
    -- 遍历每条记录
    FOR v_record IN SELECT * FROM jsonb_array_elements(p_records)
    LOOP
        -- 先尝试UPDATE
        UPDATE task_runs SET
            consumer_name = COALESCE((v_record->>'consumer_name')::TEXT, consumer_name),
            status = CASE 
                WHEN (v_record->>'status')::TEXT IS NULL THEN status
                WHEN status = 'pending' THEN COALESCE((v_record->>'status')::TEXT, status)
                WHEN status = 'running' AND (v_record->>'status')::TEXT IN ('success', 'failed', 'timeout', 'skipped') THEN (v_record->>'status')::TEXT
                WHEN status IN ('success', 'failed', 'timeout', 'skipped') THEN status
                ELSE COALESCE((v_record->>'status')::TEXT, status)
            END,
            result = CASE
                WHEN status IN ('success', 'failed', 'timeout', 'skipped') AND (v_record->>'status')::TEXT NOT IN ('success', 'failed', 'timeout', 'skipped') THEN result
                ELSE COALESCE((v_record->>'result')::jsonb, result)
            END,
            error_message = CASE
                WHEN status IN ('success', 'failed', 'timeout', 'skipped') AND (v_record->>'status')::TEXT NOT IN ('success', 'failed', 'timeout', 'skipped') THEN error_message
                ELSE COALESCE((v_record->>'error_message')::TEXT, error_message)
            END,
            start_time = COALESCE((v_record->>'started_at')::TIMESTAMPTZ, start_time),
            end_time = CASE
                WHEN status IN ('success', 'failed', 'timeout', 'skipped') AND (v_record->>'status')::TEXT NOT IN ('success', 'failed', 'timeout', 'skipped') THEN end_time
                ELSE COALESCE((v_record->>'completed_at')::TIMESTAMPTZ, end_time)
            END,
            worker_id = COALESCE((v_record->>'worker_id')::TEXT, worker_id),
            duration = COALESCE((v_record->>'duration')::DOUBLE PRECISION, duration),
            execution_time = COALESCE((v_record->>'execution_time')::DOUBLE PRECISION, execution_time),
            updated_at = CURRENT_TIMESTAMP
        WHERE stream_id = (v_record->>'stream_id')::TEXT 
          AND consumer_group = (v_record->>'consumer_group')::TEXT;
        
        -- 如果没有更新到任何行，则INSERT
        IF NOT FOUND THEN
            INSERT INTO task_runs (
                stream_id, task_name, consumer_group, consumer_name, status, result, error_message, 
                start_time, end_time, worker_id, duration, execution_time,
                created_at, updated_at
            ) VALUES (
                (v_record->>'stream_id')::TEXT,
                (v_record->>'task_name')::TEXT,
                (v_record->>'consumer_group')::TEXT,
                (v_record->>'consumer_name')::TEXT,
                COALESCE((v_record->>'status')::TEXT, 'pending'),
                (v_record->>'result')::jsonb,
                (v_record->>'error_message')::TEXT,
                (v_record->>'started_at')::TIMESTAMPTZ,
                (v_record->>'completed_at')::TIMESTAMPTZ,
                (v_record->>'worker_id')::TEXT,
                (v_record->>'duration')::DOUBLE PRECISION,
                (v_record->>'execution_time')::DOUBLE PRECISION,
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP
            );
        END IF;
        
        v_count := v_count + 1;
    END LOOP;
    
    RETURN v_count;
END;
$$ LANGUAGE plpgsql;

-- 批量插入tasks的优化函数
CREATE OR REPLACE FUNCTION batch_insert_tasks(
    p_records jsonb
) RETURNS INTEGER AS $$
DECLARE
    v_inserted INTEGER;
BEGIN
    -- 使用单个INSERT语句批量插入，忽略冲突
    WITH data AS (
        SELECT 
            (value->>'stream_id')::TEXT as stream_id,
            (value->>'queue')::TEXT as queue,
            (value->>'namespace')::TEXT as namespace,
            (value->>'scheduled_task_id')::TEXT as scheduled_task_id,
            (value->>'payload')::jsonb as payload,
            (value->>'priority')::INTEGER as priority,
            (value->>'created_at')::TIMESTAMPTZ as created_at,
            (value->>'source')::TEXT as source,
            (value->>'metadata')::jsonb as metadata
        FROM jsonb_array_elements(p_records)
    )
    INSERT INTO tasks (stream_id, queue, namespace, scheduled_task_id, payload, priority, created_at, source, metadata)
    SELECT * FROM data
    ON CONFLICT DO NOTHING;
    
    GET DIAGNOSTICS v_inserted = ROW_COUNT;
    RETURN v_inserted;
END;
$$ LANGUAGE plpgsql;

-- 批量清理已完成任务的函数
CREATE OR REPLACE FUNCTION cleanup_completed_tasks(
    p_stream_ids TEXT[]
) RETURNS INTEGER AS $$
DECLARE
    v_deleted INTEGER;
BEGIN
    -- 批量删除已完成的任务
    DELETE FROM task_runs 
    WHERE stream_id = ANY(p_stream_ids)
      AND status IN ('success', 'failed', 'timeout', 'skipped', 'cancelled');
    
    GET DIAGNOSTICS v_deleted = ROW_COUNT;
    RETURN v_deleted;
END;
$$ LANGUAGE plpgsql;

-- ========================================
-- 13. 创建额外的优化索引
-- ========================================

-- 为task_runs的UPSERT操作创建覆盖索引（如果不存在）
CREATE INDEX IF NOT EXISTS idx_task_runs_upsert 
ON task_runs (stream_id, consumer_group) 
INCLUDE (status, updated_at);

-- ========================================
-- 14. 创建默认数据
-- ========================================
-- 这里可以插入一些默认的配置或测试数据

-- ========================================
-- 完成
-- ========================================
-- 注意：最后的 RAISE NOTICE 可能在某些环境中不支持，可以注释掉
-- RAISE NOTICE 'Database initialization completed successfully!';