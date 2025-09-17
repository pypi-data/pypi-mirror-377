import { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { Card, Space, Button, Tag, message, Breadcrumb, Spin, Input, Empty, Select, Tooltip, Row, Col, Modal, Radio } from 'antd';
import { QuestionCircleOutlined, ShareAltOutlined, CopyOutlined, ClearOutlined, FileTextOutlined, CheckCircleOutlined, ExclamationCircleOutlined, LineChartOutlined, AreaChartOutlined, EyeOutlined } from '@ant-design/icons';
import ProTable from '@ant-design/pro-table';
import { Line } from '@ant-design/plots';
import { G2 } from "@ant-design/plots";
import TimeRangeSelector from '../components/TimeRangeSelector';
import TaskFilter from '../components/TaskFilter';
import QueueBacklogTrend from '../components/QueueBacklogTrend';
import { getQueueFilters, saveQueueFilters, clearQueueFilters } from '../utils/userPreferences';
import { useNamespace } from '../contexts/NamespaceContext';
import { useLoading } from '../contexts/LoadingContext';
import dayjs from 'dayjs';
import axios from 'axios';

const { Search } = Input;

// 任务状态配置
const STATUS_CONFIG = {
  'pending': { color: 'gold', label: '待处理' },
  'running': { color: 'blue', label: '运行中' },
  'success': { color: 'green', label: '成功' },
  'error': { color: 'red', label: '失败' },
  'rejected': { color: 'purple', label: '拒绝' },
};

function QueueDetail() {
  const { queueName } = useParams();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const { currentNamespace } = useNamespace();
  const { setLoading: setGlobalLoading } = useLoading();
  const decodedQueueName = decodeURIComponent(queueName);

  // 初始化状态：优先使用localStorage记忆，其次使用URL参数
  const getInitialState = () => {
    // 先尝试从localStorage获取记忆的设置
    const savedSettings = getQueueFilters(decodedQueueName);

    // 检查URL参数
    const urlFilters = searchParams.get('filters');
    const urlTimeRange = searchParams.get('timeRange');
    const urlCustomStart = searchParams.get('startTime');
    const urlCustomEnd = searchParams.get('endTime');
    const scheduledTaskId = searchParams.get('scheduled_task_id');

    // 如果有scheduled_task_id参数，创建对应的筛选条件
    let initialFilters = [];
    if (scheduledTaskId) {
      initialFilters = [{
        field: 'scheduled_task_id',
        operator: 'eq',
        value: parseInt(scheduledTaskId)
      }];
    } else if (urlFilters) {
      try {
        initialFilters = JSON.parse(decodeURIComponent(urlFilters));
      } catch (e) {
        console.error('Failed to parse filters from URL:', e);
      }
    } else {
      initialFilters = savedSettings.filters;
    }

    // 如果有URL参数，优先使用URL参数（分享链接场景）
    if (urlFilters || urlTimeRange || (urlCustomStart && urlCustomEnd) || scheduledTaskId) {
      let initialTimeRange = urlTimeRange || savedSettings.timeRange || '1h';
      let initialCustomTimeRange = null;

      if (urlCustomStart && urlCustomEnd) {
        initialCustomTimeRange = [dayjs(urlCustomStart), dayjs(urlCustomEnd)];
        initialTimeRange = 'custom';
      }

      return { initialFilters, initialTimeRange, initialCustomTimeRange };
    }

    // 否则使用localStorage中的记忆设置
    let initialCustomTimeRange = null;
    if (savedSettings.customTimeRange && savedSettings.customTimeRange.length === 2) {
      initialCustomTimeRange = [
        dayjs(savedSettings.customTimeRange[0]),
        dayjs(savedSettings.customTimeRange[1])
      ];
    }

    return {
      initialFilters: savedSettings.filters,
      initialTimeRange: savedSettings.timeRange,
      initialCustomTimeRange
    };
  };

  const { initialFilters, initialTimeRange, initialCustomTimeRange } = getInitialState();

  const [loading, setLoading] = useState(false);
  const [timeRange, setTimeRange] = useState(initialTimeRange);
  const [customTimeRange, setCustomTimeRange] = useState(initialCustomTimeRange);
  const [chartData, setChartData] = useState([]);
  const [granularity, setGranularity] = useState('');
  const [refreshing, setRefreshing] = useState(false);
  const [tableKey, setTableKey] = useState(0); // 用于强制刷新表格
  const [chartType, setChartType] = useState('flowRate'); // 'flowRate' | 'backlog'

  // 用于防抖的 ref
  const fetchTimeoutRef = useRef(null);
  const isBrushingRef = useRef(false);

  // 筛选条件状态
  const [filterState, setFilterState] = useState({
    status: null,
    taskId: '',
    workerId: '',
  });
  const [filters, setFilters] = useState(initialFilters);

  // 任务详细数据相关状态
  const [taskDetailsCache, setTaskDetailsCache] = useState({});
  const [loadingTaskDetails, setLoadingTaskDetails] = useState({});
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [selectedTaskDetail, setSelectedTaskDetail] = useState(null);
  const [selectedTaskId, setSelectedTaskId] = useState(null);

  // 计算表格高度的hooks
  const [tableHeight, setTableHeight] = useState(400);
  const actionRef = useRef();

  useEffect(() => {
    const updateTableHeight = () => {
      // 视窗高度 - 面包屑(约50px) - 图表卡片(约350px) - 页边距(约50px) - ProTable工具栏和分页(约150px)
      const availableHeight = window.innerHeight - 540;
      const minHeight = 300; // 最小高度
      const calculatedHeight = Math.max(availableHeight, minHeight);
      setTableHeight(calculatedHeight);
    };

    // 初始计算
    updateTableHeight();

    // 监听窗口大小变化
    window.addEventListener('resize', updateTableHeight);
    return () => window.removeEventListener('resize', updateTableHeight);
  }, []);

  // 获取队列流量速率数据
  const fetchQueueTimeline = useCallback(async () => {
    if (!decodedQueueName || !currentNamespace) {
      return;
    }

    setLoading(true);
    try {
      // 构建筛选条件（合并旧的搜索参数和新的筛选条件）
      const combinedFilters = [...filters];

      // 添加旧的搜索参数作为筛选条件（为了兼容性）
      if (filterState.status) {
        combinedFilters.push({ field: 'status', operator: 'eq', value: filterState.status });
      }
      if (filterState.taskId) {
        combinedFilters.push({ field: 'id', operator: 'contains', value: filterState.taskId });
      }
      if (filterState.workerId) {
        combinedFilters.push({ field: 'worker_id', operator: 'contains', value: filterState.workerId });
      }

      const params = {
        namespace: currentNamespace || 'default',  // 添加命名空间
        queues: [decodedQueueName],
        time_range: timeRange,
        filters: combinedFilters,  // 传递筛选条件
      };

      if (customTimeRange && customTimeRange.length === 2) {
        params.start_time = customTimeRange[0].toISOString();
        params.end_time = customTimeRange[1].toISOString();
      }

      // 使用支持命名空间的新接口
      const namespace = currentNamespace || 'default';
      const response = await axios.post(`/api/data/queue-flow-rates/${namespace}`, params);
      const { data, granularity: dataGranularity } = response.data;


      // 打印前几个数据点来调试
      if (data && data.length > 0) {
        // 检查数据一致性
        const metrics = [...new Set(data.map(d => d.metric))];

        // 按metric分组统计
        const metricCounts = {};
        metrics.forEach(metric => {
          metricCounts[metric] = data.filter(d => d.metric === metric).length;
        });
      }

      setChartData(data || []);
      setGranularity(dataGranularity || 'minute');
    } catch (error) {
      console.error('Failed to fetch queue timeline:', error);
      
      // 显示服务端返回的错误消息
      const errorMessage = error.response?.data?.detail || error.message || '获取队列趋势数据失败';
      message.error(errorMessage);
    } finally {
      setLoading(false);
      isBrushingRef.current = false;
    }
  }, [decodedQueueName, timeRange, customTimeRange, filters, filterState]);

  // ProTable的请求函数
  const request = async (params, sort, filter) => {
    setRefreshing(true);
    try {
      // 构建筛选条件（向后兼容旧的搜索参数）
      const combinedFilters = [...filters];

      // 添加旧的搜索参数作为筛选条件
      if (filterState.status) {
        combinedFilters.push({ field: 'status', operator: 'eq', value: filterState.status });
      }
      if (filterState.taskId) {
        combinedFilters.push({ field: 'id', operator: 'contains', value: filterState.taskId });
      }
      if (filterState.workerId) {
        combinedFilters.push({ field: 'worker_id', operator: 'contains', value: filterState.workerId });
      }

      // 构建请求参数，包含时间范围
      const requestParams = {
        namespace: currentNamespace || 'default',  // 添加命名空间
        queue_name: decodedQueueName,
        page: params.current,
        page_size: params.pageSize,
        filters: combinedFilters,
        time_range: timeRange,  // 传递时间范围
      };

      // 如果有自定义时间范围，使用它
      if (customTimeRange && customTimeRange.length === 2) {
        requestParams.start_time = customTimeRange[0].toISOString();
        requestParams.end_time = customTimeRange[1].toISOString();
      }

      // 处理排序
      if (sort) {
        const sortField = Object.keys(sort)[0];
        if (sortField) {
          requestParams.sort_field = sortField;
          requestParams.sort_order = sort[sortField] === 'ascend' ? 'asc' : 'desc';
        }
      }

      // 使用支持命名空间的新接口
      const namespace = requestParams.namespace || 'default';
      const response = await axios.post(`/api/data/tasks/${namespace}`, requestParams);

      if (response.data.success) {
        // 确保即使是空数据也能正确更新
        const responseData = response.data.data || [];
        console.log(`任务列表请求返回 ${responseData.length} 条数据`);
        return {
          data: responseData,
          success: true,
          total: response.data.total || 0,
        };
      }
      console.log('任务列表请求失败');
      return {
        data: [],
        success: true,  // 改为true，确保ProTable接受空数据
        total: 0,
      };
    } catch (error) {
      console.error('Failed to fetch tasks:', error);
      
      // 显示服务端返回的错误消息
      const errorMessage = error.response?.data?.detail || error.message || '获取任务列表失败';
      message.error(errorMessage);
      
      return {
        data: [],
        success: true,  // 即使出错也返回true，让ProTable清空数据
        total: 0,
      };
    } finally {
      setRefreshing(false);
    }
  };

  // 初始化加载
  // 合并的初始化和命名空间切换处理
  useEffect(() => {
    if (decodedQueueName && currentNamespace) {
      // 根据当前视图类型决定刷新哪些数据
      // if (chartType === 'flow') {
        fetchQueueTimeline();
      // }
      // chartType === 'backlog' 时，QueueBacklogTrend组件会自己处理刷新

      // 刷新表格
      if (actionRef.current) {
        actionRef.current.reload();
      }
    }
  }, [decodedQueueName, currentNamespace]);

  // 时间范围变化时重新加载（添加防抖）
  useEffect(() => {
    if (decodedQueueName) {
      // 清除之前的定时器
      if (fetchTimeoutRef.current) {
        clearTimeout(fetchTimeoutRef.current);
      }

      // 如果是刷选触发的自定义时间范围，延迟一点获取数据
      const delay = isBrushingRef.current ? 300 : 0;

      fetchTimeoutRef.current = setTimeout(() => {
        // 根据当前视图类型决定刷新哪些数据
        if (chartType === 'flow') {
          fetchQueueTimeline();
        }
        // chartType === 'backlog' 时，QueueBacklogTrend组件会自己处理刷新

        // 刷新ProTable
        if (actionRef.current) {
          actionRef.current.reload();
        }
      }, delay);
    }

    // 清理函数
    return () => {
      if (fetchTimeoutRef.current) {
        clearTimeout(fetchTimeoutRef.current);
      }
    };
  }, [timeRange, customTimeRange, chartType]);

  // 更新URL参数的函数
  const updateURLParams = useCallback(() => {
    const params = new URLSearchParams();

    // 保存筛选条件
    if (filters && filters.length > 0) {
      params.set('filters', encodeURIComponent(JSON.stringify(filters)));
    }

    // 保存时间范围
    if (timeRange !== '1h') {
      params.set('timeRange', timeRange);
    }

    // 保存自定义时间范围
    if (customTimeRange && customTimeRange.length === 2) {
      params.set('startTime', customTimeRange[0].toISOString());
      params.set('endTime', customTimeRange[1].toISOString());
    }

    // 更新URL但不触发导航
    setSearchParams(params, { replace: true });
  }, [filters, timeRange, customTimeRange, setSearchParams]);

  // 生成分享链接
  const generateShareLink = () => {
    const currentURL = new URL(window.location.href);
    const params = new URLSearchParams();

    // 添加筛选条件
    if (filters && filters.length > 0) {
      params.set('filters', encodeURIComponent(JSON.stringify(filters)));
    }

    // 添加时间范围
    if (timeRange !== '1h') {
      params.set('timeRange', timeRange);
    }

    // 添加自定义时间范围
    if (customTimeRange && customTimeRange.length === 2) {
      params.set('startTime', customTimeRange[0].toISOString());
      params.set('endTime', customTimeRange[1].toISOString());
    }

    currentURL.search = params.toString();
    return currentURL.toString();
  };

  // 复制分享链接
  const handleCopyShareLink = () => {
    const shareLink = generateShareLink();
    navigator.clipboard.writeText(shareLink).then(() => {
      message.success('分享链接已复制到剪贴板');
    }).catch(() => {
      message.error('复制失败，请手动复制');
      Modal.info({
        title: '分享链接',
        content: shareLink,
        okText: '关闭',
      });
    });
  };

  // 分享筛选条件（ProTable用）
  const shareFilters = () => {
    handleCopyShareLink();
  };

  // 保存筛选条件（ProTable用）
  const handleSaveFilters = () => {
    const settings = {
      filters,
      timeRange,
      customTimeRange: customTimeRange ? customTimeRange.map(t => t.toISOString()) : null,
    };
    saveQueueFilters(decodedQueueName, settings);
    message.success('筛选条件已保存');
  };

  // 清除筛选条件（ProTable用）
  const handleClearFilters = () => {
    setFilters([]);
    setTimeRange('1h');
    setCustomTimeRange(null);
    clearQueueFilters(decodedQueueName);
    if (actionRef.current) {
      actionRef.current.reload();
    }
    message.success('筛选条件已清除');
  };

  // 筛选条件或时间范围变化时更新URL和保存到localStorage
  useEffect(() => {
    updateURLParams();

    // 保存到localStorage（用于记忆）
    if (decodedQueueName) {
      // 准备要保存的自定义时间范围
      let customTimeRangeToSave = null;
      if (customTimeRange && customTimeRange.length === 2) {
        customTimeRangeToSave = [
          customTimeRange[0].toISOString(),
          customTimeRange[1].toISOString()
        ];
      }

      saveQueueFilters(decodedQueueName, {
        filters,
        timeRange,
        customTimeRange: customTimeRangeToSave
      });
    }
  }, [filters, timeRange, customTimeRange, updateURLParams, decodedQueueName]);

  // 搜索参数或筛选条件变化时重新加载
  useEffect(() => {
    if (decodedQueueName) {
      if (actionRef.current) {
        actionRef.current.reload();
      }
      // 根据当前视图类型决定是否刷新图表
      if (chartType === 'flow') {
        fetchQueueTimeline();
      }
    }
  }, [filterState, filters, chartType]);


  // 处理刷新
  const handleRefresh = () => {
    // 根据当前视图类型决定刷新哪些数据
    if (chartType === 'flow') {
      fetchQueueTimeline();
    }
    // chartType === 'backlog' 时，QueueBacklogTrend组件会自己处理刷新

    if (actionRef.current) {
      actionRef.current.reload();
    }
  };

  // 清除当前队列的记忆设置
  const handleClearMemory = () => {
    Modal.confirm({
      title: '清除筛选记忆',
      content: `确定要清除队列 "${decodedQueueName}" 的所有筛选记忆吗？这将重置所有筛选条件和时间范围。`,
      okText: '确定',
      cancelText: '取消',
      onOk: () => {
        clearQueueFilters(decodedQueueName);
        // 重置为默认值
        setFilters([]);
        setTimeRange('1h');
        setCustomTimeRange(null);
        message.success('筛选记忆已清除');
        // 刷新数据
        fetchQueueTimeline();
        if (actionRef.current) {
          actionRef.current.reload();
        }
      }
    });
  };


  // 获取单个任务的详细数据
  const fetchTaskDetails = async (taskId, consumerGroup) => {
    // 使用taskId和consumerGroup作为缓存键
    const cacheKey = consumerGroup ? `${taskId}_${consumerGroup}` : taskId;

    // 如果已经在缓存中，直接使用
    if (taskDetailsCache[cacheKey]) {
      return taskDetailsCache[cacheKey];
    }

    // 如果正在加载，避免重复请求
    if (loadingTaskDetails[cacheKey]) {
      return;
    }

    setLoadingTaskDetails(prev => ({ ...prev, [cacheKey]: true }));

    try {
      // 构建URL，如果有consumerGroup则添加为查询参数
      const url = consumerGroup
        ? `/api/task/${taskId}/details?consumer_group=${encodeURIComponent(consumerGroup)}`
        : `/api/task/${taskId}/details`;
      const response = await axios.get(url);

      if (response.data.success) {
        const details = response.data.data;
        setTaskDetailsCache(prev => ({ ...prev, [cacheKey]: details }));
        return details;
      }
    } catch (error) {
      message.error('获取任务详细数据失败');
      console.error('Failed to fetch task details:', error);
    } finally {
      setLoadingTaskDetails(prev => ({ ...prev, [cacheKey]: false }));
    }
  };

  // 处理查看任务详情
  const handleViewTaskDetail = async (taskId, field, consumerGroup) => {
    const details = await fetchTaskDetails(taskId, consumerGroup);
    if (details) {
      setSelectedTaskId(taskId);
      let data;
      if (field === 'task_data') {
        data = details.task_data;
      } else if (field === 'result') {
        data = details.result;
      } else if (field === 'error_message') {
        data = details.error_message;
      }
      setSelectedTaskDetail({
        field: field,
        data: data,
        consumerGroup: consumerGroup
      });
      setDetailModalVisible(true);
    }
  };

  // 图表配置 - 显示三条流量速率线
  const chartConfig = {
    data: chartData,
    xField: (d) => new Date(d.time),
    yField: 'value',
    colorField: 'metric',  // 使用metric字段区分不同的线
    smooth: true,
    animate: false,
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
      y: {
        title: '任务数量',
        titleFontSize: 14,
      },
    },
    // 配置颜色映射
    scale: {
      color: {
        domain: ['入队速率', '完成速率', '失败数'],
        range: ['#1890ff', '#52c41a', '#ff4d4f'],  // 蓝色(入队)、绿色(完成)、红色(失败)
      },
      y: { nice: true },
    },
    legend: {
      position: 'top',
      itemName: {
        style: {
          fontSize: 12,
        },
      },
    },
    tooltip: {
      title: (title) => {
        const date = dayjs(title.time);
        switch (granularity) {
          case 'second':
            return date.format('YYYY-MM-DD HH:mm:ss');
          case 'minute':
            return date.format('YYYY-MM-DD HH:mm');
          case 'hour':
            return date.format('YYYY-MM-DD HH:mm');
          case 'day':
            return date.format('YYYY-MM-DD');
          default:
            return date.format('YYYY-MM-DD HH:mm');
        }
      },
      items: [
        {
          field: 'value',
          name: (datum) => datum.metric,
          valueFormatter: (value) => {
            return `${value} 个`;
          },
        },
      ],
    },
    style: {
      lineWidth: 2,
    },
    // point: {
    //   size: 3,
    //   shape: 'circle',
    // },
    height: 240,
    interaction: {
      brushXFilter: true // 启用横向筛选
    },
    // 监听brush事件，实现框选后自动请求数据
    onReady: (plot) => {

      // 获取图表实例
      const chart = plot.chart;

      chart.on("brush:filter", (e) => {
        console.log('Brush filter 事件:', e);

        // 获取刷选的数据范围
        if (e.data && e.data.selection) {
          const selection = e.data.selection;
          console.log('Selection 数据:', selection);

          // selection[0] 是选中的时间数组
          if (selection && selection[0] && selection[0].length > 0) {
            const selectedTimes = selection[0];

            // 获取选中时间的起止
            const startTime = dayjs(selectedTimes[0]);
            const endTime = dayjs(selectedTimes[selectedTimes.length - 1]);

            console.log('刷选范围:', startTime.format(), endTime.format());

            // 设置刷选标志
            isBrushingRef.current = true;

            // 更新UI状态，这会触发 useEffect 重新获取数据
            setTimeRange('custom');
            setCustomTimeRange([startTime, endTime]);
          }
        }
      });
    },
  };

  // 生成GCS日志系统的链接
  const generateGCSLogLink = (taskId, task) => {
    // 如果task_name是unknown，只筛选task_id
    const query = task.task_name && task.task_name !== 'unknown' 
      ? `jsonPayload.event_id%3D%22${taskId}%22%20and%20jsonPayload.task_name%3D%22${task.task_name}%22`
      : `jsonPayload.event_id%3D%22${taskId}%22`;
    const baseUrl = 'https://console.cloud.google.com/logs/query';
    const storageScope = 'logScope,projects%2Ftap-testing-env%2Flocations%2Fglobal%2FlogScopes%2Fall-project-log';
    const currentTime = new Date().toISOString();
    
    // 检查任务是否为最终状态
    const finalStates = ['success', 'error', 'cancel'];
    const isTaskCompleted = finalStates.includes(task.status);
    
    if (isTaskCompleted) {
      // 任务已完成，使用精确的时间范围
      let startTime, endTime;
      
      if (task.created_at) {
        // 任务创建时间前5分钟
        const createdAt = new Date(task.created_at);
        startTime = new Date(createdAt.getTime() - 5 * 60 * 1000).toISOString();
      } else {
        // 如果没有创建时间，使用当前时间前1小时
        startTime = new Date(Date.now() - 60 * 60 * 1000).toISOString();
      }
      
      if (task.completed_at) {
        // 任务完成时间后5分钟
        const completedAt = new Date(task.completed_at);
        endTime = new Date(completedAt.getTime() + 5 * 60 * 1000).toISOString();
      } else if (task.started_at) {
        // 如果没有完成时间但有开始时间，使用开始时间后30分钟（假设任务最多运行30分钟）
        const startedAt = new Date(task.started_at);
        endTime = new Date(startedAt.getTime() + 30 * 60 * 1000).toISOString();
      } else {
        // 如果都没有，使用当前时间
        endTime = currentTime;
      }
      
      return `${baseUrl};query=${query};storageScope=${storageScope};cursorTimestamp=${currentTime};startTime=${startTime};endTime=${endTime}?project=tap-testing-env`;
    } else {
      // 任务未完成，使用最近一天的日志
      return `${baseUrl};query=${query};storageScope=${storageScope};cursorTimestamp=${currentTime};duration=P1D?project=tap-testing-env`;
    }
  };

  // 处理查看日志
  const handleViewLogs = (taskId, task) => {
    const logUrl = generateGCSLogLink(taskId, task);
    window.open(logUrl, '_blank');
  };

  // ProTable列定义
  const columns = [
    {
      title: '任务ID',
      dataIndex: 'id',
      key: 'id',
      width: 120,
      fixed: 'left',
      ellipsis: true,
      copyable: true,
      search: false,
      render: (text) => <span style={{ fontFamily: 'monospace', fontSize: '12px' }}>{text}</span>,
    },
    {
      title: '任务名称',
      dataIndex: 'task_name',
      key: 'task_name',
      width: 150,
      ellipsis: true,
      copyable: true,
      search: false,
    },
    // {
    //   title: '消费者组',
    //   dataIndex: 'consumer_group',
    //   key: 'consumer_group',
    //   width: 180,
    //   ellipsis: true,
    //   copyable: true,
    //   search: false,
    //   render: (text) => text || '-',
    // },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      valueType: 'select',
      valueEnum: {
        pending: { text: '待处理', status: 'Warning' },
        running: { text: '运行中', status: 'Processing' },
        success: { text: '成功', status: 'Success' },
        error: { text: '失败', status: 'Error' },
        rejected: { text: '拒绝', status: 'Default' },
      },
      render: (status) => {
        const config = STATUS_CONFIG[status] || { color: 'default', label: status };
        return <Tag color={config.color}>{config.label}</Tag>;
      },
      search: false,
    },
    // {
    //   title: '优先级',
    //   dataIndex: 'priority',
    //   key: 'priority',
    //   width: 80,
    //   render: (priority) => priority ?? '-',
    // },
    // {
    //   title: '重试次数',
    //   dataIndex: 'retry_count',
    //   key: 'retry_count',
    //   width: 100,
    //   render: (count, record) => `${count || 0}/${record.max_retry || 0}`,
    // },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 160,
      sorter: true,
      search: false,
      render: (_, record) => {
        const text = record.created_at;
        if (!text) return '-';
        const date = dayjs(text);
        return date.isValid() ? date.format('YYYY-MM-DD HH:mm:ss') : '-';
      },
    },
    {
      title: '开始时间',
      dataIndex: 'started_at',
      key: 'started_at',
      width: 160,
      search: false,
      render: (_, record) => {
        const text = record.started_at;
        if (!text) return '-';
        const date = dayjs(text);
        return date.isValid() ? date.format('YYYY-MM-DD HH:mm:ss') : '-';
      },
    },
    {
      title: '完成时间',
      dataIndex: 'completed_at',
      key: 'completed_at',
      width: 160,
      search: false,
      render: (_, record) => {
        const text = record.completed_at;
        if (!text) return '-';
        const date = dayjs(text);
        return date.isValid() ? date.format('YYYY-MM-DD HH:mm:ss') : '-';
      },
    },
    {
      title: '耗时',
      key: 'duration',
      width: 75,
      search: false,
      render: (_, record) => {
        const text = record.duration;
        if (text === null || text === undefined) return '-';
        if (typeof text === 'number') {
          return `${text.toFixed(2)}s`;
        }
        const num = parseFloat(text);
        return !isNaN(num) ? `${num.toFixed(2)}s` : '-';
      },
    },
    {
      title: '执行时间',
      dataIndex: 'execution_time',
      key: 'execution_time',
      width: 100,
      align: 'right',
      search: false,
      render: (text) => {
        if (text === null || text === undefined) return '-';
        if (typeof text === 'number') {
          return `${text.toFixed(5)}s`;
        }
        const num = parseFloat(text);
        return !isNaN(num) ? `${num.toFixed(3)}s` : '-';
      },
    },
    {
      title: 'Worker',
      dataIndex: 'worker_id',
      key: 'worker_id',
      width: 200,
      ellipsis: true,
      search: false,
    },
    {
      title: '操作',
      key: 'actions',
      width: 150,
      align: 'center',
      fixed: 'right',
      search: false,
      render: (_, record) => (
        <Space size="small">
          <Tooltip title="查看任务参数">
            <Button
              type="link"
              size="small"
              icon={<FileTextOutlined />}
              loading={loadingTaskDetails[`${record.id}_${record.consumer_group || 'none'}`]}
              onClick={() => handleViewTaskDetail(record.id, 'task_data', record.consumer_group)}
            />
          </Tooltip>
          <Tooltip title="查看执行结果">
            <Button
              type="link"
              size="small"
              icon={<CheckCircleOutlined />}
              loading={loadingTaskDetails[`${record.id}_${record.consumer_group || 'none'}`]}
              onClick={() => handleViewTaskDetail(record.id, 'result', record.consumer_group)}
              style={{ color: '#52c41a' }}
            />
          </Tooltip>
          <Tooltip title={record.status === 'error' ? "查看错误信息" : "无错误信息"}>
            <Button
              type="link"
              size="small"
              icon={<ExclamationCircleOutlined />}
              loading={loadingTaskDetails[`${record.id}_${record.consumer_group || 'none'}`]}
              onClick={() => handleViewTaskDetail(record.id, 'error_message', record.consumer_group)}
              disabled={record.status !== 'error'}
              danger={record.status === 'error'}
            />
          </Tooltip>
          <Tooltip title="查看GCS日志">
            <Button
              type="link"
              size="small"
              icon={<EyeOutlined />}
              onClick={() => handleViewLogs(record.id, record)}
              style={{ color: '#1890ff' }}
            />
          </Tooltip>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: '0px', height: '94.5vh', overflow: 'hidden' }}>
      {/* 面包屑导航 */}
      {/* <Breadcrumb
        style={{ marginBottom: 16 }}
        items={[
          {
            title: <a onClick={() => navigate('/queues')}>队列管理</a>
          },
          {
            title: decodedQueueName
          }
        ]}
      /> */}
      {/* 趋势图 */}
      {/* 任务列表 */}
      <Card
        style={{ marginBottom: 0 }}
      >
        <div style={{ height: 240 }}>
          <Spin spinning={loading}>
            {chartData.length > 0 ? (
              <Line {...chartConfig} />
            ) : (
              <Empty description="暂无数据" />
            )}
          </Spin>
        </div>



        <ProTable
          key={tableKey}
          columns={columns}
          actionRef={actionRef}
          request={request}
          rowKey={(record) => `${record.id}_${record.consumer_group || 'none'}`}
          pagination={{
            showQuickJumper: true,
            showSizeChanger: true,
            defaultPageSize: 20,
          }}
          search={false}
          dateFormatter="string"
          headerTitle="任务列表"
          scroll={{
            y: tableHeight,
            x: 1300,
          }}
          size="small"
          options={{
            reload: async () => {
              try {
                console.log('刷新数据...');
                setRefreshing(true);
                setGlobalLoading(true, '刷新数据中...');

                // 先刷新图表
                await fetchQueueTimeline();

                // 然后通过修改key强制刷新表格
                // 不要调用action?.reload()，避免循环
                setTableKey(prev => prev + 1);

                // 给一点时间让表格重新渲染
                await new Promise(resolve => setTimeout(resolve, 100));

              } catch (error) {
                console.error('刷新失败:', error);
                message.error('刷新数据失败');
              } finally {
                setRefreshing(false);
                setGlobalLoading(false);
              }
            },
            density: true,
            fullScreen: true,
            setting: true,
          }}
          loading={refreshing}
          toolbar={{
            title: (
              <Space>
                <TaskFilter
                  filters={filters}
                  onFiltersChange={(newFilters) => {
                    setFilters(newFilters);
                    if (actionRef.current) {
                      actionRef.current.reload();
                    }
                  }}
                />
              </Space>
            ),
            actions: [
              <TimeRangeSelector
                value={timeRange}
                onChange={setTimeRange}
                customValue={customTimeRange}
                onCustomChange={setCustomTimeRange}
              />,
              <Tooltip key="share" title="分享当前筛选条件">
                <Button icon={<ShareAltOutlined />} onClick={shareFilters}>
                  分享
                </Button>
              </Tooltip>,
              // <Tooltip key="clear" title="清除所有筛选条件">
              //   <Button icon={<ClearOutlined />} onClick={handleClearFilters}>
              //     清除
              //   </Button>
              // </Tooltip>,
            ],
          }}
          params={{
            timeRange,
            customTimeRange,
            filters,
          }}
        />
      </Card>


      {/* JSON数据展示弹窗 */}
      <Modal
        title={`${selectedTaskDetail?.field === 'task_data' ? '任务参数' :
          selectedTaskDetail?.field === 'result' ? '执行结果' :
            selectedTaskDetail?.field === 'error_message' ? '错误信息' : ''
          } - ${selectedTaskId}`}
        open={detailModalVisible}
        onCancel={() => {
          setDetailModalVisible(false);
          setSelectedTaskDetail(null);
          setSelectedTaskId(null);
        }}
        width={800}
        footer={null}
      >
        <div style={{ maxHeight: '60vh', overflowY: 'auto' }}>
          {selectedTaskDetail?.field === 'error_message' ? (
            // 错误信息直接显示为文本
            <div style={{
              backgroundColor: '#fff2f0',
              padding: '16px',
              borderRadius: '4px',
              border: '1px solid #ffccc7',
              color: '#cf1322',
              fontSize: '13px',
              lineHeight: '1.5',
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word'
            }}>
              {selectedTaskDetail?.data || '无错误信息'}
            </div>
          ) : (
            // JSON数据格式化显示
            <pre style={{
              backgroundColor: '#f5f5f5',
              padding: '16px',
              borderRadius: '4px',
              fontSize: '12px',
              lineHeight: '1.5',
              overflowX: 'auto'
            }}>
              {selectedTaskDetail?.data ?
                JSON.stringify(selectedTaskDetail.data, null, 2) :
                '无数据'
              }
            </pre>
          )}
        </div>
      </Modal>
    </div >
  );
}

export default QueueDetail;