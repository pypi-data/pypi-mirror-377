import { useState, useEffect, useCallback } from 'react';
import { Card, Row, Col, Statistic, Space, Select, Button, Tag, Spin, Empty, Tooltip, Table, Progress, Alert } from 'antd';
import {
  ReloadOutlined,
  InfoCircleOutlined,
  RiseOutlined,
  FallOutlined,
  ArrowUpOutlined,
  ArrowDownOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  SyncOutlined,
  ExclamationCircleOutlined,
  DashboardOutlined,
  DatabaseOutlined,
  CloudServerOutlined,
  ThunderboltOutlined,
  RocketOutlined,
  TeamOutlined,
  WarningOutlined,
  PieChartOutlined
} from '@ant-design/icons';
import { Line, Area, Column, Pie, Gauge } from '@ant-design/plots';
import { useNamespace } from '../contexts/NamespaceContext';
import dayjs from 'dayjs';
import axios from 'axios';
import QueueBacklogTrend from '../components/QueueBacklogTrend';

const { Option } = Select;

// 时间范围选项
const TIME_RANGES = {
  '15m': '15分钟',
  '30m': '30分钟',
  '1h': '1小时',
  '3h': '3小时',
  '6h': '6小时',
  '12h': '12小时',
  '24h': '24小时',
  '7d': '7天'
};

