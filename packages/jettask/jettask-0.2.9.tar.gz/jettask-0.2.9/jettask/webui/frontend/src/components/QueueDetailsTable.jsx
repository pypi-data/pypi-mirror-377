import { useState, useEffect, forwardRef, useImperativeHandle } from 'react';
import { Table, Tag, Tooltip, message, Button, Space, Popconfirm, Modal, InputNumber } from 'antd';
import { InfoCircleOutlined, ScissorOutlined, DeleteOutlined, EyeOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import dayjs from 'dayjs';
import { getPreference, setPreference, PREFERENCE_KEYS } from '../utils/userPreferences';
import { useNamespace } from '../contexts/NamespaceContext';
import './QueueDetailsTable.css';

const QueueDetailsTable = forwardRef(({ 
  autoRefresh = false, 
  refreshInterval = 5000,
  timeRange: parentTimeRange,
  customTimeRange,
  selectedQueues = []
}, ref) => {
  const navigate = useNavigate();
  const { currentNamespace } = useNamespace();
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState([]);
  const [trimModalVisible, setTrimModalVisible] = useState(false);
  const [trimQueue, setTrimQueue] = useState(null);
  const [trimCount, setTrimCount] = useState(100);
  
  // 从本地存储恢复分页大小
  const [pageSize, setPageSize] = useState(
    getPreference(PREFERENCE_KEYS.QUEUE_DETAILS_PAGE_SIZE, 10)
  );
  
  // 计算实际的时间范围（分钟）
  const calculateTimeRangeMinutes = () => {
    if (customTimeRange && customTimeRange.length === 2) {
      // 自定义时间范围，计算分钟差
      const start = dayjs(customTimeRange[0]);
      const end = dayjs(customTimeRange[1]);
      const diffMinutes = Math.ceil(end.diff(start, 'minute'));
      return Math.max(1, diffMinutes); // 至少1分钟
    }
    
    // 预设时间范围
    const timeRangeMap = {
      '15m': 15,
      '30m': 30,
      '1h': 60,
      '3h': 180,
      '6h': 360,
      '12h': 720,
      '24h': 1440,
      '7d': 10080,
      '30d': 43200,
    };
    
    return timeRangeMap[parentTimeRange] || 15; // 默认15分钟
  };
  
  const timeRangeMinutes = calculateTimeRangeMinutes();

  // 暴露刷新方法给父组件
  useImperativeHandle(ref, () => ({
    refresh: fetchQueueDetails
  }));

  // 获取队列详细信息
  const fetchQueueDetails = async () => {
    if (!currentNamespace) {
      return;
    }
    
    setLoading(true);
    try {
      // 构建与queue-timeline相同格式的请求参数
      const params = {
        namespace: currentNamespace,
        time_range: parentTimeRange || '15m',  // 添加默认值
        queues: selectedQueues  // 传递选中的队列
      };

      // 如果有自定义时间范围
      if (customTimeRange && customTimeRange.length === 2) {
        params.start_time = customTimeRange[0].toISOString();
        params.end_time = customTimeRange[1].toISOString();
      }

      console.log('[QueueDetailsTable] 请求参数:', params, 'parentTimeRange:', parentTimeRange);

      const response = await axios.post(`/api/data/queue-details/${currentNamespace}`, params);
      if (response.data.success) {
        setData(response.data.data);
      } else {
        message.error('获取队列详情失败');
      }
    } catch (error) {
      console.error('Failed to fetch queue details:', error);
      message.error('获取队列详情失败');
    } finally {
      setLoading(false);
    }
  };

  // 初始化加载数据
  useEffect(() => {
    // 只有当有选中的队列时才加载数据
    if (selectedQueues && selectedQueues.length > 0) {
      fetchQueueDetails();
    } else {
      setData([]);  // 没有选中队列时清空数据
    }
  }, [parentTimeRange, customTimeRange, selectedQueues]); // 当时间范围或选中队列变化时重新加载

  // 自动刷新
  useEffect(() => {
    if (autoRefresh) {
      const timer = setInterval(() => {
        fetchQueueDetails();
      }, refreshInterval);

      return () => clearInterval(timer);
    }
  }, [autoRefresh, refreshInterval]);

  // 格式化消费速度
  const formatConsumptionRate = (rate) => {
    if (rate === null || rate === undefined) return '-';
    if (rate === 0) return '0 任务/分钟';
    if (rate < 1) return `${(rate * 60).toFixed(1)} 任务/小时`;
    return `${rate.toFixed(1)} 任务/分钟`;
  };
  
  // 处理分页变化
  const handleTableChange = (pagination) => {
    if (pagination.pageSize !== pageSize) {
      setPageSize(pagination.pageSize);
      // 保存到本地存储
      setPreference(PREFERENCE_KEYS.QUEUE_DETAILS_PAGE_SIZE, pagination.pageSize);
    }
  };

  // 处理删除队列
  const handleDeleteQueue = async (queueName) => {
    try {
      const response = await axios.delete(`/api/queue/${queueName}`);
      if (response.data.success) {
        message.success(`队列 ${queueName} 已删除`);
        fetchQueueDetails(); // 刷新数据
      } else {
        message.error(response.data.message || '删除失败');
      }
    } catch (error) {
      console.error('Failed to delete queue:', error);
      message.error('删除队列失败');
    }
  };

  // 处理裁剪队列
  const handleTrimQueue = async () => {
    if (!trimQueue || !trimCount) return;
    
    try {
      const response = await axios.post(`/api/queue/${trimQueue}/trim`, { 
        max_length: trimCount 
      });
      if (response.data.success) {
        message.success(`队列 ${trimQueue} 已裁剪至 ${trimCount} 条消息`);
        setTrimModalVisible(false);
        fetchQueueDetails(); // 刷新数据
      } else {
        message.error(response.data.message || '裁剪失败');
      }
    } catch (error) {
      console.error('Failed to trim queue:', error);
      message.error('裁剪队列失败');
    }
  };

  // 查看队列详情
  const handleViewDetails = (queueName) => {
    navigate(`/queue/${encodeURIComponent(queueName)}`);
  };

  // 显示裁剪模态框
  const showTrimModal = (queueName) => {
    setTrimQueue(queueName);
    setTrimModalVisible(true);
  };

  // 表格列定义
  const columns = [
    {
      title: '队列名称',
      dataIndex: 'queue_name',
      key: 'queue_name',
      fixed: 'left',
      width: 150,
      render: (text) => <strong>{text}</strong>,
    },
    {
      title: '消息数量',
      dataIndex: 'message_count',
      key: 'message_count',
      width: 100,
      align: 'right',
      sorter: (a, b) => a.message_count - b.message_count,
      render: (value) => value?.toLocaleString() || '0',
    },
    {
      title: '可见消息',
      dataIndex: 'visible_messages',
      key: 'visible_messages',
      width: 100,
      align: 'right',
      sorter: (a, b) => a.visible_messages - b.visible_messages,
      render: (value) => {
        if (value > 0) {
          return <Tag color="orange">{value.toLocaleString()}</Tag>;
        }
        return <span style={{ color: '#999' }}>0</span>;
      },
    },
    {
      title: '不可见消息',
      dataIndex: 'invisible_messages',
      key: 'invisible_messages',
      width: 120,
      align: 'right',
      sorter: (a, b) => a.invisible_messages - b.invisible_messages,
      // render: (value) => {
      //   if (value > 0) {
      //     return <Tag color="blue">{value.toLocaleString()}</Tag>;
      //   }
      //   return <span style={{ color: '#999' }}>0</span>;
      // },
    },
    {
      title: '成功',
      dataIndex: 'completed',
      key: 'completed',
      width: 100,
      align: 'right',
      sorter: (a, b) => a.completed - b.completed,
      render: (value) => {
        if (value > 0) {
          return <Tag color="green">{value.toLocaleString()}</Tag>;
        }
        return <span style={{ color: '#999' }}>0</span>;
      },
    },
    {
      title: '失败',
      dataIndex: 'failed',
      key: 'failed',
      width: 100,
      align: 'right',
      sorter: (a, b) => a.failed - b.failed,
      render: (value) => {
        if (value > 0) {
          return <Tag color="red">{value.toLocaleString()}</Tag>;
        }
        return <span style={{ color: '#999' }}>0</span>;
      },
    },
    {
      title: (
        <Tooltip title={`基于最近${timeRangeMinutes}分钟的平均处理速度`}>
          <span>
            消费速度 <InfoCircleOutlined />
          </span>
        </Tooltip>
      ),
      dataIndex: 'consumption_rate',
      key: 'consumption_rate',
      width: 150,
      align: 'right',
      sorter: (a, b) => (a.consumption_rate || 0) - (b.consumption_rate || 0),
      render: (value) => {
        const formatted = formatConsumptionRate(value);
        if (value > 10) {
          return <span style={{ color: '#52c41a', fontWeight: 'bold' }}>{formatted}</span>;
        } else if (value > 0) {
          return <span style={{ color: '#1890ff' }}>{formatted}</span>;
        }
        return <span style={{ color: '#999' }}>{formatted}</span>;
      },
    },
    {
      title: '在线Workers',
      dataIndex: 'active_workers',
      key: 'active_workers',
      width: 120,
      align: 'center',
      sorter: (a, b) => a.active_workers - b.active_workers,
      render: (value) => {
        if (value > 0) {
          return (
            <Tag color="green">
              <span style={{ fontSize: '14px' }}>👥 {value}</span>
            </Tag>
          );
        }
        return <Tag color="default">无</Tag>;
      },
    },
    {
      title: (
        <Tooltip title={`基于最近${timeRangeMinutes}分钟的成功率`}>
          <span>
            成功率 <InfoCircleOutlined />
          </span>
        </Tooltip>
      ),
      dataIndex: 'success_rate',
      key: 'success_rate',
      width: 100,
      align: 'center',
      sorter: (a, b) => (a.success_rate || 0) - (b.success_rate || 0),
      render: (value) => {
        if (!value && value !== 0) return <span style={{ color: '#999' }}>-</span>;
        
        let color = '#52c41a';
        if (value < 50) color = '#ff4d4f';
        else if (value < 90) color = '#faad14';
        
        return (
          <span style={{ color, fontWeight: 'bold' }}>
            {value.toFixed(1)}%
          </span>
        );
      },
    },
    {
      title: '队列状态',
      dataIndex: 'queue_status',
      key: 'queue_status',
      width: 100,
      align: 'center',
      render: (value) => {
        const statusConfig = {
          'active': { color: 'green', label: '活跃' },
          'idle': { color: 'blue', label: '空闲' },
          'unknown': { color: 'default', label: '未知' }
        };
        const config = statusConfig[value] || statusConfig['unknown'];
        return <Tag color={config.color}>{config.label}</Tag>;
      },
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      align: 'center',
      fixed: 'right',
      render: (_, record) => (
        <Space size="small">
          <Tooltip title="查看详情">
            <Button
              type="link"
              size="small"
              icon={<EyeOutlined />}
              onClick={() => handleViewDetails(record.queue_name)}
            />
          </Tooltip>
          <Tooltip title="裁剪消息">
            <Button
              type="link"
              size="small"
              icon={<ScissorOutlined />}
              onClick={() => showTrimModal(record.queue_name)}
              disabled={record.message_count === 0}
            />
          </Tooltip>
          <Popconfirm
            title="确定要删除这个队列吗？"
            description="此操作不可恢复"
            onConfirm={() => handleDeleteQueue(record.queue_name)}
            okText="确定"
            cancelText="取消"
          >
            <Tooltip title="删除队列">
              <Button
                type="link"
                size="small"
                danger
                icon={<DeleteOutlined />}
              />
            </Tooltip>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <>
      <div className="compact-table">
        <Table
        columns={columns}
        dataSource={data}
        rowKey="queue_name"
        loading={loading}
        onChange={handleTableChange}
        pagination={{
          pageSize: pageSize,
          pageSizeOptions: ['5', '6', '7', '8', '10', '20', '50', '100'],
          showTotal: (total) => `共 ${total} 个队列`,
          showSizeChanger: true,
          showQuickJumper: true,
        }}
        scroll={{ x: 1300 }}
        size="small"
        summary={(pageData) => {
          const totals = pageData.reduce(
            (acc, row) => ({
              message_count: acc.message_count + (row.message_count || 0),
              visible: acc.visible + (row.visible_messages || 0),
              invisible: acc.invisible + (row.invisible_messages || 0),
              completed: acc.completed + (row.completed || 0),
              failed: acc.failed + (row.failed || 0),
              workers: acc.workers + (row.active_workers || 0),
            }),
            { message_count: 0, visible: 0, invisible: 0, completed: 0, failed: 0, workers: 0 }
          );

          return (
            <Table.Summary.Row style={{ background: '#fafafa', fontWeight: 'bold' }}>
              <Table.Summary.Cell index={0}>总计</Table.Summary.Cell>
              <Table.Summary.Cell index={1} align="right">
                {totals.message_count.toLocaleString()}
              </Table.Summary.Cell>
              <Table.Summary.Cell index={2} align="right">
                {totals.visible.toLocaleString()}
              </Table.Summary.Cell>
              <Table.Summary.Cell index={3} align="right">
                {totals.invisible.toLocaleString()}
              </Table.Summary.Cell>
              <Table.Summary.Cell index={4} align="right">
                {totals.completed.toLocaleString()}
              </Table.Summary.Cell>
              <Table.Summary.Cell index={5} align="right">
                {totals.failed.toLocaleString()}
              </Table.Summary.Cell>
              <Table.Summary.Cell index={6} align="right">-</Table.Summary.Cell>
              <Table.Summary.Cell index={7} align="center">
                {totals.workers}
              </Table.Summary.Cell>
              <Table.Summary.Cell index={8} align="center">
                {(totals.completed + totals.failed) > 0 
                  ? `${((totals.completed / (totals.completed + totals.failed)) * 100).toFixed(1)}%`
                  : '-'}
              </Table.Summary.Cell>
              <Table.Summary.Cell index={9} align="center">-</Table.Summary.Cell>
            </Table.Summary.Row>
          );
        }}
        rowHoverable	
        />
      </div>
      
      {/* 裁剪队列模态框 */}
      <Modal
        title={`裁剪队列: ${trimQueue}`}
        open={trimModalVisible}
        onOk={handleTrimQueue}
        onCancel={() => setTrimModalVisible(false)}
        okText="确定"
        cancelText="取消"
      >
        <div style={{ marginBottom: 16 }}>
          <span>保留最新的消息数量：</span>
          <InputNumber
            min={0}
            max={10000}
            value={trimCount}
            onChange={setTrimCount}
            style={{ width: 150, marginLeft: 8 }}
          />
        </div>
        <div style={{ color: '#ff4d4f' }}>
          注意：裁剪操作不可恢复，将永久删除旧消息
        </div>
      </Modal>
    </>
  );
});

QueueDetailsTable.displayName = 'QueueDetailsTable';

export default QueueDetailsTable;