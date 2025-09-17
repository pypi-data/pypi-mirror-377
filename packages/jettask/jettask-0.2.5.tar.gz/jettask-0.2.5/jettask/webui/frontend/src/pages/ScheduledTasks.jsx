import { useState, useEffect, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Card, Button, Space, Tag, message, Modal, Form, Input, Select, Switch, Tooltip, Row, Col, Statistic, InputNumber, Empty } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, PlayCircleOutlined, HistoryOutlined, ShareAltOutlined, FileTextOutlined, TagsOutlined, DatabaseOutlined } from '@ant-design/icons';
import ProTable from '@ant-design/pro-table';
import ScheduledTaskFilter from '../components/ScheduledTaskFilter';
import dayjs from 'dayjs';
import axios from 'axios';
import { useNamespace } from '../contexts/NamespaceContext';

const { Option } = Select;
const { TextArea } = Input;

// 任务类型配置
const TASK_TYPE_CONFIG = {
  'cron': { label: 'Cron表达式', color: 'blue' },
  'interval': { label: '间隔执行', color: 'green' },
  'once': { label: '单次执行', color: 'orange' },
};

// 任务状态配置
const TASK_STATUS_CONFIG = {
  'active': { label: '活跃', color: 'green' },
  'paused': { label: '暂停', color: 'orange' },
  'completed': { label: '已完成', color: 'gray' },
  'error': { label: '错误', color: 'red' },
};

