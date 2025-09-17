import { useState, useEffect, forwardRef, useImperativeHandle, useRef } from 'react';
import { Tag, message, Button, Space, Progress, Tooltip } from 'antd';
import { ProTable } from '@ant-design/pro-components';
import { 
  TeamOutlined, 
  ThunderboltOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  SyncOutlined,
  EyeOutlined,
  ExpandOutlined,
  CompressOutlined,
  UserOutlined,
  CopyOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import dayjs from 'dayjs';
import { useNamespace } from '../contexts/NamespaceContext';
import './QueueDetailsTable.css';

const QueueDetailsTableV2 = forwardRef(({ 
  autoRefresh = false, 
  refreshInterval = 5000,
  selectedQueues = [],
  timeRange = '15m',
  customTimeRange = null
}, ref) => {
  const navigate = useNavigate();
  const { currentNamespace } = useNamespace();
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState([]);
  const [expandedRowKeys, setExpandedRowKeys] = useState([]);
  const actionRef = useRef();

  // 暴露刷新方法给父组件
  useImperativeHandle(ref, () => ({
    refresh: fetchQueueStats
  }));

  // 复制文本到剪贴板
  const handleCopy = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      message.success('已复制到剪贴板');
    } catch (err) {
      message.error('复制失败');
    }
  };

  // 获取队列统计信息（使用新的v2 API）
  const fetchQueueStats = async () => {
    if (!currentNamespace) {
      return;
    }
    
    setLoading(true);
    try {
      // 构建查询参数
      const params = new URLSearchParams();
      
      // 添加时间范围参数
      if (customTimeRange && customTimeRange.length === 2) {
        // 自定义时间范围
        // customTimeRange可能是dayjs对象或ISO字符串
        const startTime = dayjs.isDayjs(customTimeRange[0]) 
          ? customTimeRange[0].toISOString() 
          : customTimeRange[0];
        const endTime = dayjs.isDayjs(customTimeRange[1]) 
          ? customTimeRange[1].toISOString() 
          : customTimeRange[1];
        params.append('start_time', startTime);
        params.append('end_time', endTime);
      } else if (timeRange && timeRange !== 'custom') {
        // 预设时间范围
        params.append('time_range', timeRange);
      }
      
      const url = `/api/v2/namespaces/${currentNamespace}/queues/stats${params.toString() ? '?' + params.toString() : ''}`;
      console.log('Fetching queue stats with URL:', url);
      
      const response = await axios.get(url);
      if (response.data.success) {
        // 过滤选中的队列
        let queuesData = response.data.data;
        if (selectedQueues && selectedQueues.length > 0) {
          queuesData = queuesData.filter(q => selectedQueues.includes(q.queue_name));
        }
        setData(queuesData);
      } else {
        message.error('获取队列详情失败');
      }
    } catch (error) {
      console.error('Failed to fetch queue stats:', error);
      message.error('获取队列详情失败');
    } finally {
      setLoading(false);
    }
  };

  // 初始化加载数据
  useEffect(() => {
    if (selectedQueues && selectedQueues.length > 0) {
      fetchQueueStats();
    } else {
      setData([]);
    }
  }, [currentNamespace, selectedQueues, timeRange, customTimeRange]);

  // 自动刷新
  useEffect(() => {
    if (autoRefresh) {
      const timer = setInterval(() => {
        fetchQueueStats();
      }, refreshInterval);
      return () => clearInterval(timer);
    }
  }, [autoRefresh, refreshInterval]);

  // 消费者组表格列定义
  const consumerGroupColumns = [
    // {
    //   title: '消费者组',
    //   dataIndex: 'group_name',
    //   key: 'group_name',
    //   width: 220,
    //   ellipsis: {
    //     showTitle: false, // 不使用默认的 title，我们自定义
    //   },
    //   render: (_, record) => {
    //     // 直接从 record 获取原始数据
    //     const text = record.group_name || '';
    //     // 提取最后一部分（冒号分隔的最后一段）
    //     const lastPart = text.split(':').pop() || text;
    //     return (
    //       <div style={{ display: 'flex', alignItems: 'center', width: '100%' }}>
    //         <Tooltip title={text}>
    //           <span 
    //             style={{ 
    //               cursor: 'pointer',
    //               overflow: 'hidden',
    //               textOverflow: 'ellipsis',
    //               whiteSpace: 'nowrap',
    //               flex: 1,
    //               minWidth: 0
    //             }} 
    //             onClick={() => handleCopy(text)}
    //           >
    //             {lastPart}
    //           </span>
    //         </Tooltip>
    //         <Tooltip title="点击复制完整名称">
    //           <Button
    //             type="text"
    //             size="small"
    //             icon={<CopyOutlined />}
    //             onClick={() => handleCopy(text)}
    //             style={{ padding: '0 4px', flexShrink: 0 }}
    //           />
    //         </Tooltip>
    //       </div>
    //     );
    //   },
    // },
    {
      title: '任务名',
      dataIndex: 'task_name',
      key: 'task_name',
      width: 180,
      ellipsis: true,
      copyable: true,
    },
    {
      title: '优先级',
      dataIndex: 'priority',
      key: 'priority',
      width: 80,
      align: 'center',
      render: (priority) => {
        let color;
        if (priority === 0) {
          color = 'default';
        } else if (priority <= 3) {
          color = 'red';
        } else if (priority <= 6) {
          color = 'orange';
        } else {
          color = 'green';
        }
        
        return (
          <Tag color={color} style={{ fontSize: '12px', fontWeight: 'bold' }}>
            {priority}
          </Tag>
        );
      }
    },
    {
      title: '待处理',
      dataIndex: 'pending',
      key: 'pending',
      width: 100,
      align: 'center',
      render: (pending) => (
        <span>{pending ? pending : 0}</span>
        // <Badge count={pending} style={{ backgroundColor: pending > 0 ? '#fa8c16' : '#d9d9d9' }} overflowCount={9999} />
      )
    },
    {
      title: '可见/不可见',
      key: 'messages',
      width: 140,
      align: 'center',
      render: (_, record) => (
        <Space>
          <span style={{ color: '#1890ff' }}>{record.visible_messages}</span>
          <span>/</span>
          <span style={{ color: '#8c8c8c' }}>{record.invisible_messages}</span>
        </Space>
      )
    },
    {
      title: '成功/失败',
      key: 'stats',
      width: 120,
      align: 'center',
      render: (_, record) => (
        <Space>
          <span style={{ color: '#52c41a' }}>{record.success_count}</span>
          <span>/</span>
          <span style={{ color: '#ff4d4f' }}>{record.failed_count}</span>
        </Space>
      )
    },
    {
      title: '成功率',
      dataIndex: 'success_rate',
      key: 'success_rate',
      width: 120,
      align: 'center',
      render: (rate) => (
        <Progress 
          percent={rate} 
          size="small" 
          strokeColor={rate >= 95 ? '#52c41a' : rate >= 80 ? '#faad14' : '#ff4d4f'}
        />
      )
    },
    {
      title: '处理速率',
      dataIndex: 'processing_rate',
      key: 'processing_rate',
      width: 100,
      align: 'center',
      render: (rate) => (
        <span>
          <ThunderboltOutlined style={{ color: '#faad14' }} /> {rate}/min
        </span>
      )
    },
    {
      title: '平均耗时',
      dataIndex: 'avg_execution_time',
      key: 'avg_execution_time',
      width: 100,
      align: 'center',
      render: (time) => (
        <span>{time ? `${time.toFixed(2)}s` : '-'}</span>
      )
    }
  ];

  // 主表格列定义
  const columns = [
    {
      title: '队列名',
      dataIndex: 'queue_name',
      key: 'queue_name',
      width: 200,
      fixed: 'left',
      ellipsis: true,
      copyable: true,
      render: (text) => (
        <span style={{ fontWeight: 'bold' }}>{text}</span>
      )
    },
    {
      title: '消费者组数',
      dataIndex: 'consumer_groups_count',
      key: 'consumer_groups_count',
      width: 120,
      align: 'center',
      render: (count, record) => (
        <Space>
          <TeamOutlined />
          <span>{count}</span>
          {count > 0 && (
            <Button
              type="link"
              size="small"
              onClick={() => {
                if (expandedRowKeys.includes(record.queue_name)) {
                  setExpandedRowKeys(expandedRowKeys.filter(key => key !== record.queue_name));
                } else {
                  setExpandedRowKeys([...expandedRowKeys, record.queue_name]);
                }
              }}
            >
              {expandedRowKeys.includes(record.queue_name) ? '收起' : '展开'}
            </Button>
          )}
        </Space>
      )
    },
    {
      title: '队列总长度',
      dataIndex: 'total_length',
      key: 'total_length',
      width: 120,
      align: 'center',
      render: (length) => (
        <span>{length ? length : 0}</span>
        // <Badge 
        //   count={length} 
        //   style={{ 
        //     backgroundColor: length > 1000 ? '#ff4d4f' : length > 100 ? '#fa8c16' : '#52c41a' 
        //   }} 
        //   overflowCount={999999}
        // />
      )
    },
    {
      title: '在线Workers',
      dataIndex: 'active_workers',
      key: 'active_workers',
      width: 120,
      align: 'center',
      render: (workers) => (
        <Space>
          <UserOutlined style={{ color: workers > 0 ? '#52c41a' : '#d9d9d9' }} />
          <span style={{ color: workers > 0 ? '#52c41a' : '#d9d9d9' }}>{workers}</span>
        </Space>
      )
    },
    {
      title: '成功/失败',
      key: 'success_failed',
      width: 150,
      align: 'center',
      render: (_, record) => (
        <Space>
          <span style={{ color: '#52c41a' }}>{record.total_success}</span>
          <span>/</span>
          <span style={{ color: '#ff4d4f' }}>{record.total_failed}</span>
        </Space>
      )
    },
    {
      title: '总体成功率',
      dataIndex: 'overall_success_rate',
      key: 'overall_success_rate',
      width: 120,
      align: 'center',
      render: (rate) => (
        <Progress 
          percent={rate} 
          size="small" 
          strokeColor={rate >= 95 ? '#52c41a' : rate >= 80 ? '#faad14' : '#ff4d4f'}
        />
      )
    },
    {
      title: '操作',
      key: 'action',
      width: 100,
      fixed: 'right',
      align: 'center',
      render: (_, record) => (
        <Button
          type="link"
          icon={<EyeOutlined />}
          onClick={() => {
            navigate(`/queue/${record.queue_name}`);
          }}
        >
          查看
        </Button>
      )
    }
  ];

  // 展开行渲染
  const expandedRowRender = (record) => {
    return (
      <ProTable
        columns={consumerGroupColumns}
        dataSource={record.consumer_groups}
        rowKey="unique_key"
        pagination={false}
        search={false}
        options={false}
        size="small"
        toolBarRender={false}
      />
    );
  };

  return (
    <div className="queue-details-table-v2">
      <ProTable
        columns={columns}
        dataSource={data}
        rowKey="queue_name"
        loading={loading}
        pagination={false}
        search={false}
        dateFormatter="string"
        headerTitle="队列概览"
        actionRef={actionRef}
        expandable={{
          expandedRowRender,
          expandedRowKeys,
          onExpandedRowsChange: setExpandedRowKeys,
        }}
        options={{
          reload: () => fetchQueueStats(),
          density: true,
          fullScreen: true,
          setting: true,
        }}
        toolBarRender={() => [
          expandedRowKeys.length === data.filter(d => d.consumer_groups_count > 0).length ? (
            <Button
              key="collapse"
              icon={<CompressOutlined />}
              onClick={() => setExpandedRowKeys([])}
            >
              收起全部
            </Button>
          ) : (
            <Button
              key="expand"
              icon={<ExpandOutlined />}
              onClick={() => {
                const keys = data.filter(d => d.consumer_groups_count > 0).map(d => d.queue_name);
                setExpandedRowKeys(keys);
              }}
            >
              展开全部
            </Button>
          ),
          // <Button
          //   key="refresh"
          //   icon={<SyncOutlined spin={loading} />}
          //   onClick={fetchQueueStats}
          // >
          //   刷新
          // </Button>
        ]}
      />
    </div>
  );
});

export default QueueDetailsTableV2;