function Dashboard() {
  const { currentNamespace } = useNamespace();
  
  // 添加调试输出，直接显示在页面上
  console.log('🔧 Dashboard组件渲染，currentNamespace:', currentNamespace);
  const [loading, setLoading] = useState(false);
  const [timeRange, setTimeRange] = useState('1h');
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval] = useState(30000); // 30秒自动刷新
  const [granularity, setGranularity] = useState('');
  const [hasAnimated, setHasAnimated] = useState(false); // 跟踪是否已经播放过首次动画
  
  // 队列筛选相关状态
  const [selectedQueues, setSelectedQueues] = useState([]); // 选中的队列列表，空数组表示全部队列
  const [availableQueues, setAvailableQueues] = useState([]); // 可用的队列列表

  // 核心统计数据
  const [coreStats, setCoreStats] = useState({
    totalQueues: 0,
    totalTasks: 0,
    runningTasks: 0,
    completedTasks: 0,
    failedTasks: 0,
    pendingTasks: 0,
    successRate: 0,
    throughput: 0,
    avgProcessingTime: 0,
  });

  // 系统健康状态（仅保留必要字段）
  const [systemHealth, setSystemHealth] = useState({
    redis: 'healthy',
    postgresql: 'healthy',
  });

  // Redis监控数据
  const [redisMonitor, setRedisMonitor] = useState({
    status: 'healthy',
    memory: {
      used_memory: 0,
      used_memory_human: '0B',
      usage_percentage: null,
      maxmemory: null,
      maxmemory_human: '0B',
      mem_fragmentation_ratio: 1.0
    },
    clients: {
      connected_clients: 0,
      blocked_clients: 0
    },
    stats: {
      instantaneous_ops_per_sec: 0,
      hit_rate: 0,
      keyspace_hits: 0,
      keyspace_misses: 0
    },
    keyspace: {
      total_keys: 0
    },
    server: {
      redis_version: 'unknown',
      uptime_in_seconds: 0
    }
  });
  const [redisLoading, setRedisLoading] = useState(false);

  // 任务并发数趋势（小图表）
  const [concurrencyData, setConcurrencyData] = useState([]);

  // 任务执行趋势（大图表）
  const [taskTrendData, setTaskTrendData] = useState([]);

  // 任务处理时间趋势
  const [processingTimeData, setProcessingTimeData] = useState([]);
  const [processingTimeLoading, setProcessingTimeLoading] = useState(false);

  // 排队任务数趋势
  const [queuedTasksData, setQueuedTasksData] = useState([]);

  // 创建任务延时趋势
  const [createLatencyData, setCreateLatencyData] = useState([]);


  // 队列积压Top10
  const [topBacklogQueues, setTopBacklogQueues] = useState([]);

  // 错误率Top10
  const [topErrorQueues, setTopErrorQueues] = useState([]);

  // 任务分布数据
  const [taskDistribution, setTaskDistribution] = useState([]);

  // fetchOverviewData 已移动到统一的 fetchData 函数中

  // 获取任务处理时间数据 - 已被 fetchOverviewData 统一替代
  // const fetchProcessingTimeData = useCallback(async () => {
  //   // 此函数已被 fetchOverviewData 替代，保留用于兼容性
  // }, [currentNamespace, timeRange]);

  // 生成模拟的处理时间数据（作为备用）
  const generateMockProcessingTimeData = useCallback(() => {
    const now = dayjs();
    const points = 20;
    const processingTime = [];

    for (let i = points - 1; i >= 0; i--) {
      const time = now.subtract(i * 2, 'minute');
      const timeStr = time.format('HH:mm');
      const baseTime = Math.random() * 1000 + 500;

      processingTime.push({
        time: timeStr,
        value: baseTime * 1.8,
        metric: 'P90处理时间',
      });
      processingTime.push({
        time: timeStr,
        value: baseTime,
        metric: 'P50处理时间',
      });
      processingTime.push({
        time: timeStr,
        value: baseTime * 1.2,
        metric: '平均处理时间',
      });
    }
    setProcessingTimeData(processingTime);
  }, []);
  // fetchRedisMonitor 已移动到统一的 fetchData 函数中

  // fetchSystemOverview 已移动到统一的 fetchData 函数中

  // fetchQueuedTasksData 已移动到统一的 fetchData 函数中

  // 获取任务趋势数据（大图表）- 已被 fetchOverviewData 统一替代  
  // const fetchTaskTrendData = useCallback(async () => {
  //   // 此函数已被 fetchOverviewData 替代，保留用于兼容性
  // }, [currentNamespace, timeRange]);

  // 获取任务并发数数据（小图表）- 已被 fetchOverviewData 统一替代
  // const fetchConcurrencyData = useCallback(async () => {
  //   // 此函数已被 fetchOverviewData 替代，保留用于兼容性
  // }, [currentNamespace, timeRange]);

  // 获取任务状态分布数据 - 已移动到fetchSystemOverview中，避免重复请求

  // 生成模拟的任务分布数据（作为备用）
  const generateMockTaskDistribution = useCallback(() => {
    const mockData = [
      { type: '队列1 (成功)', value: 45, queue: 'queue1', status: 'success' },
      { type: '队列1 (失败)', value: 5, queue: 'queue1', status: 'error' },
      { type: '队列2 (成功)', value: 30, queue: 'queue2', status: 'success' },
      { type: '队列3 (成功)', value: 20, queue: 'queue3', status: 'success' }
    ];
    setTaskDistribution(mockData);
  }, []);

  // 生成模拟的任务趋势数据（作为备用）
  const generateMockTaskTrendData = useCallback(() => {
    const now = dayjs();
    const points = 50; // 数据点数
    const taskTrend = [];
    for (let i = points - 1; i >= 0; i--) {
      const time = now.subtract(i * 2, 'minute');
      const timeStr = time.format('HH:mm');
      taskTrend.push({
        time: timeStr,
        value: Math.floor(Math.random() * 100) + 50,
        type: '创建',
      });
      taskTrend.push({
        time: timeStr,
        value: Math.floor(Math.random() * 90) + 45,
        type: '完成',
      });
      taskTrend.push({
        time: timeStr,
        value: Math.floor(Math.random() * 10) + 2,
        type: '失败',
      });
    }
    setTaskTrendData(taskTrend);
  }, []);

  // 生成模拟的并发数据（作为备用）
  const generateMockConcurrencyData = useCallback(() => {
    const now = dayjs();
    const points = 20;
    const concurrency = [];
    for (let i = points - 1; i >= 0; i--) {
      const time = now.subtract(i * 2, 'minute');
      concurrency.push({
        time: time.format('HH:mm'),
        value: Math.floor(Math.random() * 5) + 2,
        type: '并发数',
      });
    }
    setConcurrencyData(concurrency);
  }, []);

  // 获取任务创建延时数据 - 已被 fetchOverviewData 统一替代
  // const fetchCreateLatencyData = useCallback(async () => {
  //   // 此函数已被 fetchOverviewData 替代，保留用于兼容性
  // }, [currentNamespace, timeRange]);



  // 生成模拟的排队任务数数据（作为备用）
  const generateMockQueuedTasksData = useCallback(() => {
    const now = dayjs();
    const points = 20;
    const queued = [];
    for (let i = points - 1; i >= 0; i--) {
      const time = now.subtract(i * 2, 'minute');
      const timeStr = time.format('HH:mm');
      queued.push({
        time: timeStr,
        value: Math.floor(Math.random() * 10) + 5,
        type: '排队任务数',
      });
    }
    setQueuedTasksData(queued);
  }, []);

  // 生成模拟的创建延时数据（作为备用）
  const generateMockCreateLatencyData = useCallback(() => {
    const now = dayjs();
    const points = 20;
    const createLatency = [];
    for (let i = points - 1; i >= 0; i--) {
      const time = now.subtract(i * 2, 'minute');
      const timeStr = time.format('HH:mm');
      createLatency.push({
        time: timeStr,
        value: Math.floor(Math.random() * 100) + 50,
        type: '创建延时',
      });
    }
    setCreateLatencyData(createLatency);
  }, []);

  // 生成模拟系统状态数据
  const generateMockData = useCallback(() => {
    // 任务趋势数据现在通过fetchTaskTrendData获取，不在这里生成
    // 任务处理时间数据现在通过fetchProcessingTimeData获取，不在这里生成
    // 排队任务数和创建延时数据现在通过对应的API获取，不在这里生成

    // 系统健康状态（模拟PostgreSQL状态）
    setSystemHealth(prev => ({
      ...prev,
      postgresql: 'healthy'
    }));
  }, []);

  // 获取所有数据 - 统一在一个函数中避免重复请求
  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const namespace = currentNamespace || 'default';
      
      // 构建队列筛选参数（空数组表示全部队列）
      const queueParams = selectedQueues.length > 0 
        ? `&queues=${selectedQueues.join(',')}` 
        : '';
      
      console.log('🔄 开始获取Dashboard所有数据...');
      console.log('📊 当前命名空间:', currentNamespace);
      console.log('📊 使用的命名空间:', namespace);
      console.log('📊 选中的队列:', selectedQueues);
      console.log('📊 队列筛选参数:', queueParams);

      // 并行获取所有数据，避免重复请求
      const [
        dashboardStatsResponse,
        queuesResponse,
        backlogResponse,
        errorResponse,
        overviewResponse,
        queueBacklogResponse,
        redisResponse
      ] = await Promise.all([
        axios.get(`/api/data/dashboard-stats/${namespace}?time_range=${timeRange}${queueParams}`),
        axios.get(`/api/queues/${namespace}`),
        axios.get(`/api/data/top-backlog-queues/${namespace}?limit=10&time_range=${timeRange}${queueParams}`),
        axios.get(`/api/data/top-error-queues/${namespace}?limit=10&time_range=${timeRange}${queueParams}`),
        axios.post(`/api/data/dashboard-overview-stats/${namespace}`, { time_range: timeRange, queues: selectedQueues.length > 0 ? selectedQueues : undefined }),
        axios.get(`/api/data/queue-backlog-trend/${namespace}?time_range=${timeRange}${queueParams}`),
        axios.get(`/api/redis/monitor/${namespace}`)
      ]);

      console.log('✅ 所有API请求完成，开始处理数据...');

      // 处理队列列表数据（用于筛选器）
      console.log('📊 队列响应数据:', queuesResponse.data);
      if (queuesResponse.data) {
        // 检查返回数据的格式
        if (queuesResponse.data.success && Array.isArray(queuesResponse.data.data)) {
          // 格式: {success: true, data: ['queue1', 'queue2', ...]}
          const queueNames = queuesResponse.data.data;
          console.log('📊 可用队列列表 (format 1):', queueNames);
          setAvailableQueues(queueNames);
        } else if (Array.isArray(queuesResponse.data)) {
          // 格式: [{queue_name: 'queue1'}, {queue_name: 'queue2'}, ...]
          const queueNames = queuesResponse.data.map(queue => queue.queue_name || queue);
          console.log('📊 可用队列列表 (format 2):', queueNames);
          setAvailableQueues(queueNames);
        } else {
          console.warn('📊 队列数据格式异常:', queuesResponse.data);
        }
      }

      // 处理仪表板统计数据
      if (dashboardStatsResponse.data.success) {
        const stats = dashboardStatsResponse.data.data;
        setCoreStats({
          totalQueues: stats.total_queues,
          totalTasks: stats.total_tasks,
          runningTasks: stats.running_tasks,
          completedTasks: stats.completed_tasks,
          failedTasks: stats.failed_tasks,
          pendingTasks: stats.pending_tasks,
          successRate: stats.success_rate,
          throughput: stats.throughput,
          avgProcessingTime: stats.avg_processing_time,
        });
      }

      // 处理任务分布数据（现在从dashboardStatsResponse中获取，只按队列分组）
      if (dashboardStatsResponse.data.success && dashboardStatsResponse.data.data.task_distribution) {
        const distributionData = dashboardStatsResponse.data.data.task_distribution;
        const pieData = distributionData.map(item => ({
          type: item.type,  // 直接使用队列名
          value: item.value
        })).filter(item => item.value > 0);

        if (pieData.length === 0) {
          pieData.push({ type: '暂无数据', value: 1 });
        }
        setTaskDistribution(pieData);
      }

      // 处理排行榜数据
      if (backlogResponse.data.success) {
        setTopBacklogQueues(backlogResponse.data.data || []);
      }
      if (errorResponse.data.success) {
        setTopErrorQueues(errorResponse.data.data || []);
      }

      // 处理概览统计数据（任务趋势、并发等）
      if (overviewResponse.data) {
        const data = overviewResponse.data;
        const taskTrendData = data.task_trend || [];
        const concurrencyData = data.concurrency || [];
        const processingTimeData = data.processing_time || [];
        const creationLatencyData = data.creation_latency || [];

        if (taskTrendData.length > 0) {
          setTaskTrendData(taskTrendData);
        }
        if (concurrencyData.length > 0) {
          setConcurrencyData(concurrencyData);
        }
        if (processingTimeData.length > 0) {
          setProcessingTimeData(processingTimeData);
        }
        if (creationLatencyData.length > 0) {
          setCreateLatencyData(creationLatencyData);
        }
        if (data.granularity) {
          setGranularity(data.granularity);
        }
      }

      // 处理队列积压趋势数据
      if (queueBacklogResponse.data && queueBacklogResponse.data.data) {
        setQueuedTasksData(queueBacklogResponse.data.data);
      }

      // 处理Redis监控数据
      if (redisResponse.data.success) {
        const redisData = redisResponse.data.data;
        setRedisMonitor(redisData);
        setSystemHealth(prev => ({
          ...prev,
          redis: redisData.status
        }));
      }

      // 设置PostgreSQL状态（模拟）
      setSystemHealth(prev => ({
        ...prev,
        postgresql: 'healthy'
      }));

      console.log('🎉 Dashboard数据获取和处理完成');
      
    } catch (error) {
      console.error('❌ 获取Dashboard数据失败:', error);
      
      // 显示服务端返回的错误消息
      const errorMessage = error.response?.data?.detail || error.message || '获取概览数据失败';
      message.error(errorMessage);
      
      // 设置错误状态
      setSystemHealth(prev => ({
        ...prev,
        redis: 'error'
      }));
    } finally {
      setLoading(false);
      // 首次加载完成后，标记已经播放过动画
      if (!hasAnimated) {
        setTimeout(() => {
          setHasAnimated(true);
          // 移除强制重新渲染，避免图表闪烁
        }, 1500); // 等待动画播放完成后再标记
      } else {
        // 非首次加载时，更新key强制图表重新渲染（但无动画）
        setAnimationKey(prev => prev + 1);
      }
    }
  }, [currentNamespace, timeRange, selectedQueues, hasAnimated]);

  // 监听关键状态变化，统一触发数据获取
  useEffect(() => {
    console.log('🔄 关键状态变化触发数据获取');
    console.log('📊 currentNamespace:', currentNamespace);
    console.log('📊 timeRange:', timeRange);
    console.log('📊 selectedQueues:', selectedQueues);
    
    if (currentNamespace) {
      fetchData();
    }
  }, [currentNamespace, timeRange, selectedQueues, fetchData]);

  // 自动刷新逻辑（不包含初始化调用，避免与第一个useEffect重复）
  useEffect(() => {
    if (autoRefresh) {
      const timer = setInterval(fetchData, refreshInterval);
      return () => clearInterval(timer);
    }
  }, [autoRefresh, refreshInterval, fetchData]);

  // 创建一个动画key来强制图表重新渲染
  const [animationKey, setAnimationKey] = useState(0);
  
  // 根据是否应该播放动画返回配置
  const getAnimateConfig = (enterConfig) => {
    // 只在首次渲染且未播放过动画时启用动画
    if (hasAnimated) {
      return false; // 已经播放过动画，后续不再播放
    }
    return {
      enter: enterConfig,
      update: {
        type: 'morphing',
        duration: 500,
        easing: 'ease-in-out'
      }
    };
  };

  // 图表通用配置
  const commonChartConfig = {
    // 动画配置（仅首次加载时生效）
    animate: getAnimateConfig({
      type: 'fadeIn', 
      duration: 800,
      delay: 100,
      easing: 'ease-out'
    }),
    smooth: true,
    xField: (d) => new Date(d.time),
    height: 200,
    padding: 'auto',
    xAxis: {
      label: {
        autoRotate: false,
        autoHide: true,
      },
    },
    yAxis: {
      label: {
        formatter: (v) => {
          if (v >= 1000) return `${(v / 1000).toFixed(1)}k`;
          return v;
        },
      },
    },
    connectNulls: {
      connect: true,
      connectStroke: '#aaa',
    },
    axis: {
      x: {
        labelFormatter: (text) => {
          const date = dayjs(text);
          switch (granularity) {
            case 'second':
              return date.format('HH:mm:ss');
            case 'minute':
              return date.format('HH:mm');
            case 'hour':
              return date.format('MM-DD HH:mm');
            case 'day':
              return date.format('YYYY-MM-DD');
            default:
              return date.format('MM-DD HH:mm');
          }
        },
        labelAutoRotate: true,
      },
    },
    legend: {
      position: 'top',
      itemName: {
        style: {
          fontSize: 12,
        },
      },
    },
    style: {
      lineWidth: 2,
    },
    colorField: 'metric',  // 使用metric字段区分不同的线
    yField: 'value',
  };

  // 任务并发数配置（小图表）
  const miniConcurrencyConfig = {
    ...commonChartConfig,
    data: concurrencyData,
    yField: 'value',
    smooth: true,
    color: '#5B8FF9',
    // 面积图特定的动画效果（仅首次加载时生效）
    animate: getAnimateConfig({
      type: 'growInY', 
      duration: 1000,
      delay: 200,
      easing: 'ease-out'
    }),
    areaStyle: {
      fill: 'l(270) 0:#ffffff 0.5:#7ec8f7 1:#5B8FF9',
    },
    axis: {
      x: {
        labelFormatter: (text) => {
          const date = dayjs(text);
          switch (granularity) {
            case 'second':
              return date.format('HH:mm:ss');
            case 'minute':
              return date.format('HH:mm');
            case 'hour':
              return date.format('MM-DD HH:mm');
            case 'day':
              return date.format('YYYY-MM-DD');
            default:
              return date.format('MM-DD HH:mm');
          }
        },
        labelAutoRotate: true,
      },
    },
  };

  // 任务执行趋势配置（大图表）
  const taskTrendConfig = {
    ...commonChartConfig,
    data: taskTrendData,
    yField: 'value',
    colorField: 'metric',  // 使用metric字段区分不同的线
    // 线图特定的动画效果（仅首次加载时生效）
    animate: getAnimateConfig({
      type: 'pathIn', 
      duration: 1200,
      delay: 300,
      easing: 'ease-out'
    }),
    // 配置颜色映射
    scale: {
      color: {
        domain: ['入队速率', '完成速率', '失败数'],
        range: ['#1890ff', '#52c41a', '#ff4d4f'],  // 蓝色(入队)、绿色(完成)、红色(失败)
      },
      y: { nice: true },
    },
  };

  // 任务处理时间配置
  const processingTimeConfig = {
    ...commonChartConfig,
    data: processingTimeData,
    // 处理时间图表动画效果（仅首次加载时生效）
    animate: getAnimateConfig({
      type: 'waveIn', 
      duration: 1000,
      delay: 400,
      easing: 'ease-out'
    }),
    // 配置颜色映射
    scale: {
      color: {
        domain: ['P90处理时间', 'P50处理时间', '平均处理时间'],
        range: ['#1890ff', '#52c41a', '#ff4d4f'],  // 蓝色、绿色、红色
      },
      y: { nice: true },
    },
  };

  // 排队任务数配置
  const queuedTasksConfig = {
    ...commonChartConfig,
    data: queuedTasksData,
    yField: 'value',
    smooth: true,
    colorField: 'metric',  // 使用metric字段区分不同的线
    // 排队任务数动画效果（仅首次加载时生效）
    animate: getAnimateConfig({
      type: 'scaleInY', 
      duration: 900,
      delay: 500,
      easing: 'ease-out'
    }),
  };

  // 创建任务延时配置
  const createLatencyConfig = {
    ...commonChartConfig,
    data: createLatencyData,
    yField: 'value',
    // 延时图表动画效果（仅首次加载时生效）
    animate: getAnimateConfig({
      type: 'zoomIn', 
      duration: 800,
      delay: 600,
      easing: 'ease-out'
    }),
  };


  // 任务分布饼图配置（按照官方示例简化）
  const pieConfig = {
    data: taskDistribution,
    angleField: 'value',
    colorField: 'type',
    height: 210,
    // 饼图专属动画效果（仅首次加载时生效）
    animate: getAnimateConfig({
      type: 'waveIn', 
      duration: 1200,
      delay: 100,
      easing: 'ease-out'
    }),
    label: {
      text: 'value',
      style: {
        fontWeight: 'bold',
      },
    },
    tooltip: {
      title: 'type', // 标题
      items: ['value'], // 数据项
    }
  };

  return (
    <div style={{ padding: '16px', backgroundColor: '#f0f2f5', minHeight: '100vh' }}>
      {/* 页面标题和操作栏 */}
      <div style={{ marginBottom: 16, backgroundColor: 'white', padding: '16px', borderRadius: '4px' }}>
        <Row justify="space-between" align="middle">
          <Col>
            <Space>
              <DashboardOutlined style={{ fontSize: 20 }} />
              <span style={{ fontSize: 18, fontWeight: 500 }}>系统概览</span>
            </Space>
          </Col>
          <Col>
            <Space>
              <Select
                mode="multiple"
                placeholder={`全部队列 (${availableQueues.length}个可用)`}
                value={selectedQueues}
                onChange={setSelectedQueues}
                style={{ minWidth: 200 }}
                maxTagCount={1}
                maxTagPlaceholder={(omittedValues) => `+${omittedValues.length}个`}
                allowClear
                showSearch
                optionFilterProp="children"
                dropdownRender={menu => (
                  <div>
                    {availableQueues.length === 0 ? (
                      <div style={{ padding: '8px 12px', color: '#999' }}>
                        暂无队列数据
                      </div>
                    ) : menu}
                  </div>
                )}
              >
                {availableQueues.map(queue => (
                  <Option key={queue} value={queue}>{queue}</Option>
                ))}
              </Select>
              <Select value={timeRange} onChange={setTimeRange} style={{ width: 100 }}>
                {Object.entries(TIME_RANGES).map(([key, label]) => (
                  <Option key={key} value={key}>{label}</Option>
                ))}
              </Select>
              <Button
                icon={<ReloadOutlined />}
                onClick={fetchData}
                loading={loading}
              >
                刷新
              </Button>
            </Space>
          </Col>
        </Row>
      </div>

      {/* 第一行：核心指标卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col xs={24} sm={12} md={6}>
          <Card size="small" style={{ height: 100 }}>
            <Row style={{ height: '100%' }}>
              <Col span={12}>
                <Statistic
                  title="队列总数"
                  value={coreStats.totalQueues}
                  prefix={<DatabaseOutlined />}
                  valueStyle={{ color: '#1890ff' }}
                />
              </Col>
              <Col span={12}>
                <div style={{ padding: '8px 0', fontSize: 12, height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <div style={{ textAlign: 'center', color: '#666' }}>
                    系统队列总数
                  </div>
                </div>
              </Col>
            </Row>
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card size="small" style={{ height: 100 }}>
            <Row style={{ height: '100%' }}>
              <Col span={12}>
                <Statistic
                  title="任务总数"
                  value={coreStats.totalTasks}
                  prefix={<RocketOutlined />}
                  valueStyle={{ color: '#52c41a' }}
                />
              </Col>
              <Col span={12}>
                <div style={{ padding: '8px 0', fontSize: 12, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                  <div style={{ marginBottom: 4 }}>
                    已完成: <span style={{ color: '#52c41a', fontWeight: 'bold' }}>{coreStats.completedTasks}</span>
                  </div>
                  <div style={{ marginBottom: 4 }}>
                    处理中: <span style={{ color: '#1890ff', fontWeight: 'bold' }}>{coreStats.runningTasks}</span>
                  </div>
                  <div>
                    等待中: <span style={{ color: '#faad14', fontWeight: 'bold' }}>{coreStats.pendingTasks}</span>
                  </div>
                </div>
              </Col>
            </Row>
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card size="small" style={{ height: 100 }}>
            <Row style={{ height: '100%' }}>
              <Col span={12}>
                <Statistic
                  title="成功率"
                  value={coreStats.successRate}
                  suffix="%"
                  prefix={<CheckCircleOutlined />}
                  valueStyle={{ color: coreStats.successRate >= 95 ? '#52c41a' : '#faad14' }}
                />
              </Col>
              <Col span={12}>
                <div style={{ padding: '8px 0', fontSize: 12, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                  <div style={{ marginBottom: 4 }}>
                    失败: <span style={{ color: '#ff4d4f', fontWeight: 'bold' }}>{coreStats.failedTasks}</span>
                  </div>
                  <div>
                    错误率: <span style={{ color: '#ff4d4f', fontWeight: 'bold' }}>
                      {coreStats.totalTasks > 0 ? ((coreStats.failedTasks / coreStats.totalTasks) * 100).toFixed(1) : 0}%
                    </span>
                  </div>
                </div>
              </Col>
            </Row>
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card size="small" style={{ height: 100 }}>
            <Row style={{ height: '100%' }}>
              <Col span={12}>
                <Statistic
                  title={
                    <Space>
                      <span>吞吐量</span>
                      <Tooltip title="每分钟处理的任务数，基于最近几分钟内完成的任务计算">
                        <InfoCircleOutlined style={{ fontSize: 12, color: '#999' }} />
                      </Tooltip>
                    </Space>
                  }
                  value={coreStats.throughput}
                  suffix="/min"
                  prefix={<ThunderboltOutlined />}
                  valueStyle={{ color: '#722ed1' }}
                  precision={1}
                />
              </Col>
              <Col span={12}>
                <div style={{ padding: '8px 0', fontSize: 12, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                  <div style={{ marginBottom: 4 }}>
                    平均处理时间:
                  </div>
                  <div style={{ color: '#722ed1', fontWeight: 'bold', fontSize: 14 }}>
                    {coreStats.avgProcessingTime ? `${coreStats.avgProcessingTime}ms` : 'N/A'}
                  </div>
                </div>
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>

      {/* 第二行：图表展示 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col xs={24} md={12}>
          <Card
            size="small"
            title={
              <Space>
                <span>任务处理趋势</span>
                <Tooltip title="任务处理趋势">
                  <InfoCircleOutlined style={{ fontSize: 12, color: '#999' }} />
                </Tooltip>
              </Space>
            }
          >
            <Line
              key={`task-trend-${taskTrendData.length}-${animationKey}`}
              {...taskTrendConfig}
            />
          </Card>
        </Col>
        <Col xs={24} md={12}>
          <Card
            size="small"
            title={
              <Space>
                <PieChartOutlined style={{ color: '#1890ff' }} />
                <span>任务数量分布</span>
              </Space>
            }
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '205px' }}>
              <Pie
                key={`task-distribution-${taskDistribution.length}-${animationKey}`}
                {...pieConfig}
              />
            </div>
          </Card>
        </Col>
      </Row>

      {/* 第三行：并发监控 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col xs={24} md={12}>
          <Card
            size="small"
            title={
              <Space>
                <span>任务并发数量</span>
                <Tooltip title="任务并发数量">
                  <InfoCircleOutlined style={{ fontSize: 12, color: '#999' }} />
                </Tooltip>
              </Space>
            }
          >
            <Area {...miniConcurrencyConfig} height={200} />
          </Card>
        </Col>

        <Col xs={24} md={12}>
          <Card
            size="small"
            title={
              <Space>
                <span>任务处理时间</span>
                <Tooltip title="任务从开始到完成的时间">
                  <InfoCircleOutlined style={{ fontSize: 12, color: '#999' }} />
                </Tooltip>
                {processingTimeLoading && <SyncOutlined spin />}
              </Space>
            }
            extra={
              <Button
                size="small"
                icon={<ReloadOutlined />}
                onClick={fetchData}
                loading={processingTimeLoading}
              >
                刷新
              </Button>
            }
            bodyStyle={{ padding: '12px' }}
          >
            {processingTimeLoading ? (
              <div style={{
                height: '200px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <SyncOutlined spin style={{ fontSize: '24px', color: '#1890ff' }} />
              </div>
            ) : (
              <Line
                key={`processing-time-${processingTimeData.length}-${animationKey}`}
                {...processingTimeConfig}
              />
            )}
          </Card>
        </Col>

      </Row>

      {/* 第五行：性能指标图表 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>

        <Col xs={24} md={12}>
          <Card
            size="small"
            title={
              <Space>
                <span>排队任务数（个）</span>
                <Tooltip title="等待执行的任务数量">
                  <InfoCircleOutlined style={{ fontSize: 12, color: '#999' }} />
                </Tooltip>
              </Space>
            }
            bodyStyle={{ padding: '12px' }}
          >
            <Line
              key={`queued-tasks-${queuedTasksData.length}-${animationKey}`}
              {...queuedTasksConfig}
            />
          </Card>
        </Col>

        <Col xs={24} md={12}>
          <Card
            size="small"
            title={
              <Space>
                <span>任务执行延时</span>
                <Tooltip title="任务创建到开始执行的延时">
                  <InfoCircleOutlined style={{ fontSize: 12, color: '#999' }} />
                </Tooltip>
              </Space>
            }
            bodyStyle={{ padding: '12px' }}
          >
            <Line
              key={`create-latency-${createLatencyData.length}`}
              {...createLatencyConfig}
            />
          </Card>
        </Col>
      </Row>

      {/* 第七行：队列监控表格 */}
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card
            size="small"
            title="队列积压 Top 10"
            extra={
              <Tag color="orange">
                需要关注
              </Tag>
            }
          >
            <div style={{ height: 350, overflow: 'auto' }}>
              {topBacklogQueues.length > 0 ? (
                <Table
                  dataSource={topBacklogQueues}
                  columns={[
                    {
                      title: '队列名称',
                      dataIndex: 'queue',
                      key: 'queue',
                      ellipsis: true,
                    },
                    {
                      title: '积压数量',
                      dataIndex: 'backlog',
                      key: 'backlog',
                      render: (val) => (
                        <span style={{ fontWeight: 'bold' }}>
                          {val.toLocaleString()}
                        </span>
                      ),
                    },
                    {
                      title: '状态',
                      dataIndex: 'status',
                      key: 'status',
                      render: (status) => {
                        const colorMap = {
                          normal: 'green',
                          warning: 'orange',
                          critical: 'red',
                        };
                        const textMap = {
                          normal: '正常',
                          warning: '警告',
                          critical: '严重',
                        };
                        return <Tag color={colorMap[status]}>{textMap[status]}</Tag>;
                      },
                    },
                  ]}
                  pagination={false}
                  size="small"
                />
              ) : (
                <Empty description="暂无积压队列" />
              )}
            </div>
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card
            size="small"
            title="错误率 Top 10"
            extra={
              <Tag color="red">
                需要处理
              </Tag>
            }
          >
            <div style={{ height: 350, overflow: 'auto' }}>
              {topErrorQueues.length > 0 ? (
                <Table
                  dataSource={topErrorQueues}
                  columns={[
                    {
                      title: '队列名称',
                      dataIndex: 'queue',
                      key: 'queue',
                      ellipsis: true,
                    },
                    {
                      title: '错误率',
                      dataIndex: 'errorRate',
                      key: 'errorRate',
                      render: (val) => (
                        <Progress
                          percent={parseFloat(val)}
                          size="small"
                          strokeColor={val > 10 ? '#ff4d4f' : '#faad14'}
                        />
                      ),
                    },
                    {
                      title: '失败/总数',
                      key: 'ratio',
                      render: (_, record) => (
                        <span>{record.failed}/{record.total}</span>
                      ),
                    },
                  ]}
                  pagination={false}
                  size="small"
                />
              ) : (
                <Empty description="暂无错误" />
              )}
            </div>
          </Card>
        </Col>
      </Row>
      {/* 第四行：Redis监控详情 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col span={24}>
          <Card
            size="small"
            title={
              <Space>
                <DatabaseOutlined />
                <span>Redis监控</span>
                {redisLoading && <SyncOutlined spin />}
              </Space>
            }
            extra={
              <Button
                size="small"
                icon={<ReloadOutlined />}
                onClick={fetchData}
                loading={redisLoading}
              >
                刷新
              </Button>
            }
          >
            <Row gutter={[16, 16]}>
              {/* Redis基本信息 */}
              <Col xs={24} md={6}>
                <Card size="small" bodyStyle={{ padding: '12px' }}>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ marginBottom: 8, color: '#666', fontSize: 12 }}>版本信息</div>
                    <div style={{ fontSize: 14, fontWeight: 'bold' }}>{redisMonitor.server.redis_version}</div>
                    <div style={{ fontSize: 12, color: '#999', marginTop: 4 }}>
                      运行时长: {Math.floor(redisMonitor.server.uptime_in_seconds / 3600)}小时
                    </div>
                  </div>
                </Card>
              </Col>

              {/* 内存使用情况 */}
              <Col xs={24} md={6}>
                <Card size="small" bodyStyle={{ padding: '12px' }}>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ marginBottom: 8, color: '#666', fontSize: 12 }}>内存使用</div>
                    <Progress
                      type="dashboard"
                      percent={redisMonitor.memory.usage_percentage || 0}
                      size={60}
                      strokeColor={redisMonitor.memory.usage_percentage > 80 ? '#ff4d4f' : '#52c41a'}
                      format={(percent) => `${percent || 0}%`}
                    />
                    <div style={{ fontSize: 12, color: '#999', marginTop: 4 }}>
                      {redisMonitor.memory.used_memory_human} / {redisMonitor.memory.total_memory_human || redisMonitor.memory.maxmemory_human || '∞'}
                    </div>
                  </div>
                </Card>
              </Col>

              {/* 连接数统计 */}
              <Col xs={24} md={6}>
                <Card size="small" bodyStyle={{ padding: '12px' }}>
                  <div>
                    <div style={{ marginBottom: 8, color: '#666', fontSize: 12 }}>连接数</div>
                    <Row gutter={8}>
                      <Col span={12}>
                        <div style={{ textAlign: 'center' }}>
                          <div style={{ fontSize: 16, fontWeight: 'bold', color: '#1890ff' }}>
                            {redisMonitor.clients.connected_clients}
                          </div>
                          <div style={{ fontSize: 11, color: '#999' }}>连接数</div>
                        </div>
                      </Col>
                      <Col span={12}>
                        <div style={{ textAlign: 'center' }}>
                          <div style={{ fontSize: 16, fontWeight: 'bold', color: '#faad14' }}>
                            {redisMonitor.clients.blocked_clients}
                          </div>
                          <div style={{ fontSize: 11, color: '#999' }}>阻塞数</div>
                        </div>
                      </Col>
                    </Row>
                  </div>
                </Card>
              </Col>

              {/* 操作统计 */}
              <Col xs={24} md={6}>
                <Card size="small" bodyStyle={{ padding: '12px' }}>
                  <div>
                    <div style={{ marginBottom: 8, color: '#666', fontSize: 12 }}>操作统计</div>
                    <Row gutter={8}>
                      <Col span={24}>
                        <div style={{ textAlign: 'center', marginBottom: 8 }}>
                          <div style={{ fontSize: 16, fontWeight: 'bold', color: '#52c41a' }}>
                            {redisMonitor.stats.instantaneous_ops_per_sec}
                          </div>
                          <div style={{ fontSize: 11, color: '#999' }}>QPS</div>
                        </div>
                      </Col>
                      <Col span={12}>
                        <div style={{ textAlign: 'center' }}>
                          <div style={{ fontSize: 14, fontWeight: 'bold', color: '#722ed1' }}>
                            {redisMonitor.stats.hit_rate}%
                          </div>
                          <div style={{ fontSize: 11, color: '#999' }}>命中率</div>
                        </div>
                      </Col>
                      <Col span={12}>
                        <div style={{ textAlign: 'center' }}>
                          <div style={{ fontSize: 14, fontWeight: 'bold', color: '#eb2f96' }}>
                            {redisMonitor.keyspace.total_keys}
                          </div>
                          <div style={{ fontSize: 11, color: '#999' }}>Key数</div>
                        </div>
                      </Col>
                    </Row>
                  </div>
                </Card>
              </Col>
            </Row>

            {/* Redis状态详情 */}
            <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
              <Col xs={24} lg={8}>
                <div style={{ padding: '8px 0', borderTop: '1px solid #f0f0f0' }}>
                  <div style={{ marginBottom: 8, fontSize: 13, fontWeight: 'bold', color: '#666' }}>内存详情</div>
                  <Space direction="vertical" size={4} style={{ width: '100%' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12 }}>
                      <span>已使用:</span>
                      <span>{redisMonitor.memory.used_memory_human}</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12 }}>
                      <span>碎片率:</span>
                      <span>{redisMonitor.memory.mem_fragmentation_ratio}</span>
                    </div>
                  </Space>
                </div>
              </Col>
              <Col xs={24} lg={8}>
                <div style={{ padding: '8px 0', borderTop: '1px solid #f0f0f0' }}>
                  <div style={{ marginBottom: 8, fontSize: 13, fontWeight: 'bold', color: '#666' }}>命中统计</div>
                  <Space direction="vertical" size={4} style={{ width: '100%' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12 }}>
                      <span>命中:</span>
                      <span style={{ color: '#52c41a' }}>{redisMonitor.stats.keyspace_hits?.toLocaleString() || 0}</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12 }}>
                      <span>未命中:</span>
                      <span style={{ color: '#ff4d4f' }}>{redisMonitor.stats.keyspace_misses?.toLocaleString() || 0}</span>
                    </div>
                  </Space>
                </div>
              </Col>
              <Col xs={24} lg={8}>
                <div style={{ padding: '8px 0', borderTop: '1px solid #f0f0f0' }}>
                  <div style={{ marginBottom: 8, fontSize: 13, fontWeight: 'bold', color: '#666' }}>状态信息</div>
                  <Space direction="vertical" size={4} style={{ width: '100%' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12 }}>
                      <span>状态:</span>
                      <Tag color={redisMonitor.status === 'healthy' ? 'green' : 'red'} size="small">
                        {redisMonitor.status === 'healthy' ? '健康' : '异常'}
                      </Tag>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12 }}>
                      <span>命名空间:</span>
                      <span>{currentNamespace || 'default'}</span>
                    </div>
                  </Space>
                </div>
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>

      {/* 第六行：队列积压监控 */}
      {/* <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col span={24}>
          <QueueBacklogTrend
            showTitle={true}
            defaultTimeRange={timeRange}
            autoRefresh={autoRefresh}
            refreshInterval={refreshInterval}
            showStatistics={true}
            chartType="line"
            height={300}
            selectedQueues={null}
          />
        </Col>
      </Row> */}


    </div>
  );
}

export default Dashboard;