function ScheduledTasks() {
  const [searchParams, setSearchParams] = useSearchParams();
  const { currentNamespace } = useNamespace();

  // 从URL参数初始化状态
  const getInitialState = () => {
    const urlFilters = searchParams.get('filters');

    let initialFilters = [];
    if (urlFilters) {
      try {
        initialFilters = JSON.parse(decodeURIComponent(urlFilters));
      } catch (e) {
        console.error('Failed to parse filters from URL:', e);
      }
    }

    return { initialFilters };
  };

  const { initialFilters } = getInitialState();

  const [selectedTask, setSelectedTask] = useState(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [isEditMode, setIsEditMode] = useState(false);
  const [form] = Form.useForm();
  const [statistics, setStatistics] = useState({
    total: 0,
    active: 0,
    todayExecutions: 0,
    successRate: 0,
  });
  const [filters, setFilters] = useState(initialFilters);
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [selectedTaskDetail, setSelectedTaskDetail] = useState(null);
  const [selectedDetailField, setSelectedDetailField] = useState(null);

  // ProTable相关
  const actionRef = useRef();
  const [tableHeight, setTableHeight] = useState(400);

  // 计算表格高度
  useEffect(() => {
    const updateTableHeight = () => {
      // 视窗高度 - 统计卡片(约120px) - 页边距(约50px) - ProTable工具栏和分页(约150px)
      const availableHeight = window.innerHeight - 320;
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

  // ProTable的请求函数
  const request = async (params) => {
    // 如果没有选择命名空间，返回空数据
    if (!currentNamespace) {
      return {
        data: [],
        success: true,
        total: 0,
      };
    }

    try {
      const requestParams = {
        limit: params.pageSize,
        offset: (params.current - 1) * params.pageSize,
      };

      const response = await axios.get(
        `http://localhost:8001/api/data/scheduled-tasks/${currentNamespace}`,
        { params: requestParams }
      );

      if (response.data) {
        calculateStatistics(response.data.tasks || []);
        return {
          data: response.data.tasks || [],
          success: true,
          total: response.data.total || 0,
        };
      }
      return {
        data: [],
        success: false,
        total: 0,
      };
    } catch (error) {
      console.error('Failed to fetch scheduled tasks:', error);
      return {
        data: [],
        success: false,
        total: 0,
      };
    }
  };



  // 获取统计数据
  const fetchStatistics = async () => {
    if (!currentNamespace) {
      return;
    }
    
    try {
      const response = await axios.get(`/api/scheduled-tasks/statistics/${currentNamespace}`);
      if (response.data) {
        setStatistics(response.data);
      }
    } catch (error) {
      console.error('Failed to fetch statistics:', error);
    }
  };

  // 计算统计数据（保留以兼容旧逻辑）
  const calculateStatistics = (taskList) => {
    // 调用新的统计API
    fetchStatistics();
  };

  // 筛选变化时刷新ProTable并保存状态
  useEffect(() => {
    if (actionRef.current) {
      actionRef.current.reload();
    }
  }, [filters]);

  // 组件加载时获取统计数据，命名空间变化时重新获取
  useEffect(() => {
    if (currentNamespace) {
      fetchStatistics();
    }
  }, [currentNamespace]);


  // 处理添加/编辑任务
  const handleAddOrEditTask = () => {
    form.validateFields().then(async (values) => {
      try {
        const url = isEditMode
          ? `/api/scheduled-tasks/${selectedTask.id}`
          : '/api/scheduled-tasks';
        const method = isEditMode ? 'put' : 'post';

        // 处理task_data
        let taskData = {};
        if (values.task_data) {
          try {
            taskData = JSON.parse(values.task_data);
          } catch (e) {
            message.error('任务数据格式错误，请输入有效的JSON');
            return;
          }
        }

        // 构建请求数据
        const requestData = {
          namespace: currentNamespace,
          name: values.name,
          queue_name: values.queue_name,
          schedule_type: values.schedule_type,
          is_active: values.is_active !== false,
          description: values.description,
          task_data: taskData,
          schedule_config: {}
        };

        // 根据schedule_type设置schedule_config
        if (values.schedule_type === 'cron') {
          requestData.schedule_config = { cron_expression: values.cron_expression };
        } else if (values.schedule_type === 'interval') {
          requestData.schedule_config = { seconds: values.interval_seconds || 60 };
        }

        const response = await axios[method](url, requestData);
        if (response.data.success) {
          message.success(isEditMode ? '任务更新成功' : '任务创建成功');
          setModalVisible(false);
          form.resetFields();
          if (actionRef.current) {
            actionRef.current.reload();
          }
        }
      } catch (error) {
        message.error(isEditMode ? '更新任务失败' : '创建任务失败');
        console.error('Failed to save task:', error);
      }
    });
  };

  // 处理删除任务
  const handleDeleteTask = (task) => {
    Modal.confirm({
      title: '确认删除',
      content: `确定要删除定时任务 "${task.name}" 吗？`,
      onOk: async () => {
        try {
          const response = await axios.delete(`/api/scheduled-tasks/${task.id}`);
          if (response.data.success) {
            message.success('任务删除成功');
            if (actionRef.current) {
              actionRef.current.reload();
            }
          }
        } catch (error) {
          message.error('删除任务失败');
          console.error('Failed to delete task:', error);
        }
      },
    });
  };

  // 处理启用/禁用任务
  const handleToggleTask = async (task) => {
    try {
      const response = await axios.post(`/api/scheduled-tasks/${task.id}/toggle`);
      if (response.data.success) {
        message.success(task.is_active ? '任务已暂停' : '任务已启用');
        if (actionRef.current) {
          actionRef.current.reload();
        }
      }
    } catch (error) {
      message.error('操作失败');
      console.error('Failed to toggle task:', error);
    }
  };

  // 处理立即执行
  const handleExecuteNow = async (task) => {
    try {
      const response = await axios.post(`/api/scheduled-tasks/${task.id}/execute`);
      if (response.data.success) {
        message.success('任务已触发执行');
      }
    } catch (error) {
      message.error('执行失败');
      console.error('Failed to execute task:', error);
    }
  };

  // 打开添加/编辑模态框
  const openModal = (task = null) => {
    setIsEditMode(!!task);
    setSelectedTask(task);
    if (task) {
      // 转换后端数据格式为表单格式
      const formValues = {
        name: task.name,
        queue_name: task.queue_name,
        schedule_type: task.schedule_type,
        is_active: task.is_active,
        description: task.description,
        task_data: task.task_data ? JSON.stringify(task.task_data) : '{}',
      };

      // 根据schedule_type设置相应的配置字段
      if (task.schedule_type === 'cron') {
        formValues.cron_expression = task.schedule_config?.cron_expression;
      } else if (task.schedule_type === 'interval') {
        formValues.interval_seconds = task.schedule_config?.seconds;
      }

      form.setFieldsValue(formValues);
    } else {
      form.resetFields();
    }
    setModalVisible(true);
  };

  // 打开历史记录模态框
  const openHistoryModal = (task) => {
    // 跳转到任务队列详情页面，带上 scheduled_task_id 筛选参数
    window.location.href = `/queue/${task.queue_name}?scheduled_task_id=${task.id}`;
  };

  // 查看任务详情
  const handleViewDetail = (task, field) => {
    setSelectedTaskDetail(task);
    setSelectedDetailField(field);
    setDetailModalVisible(true);
  };


  // ProTable列定义
  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 50,
      ellipsis: true,
      search: false,
    },
    {
      title: '任务名称',
      dataIndex: 'name',
      key: 'name',
      width: 200,
      ellipsis: true,
      search: false,
    },
    {
      title: '队列名称',
      dataIndex: 'queue_name',
      key: 'queue_name',
      width: 120,
      search: false,
    },
    {
      title: '调度类型',
      dataIndex: 'schedule_type',
      key: 'schedule_type',
      width: 100,
      valueType: 'select',
      valueEnum: {
        cron: { text: 'Cron表达式', status: 'Default' },
        interval: { text: '间隔执行', status: 'Processing' },
        once: { text: '单次执行', status: 'Warning' },
      },
      render: (type) => {
        const config = TASK_TYPE_CONFIG[type] || { label: type, color: 'default' };
        return <Tag color={config.color}>{config.label}</Tag>;
      },
      search: false,
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      width: 60,
      valueType: 'select',
      valueEnum: {
        true: { text: '启用', status: 'Success' },
        false: { text: '暂停', status: 'Default' },
      },
      render: (_, record) => (
        <Switch
          checked={record.is_active}
          size="small"
          onChange={() => handleToggleTask(record)}
        />
      ),
      search: false,
    },
    {
      title: '调度配置',
      key: 'schedule',
      width: 80,
      search: false,
      render: (_, record) => {
        if (record.schedule_type === 'cron') {
          return <code>{record.schedule_config?.cron_expression || '-'}</code>;
        } else if (record.schedule_type === 'interval') {
          const seconds = record.schedule_config?.seconds || record.schedule_config?.minutes * 60;
          return `每 ${seconds} 秒`;
        } else {
          return '-';
        }
      },
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      width: 140,
      ellipsis: true,
      search: false,
      render: (text) => (
          text || '-'
      ),
    },
    {
      title: '执行次数',
      dataIndex: 'execution_count',
      key: 'execution_count',
      width: 60,
      ellipsis: true,
      search: false,
      render: (text) => text || 0,
    },
    {
      title: '上次执行',
      dataIndex: 'last_run',
      key: 'last_run',
      width: 130,
      search: false,
      render: (_, record) => {
        const time = record.last_run;
        if (!time) return '-';
        const date = dayjs(time);
        return date.isValid() ? date.format('YYYY-MM-DD HH:mm:ss') : '-';
      },
    },
    {
      title: '下次执行',
      dataIndex: 'next_run',
      key: 'next_run',
      width: 130,
      search: false,
      render: (_, record) => {
        const time = record.next_run;
        if (!time) return '-';
        const date = dayjs(time);
        return date.isValid() ? date.format('YYYY-MM-DD HH:mm:ss') : '-';
      },
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 130,
      search: false,
      render: (_, record) => {
        const text = record.created_at;
        if (!text) return '-';
        const date = dayjs(text);
        return date.isValid() ? date.format('YYYY-MM-DD HH:mm:ss') : '-';
      },
    },
    {
      title: '操作',
      key: 'actions',
      width: 190,
      fixed: 'right',
      search: false,
      render: (_, record) => (
        <Space size="small">
          <Tooltip title="查看任务参数">
            <Button
              type="link"
              size="small"
              icon={<FileTextOutlined />}
              onClick={() => handleViewDetail(record, 'task_data')}
            />
          </Tooltip>
          <Tooltip title={record.tags ? "查看标签" : "无标签"}>
            <Button
              type="link"
              size="small"
              icon={<TagsOutlined />}
              onClick={() => handleViewDetail(record, 'tags')}
              disabled={!record.tags}
              style={{ color: record.tags ? '#722ed1' : undefined }}
            />
          </Tooltip>
          <Tooltip title={record.metadata ? "查看元数据" : "无元数据"}>
            <Button
              type="link"
              size="small"
              icon={<DatabaseOutlined />}
              onClick={() => handleViewDetail(record, 'metadata')}
              disabled={!record.metadata}
              style={{ color: record.metadata ? '#13c2c2' : undefined }}
            />
          </Tooltip>
          <Tooltip title="立即执行">
            <Button
              type="link"
              size="small"
              icon={<PlayCircleOutlined />}
              onClick={() => handleExecuteNow(record)}
              disabled={!record.is_active}
            />
          </Tooltip>
          <Tooltip title="历史">
            <Button
              type="link"
              size="small"
              icon={<HistoryOutlined />}
              onClick={() => openHistoryModal(record)}
            />
          </Tooltip>
          <Tooltip title="编辑">
            <Button
              type="link"
              size="small"
              icon={<EditOutlined />}
              onClick={() => {
                setSelectedTask(record);
                setIsEditMode(true);
                openModal(record);
              }}
            />
          </Tooltip>
          <Tooltip title="删除">
            <Button
              type="link"
              size="small"
              danger
              icon={<DeleteOutlined />}
              onClick={() => handleDeleteTask(record)}
            />
          </Tooltip>
        </Space>
      ),
    },
  ];


  // 如果没有选择命名空间，显示提示
  if (!currentNamespace) {
    return (
      <div className="page-wrapper" style={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center' 
      }}>
        <Empty
          image={Empty.PRESENTED_IMAGE_SIMPLE}
          description={
            <span>
              请先在右上角选择一个命名空间
              <br />
              <span style={{ color: '#999', fontSize: '12px' }}>
                选择命名空间后才能查看该空间的定时任务
              </span>
            </span>
          }
        />
      </div>
    );
  }

  return (
    <div className="page-wrapper">
      {/* 统计卡片 */}
      <Card style={{ marginBottom: 16 }} bodyStyle={{ padding: '16px' }}>
        <Row gutter={16}>
          <Col span={6}>
            <Statistic title="总任务数" value={statistics.total} />
          </Col>
          <Col span={6}>
            <Statistic
              title="活跃任务"
              value={statistics.active}
              valueStyle={{ color: '#3f8600' }}
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="今日执行次数"
              value={statistics.todayExecutions}
              valueStyle={{ color: '#1890ff' }}
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="成功率"
              value={statistics.successRate}
              precision={1}
              suffix="%"
              valueStyle={{ color: statistics.successRate > 90 ? '#3f8600' : '#cf1322' }}
            />
          </Col>
        </Row>
      </Card>

      {/* ProTable卡片 */}
      <Card style={{ marginBottom: 0 }}>
        <ProTable
        columns={columns}
        actionRef={actionRef}
        request={request}
        rowKey="id"
        pagination={{
          showQuickJumper: true,
          showSizeChanger: true,
          defaultPageSize: 20,
        }}
        search={false}
        dateFormatter="string"
        headerTitle="定时任务列表"
        scroll={{ 
          y: tableHeight,
          x: 1680,
        }}
        size="small"
        options={{
          reload: true,
          density: true,
          fullScreen: true,
          setting: true,
        }}
        toolbar={{
          title: (
            <Space>
              <ScheduledTaskFilter
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
            <Button
              key="add"
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => openModal()}
            >
              新建任务
            </Button>,
            <Button
              key="share"
              icon={<ShareAltOutlined />}
              onClick={() => {
                if (filters && filters.length > 0) {
                  const params = new URLSearchParams();
                  params.set('filters', encodeURIComponent(JSON.stringify(filters)));
                  const shareUrl = `${window.location.origin}${window.location.pathname}?${params.toString()}`;
                  navigator.clipboard.writeText(shareUrl);
                  message.success('分享链接已复制到剪贴板');
                } else {
                  message.info('当前没有筛选条件可分享');
                }
              }}
            >
              分享筛选
            </Button>,
          ],
        }}
        params={{
          filters,
          currentNamespace,
        }}
        />
      </Card>

      {/* 详情查看弹窗 */}
      <Modal
        title={`${
          selectedDetailField === 'task_data' ? '任务参数' : 
          selectedDetailField === 'tags' ? '标签' : 
          selectedDetailField === 'metadata' ? '元数据' : ''
        } - ${selectedTaskDetail?.name || ''}`}
        open={detailModalVisible}
        onCancel={() => {
          setDetailModalVisible(false);
          setSelectedTaskDetail(null);
          setSelectedDetailField(null);
        }}
        width={800}
        footer={null}
      >
        <div style={{ maxHeight: '60vh', overflowY: 'auto' }}>
          <pre style={{ 
            backgroundColor: '#f5f5f5', 
            padding: '16px', 
            borderRadius: '4px',
            fontSize: '12px',
            lineHeight: '1.5',
            overflowX: 'auto'
          }}>
            {selectedTaskDetail && selectedDetailField ? 
              JSON.stringify(selectedTaskDetail[selectedDetailField], null, 2) : 
              '无数据'
            }
          </pre>
        </div>
      </Modal>

      {/* 添加/编辑任务模态框 */}
      <Modal
        title={isEditMode ? '编辑定时任务' : '添加定时任务'}
        open={modalVisible}
        onOk={handleAddOrEditTask}
        onCancel={() => {
          setModalVisible(false);
          form.resetFields();
        }}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          initialValues={{
            schedule_type: 'interval',
            is_active: true,
            task_data: '{}',
          }}
        >
          <Form.Item
            name="name"
            label="任务名称"
            rules={[{ required: true, message: '请输入任务名称' }]}
          >
            <Input placeholder="任务的描述性名称" />
          </Form.Item>

          <Form.Item
            name="schedule_type"
            label="调度类型"
            rules={[{ required: true, message: '请选择调度类型' }]}
          >
            <Select>
              <Option value="interval">间隔执行</Option>
              <Option value="cron">Cron表达式</Option>
              <Option value="once">单次执行</Option>
            </Select>
          </Form.Item>

          <Form.Item noStyle shouldUpdate={(prevValues, currentValues) => prevValues.schedule_type !== currentValues.schedule_type}>
            {({ getFieldValue }) => {
              const scheduleType = getFieldValue('schedule_type');
              if (scheduleType === 'cron') {
                return (
                  <Form.Item
                    name="cron_expression"
                    label="Cron表达式"
                    rules={[{ required: true, message: '请输入Cron表达式' }]}
                    extra="例如: 0 0 * * * (每天零点)"
                  >
                    <Input placeholder="* * * * *" />
                  </Form.Item>
                );
              } else if (scheduleType === 'interval') {
                return (
                  <Form.Item
                    name="interval_seconds"
                    label="执行间隔（秒）"
                    rules={[{ required: true, message: '请输入执行间隔' }]}
                  >
                    <InputNumber min={1} style={{ width: '100%' }} placeholder="60" />
                  </Form.Item>
                );
              }
              return null;
            }}
          </Form.Item>

          <Form.Item
            name="queue_name"
            label="目标队列"
            rules={[{ required: true, message: '请输入目标队列' }]}
          >
            <Input placeholder="default" />
          </Form.Item>

          <Form.Item
            name="task_data"
            label="任务数据 (JSON格式)"
            extra={'例如: {"args": [], "kwargs": {"key": "value"}}'}
          >
            <TextArea rows={3} placeholder="{}" />
          </Form.Item>


          <Form.Item
            name="description"
            label="任务描述"
          >
            <TextArea rows={2} placeholder="任务的详细描述" />
          </Form.Item>

          <Form.Item
            name="is_active"
            label="启用状态"
            valuePropName="checked"
          >
            <Switch checkedChildren="启用" unCheckedChildren="暂停" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}

export default ScheduledTasks;