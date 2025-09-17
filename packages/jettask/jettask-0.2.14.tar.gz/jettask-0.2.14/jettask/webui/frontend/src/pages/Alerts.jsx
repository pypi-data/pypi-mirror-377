import { useState, useEffect } from 'react';
import { Card, Table, Button, Space, Tag, message, Modal, Form, Input, Select, Switch, InputNumber, Row, Col, Statistic, Tabs, Timeline, Badge } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, ReloadOutlined, BellOutlined, WarningOutlined, CheckCircleOutlined, CloseCircleOutlined, HistoryOutlined, ExpandOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import axios from 'axios';

const { Option } = Select;
const { TextArea } = Input;
const { TabPane } = Tabs;

// 告警级别配置
const ALERT_LEVEL_CONFIG = {
  'critical': { label: '严重', color: 'red', icon: <CloseCircleOutlined /> },
  'warning': { label: '警告', color: 'orange', icon: <WarningOutlined /> },
  'info': { label: '信息', color: 'blue', icon: <BellOutlined /> },
};

// 告警类型配置
const ALERT_TYPE_CONFIG = {
  'error_rate': { label: '错误率', description: '任务错误率超过阈值' },
  'queue_length': { label: '队列长度', description: '队列积压任务超过阈值' },
  'worker_count': { label: 'Worker数量', description: 'Worker数量低于阈值' },
  'execution_time': { label: '执行时长', description: '任务执行时间超过阈值' },
  'failure_count': { label: '失败次数', description: '连续失败次数超过阈值' },
  'throughput': { label: '吞吐量', description: '任务处理速率低于阈值' },
  'idle_time': { label: '空闲时间', description: 'Worker空闲时间超过阈值' },
  'memory_usage': { label: '内存使用', description: 'Worker内存使用超过阈值' },
};

// 比较操作符
const OPERATORS = {
  'gt': '大于',
  'gte': '大于等于',
  'lt': '小于',
  'lte': '小于等于',
  'eq': '等于',
  'ne': '不等于',
};

function Alerts() {
  const [loading, setLoading] = useState(false);
  const [alertRules, setAlertRules] = useState([]);
  const [alertHistory, setAlertHistory] = useState([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [historyModalVisible, setHistoryModalVisible] = useState(false);
  const [isEditMode, setIsEditMode] = useState(false);
  const [selectedRule, setSelectedRule] = useState(null);
  const [form] = Form.useForm();
  const [statistics, setStatistics] = useState({
    totalRules: 0,
    activeRules: 0,
    todayAlerts: 0,
    criticalAlerts: 0,
  });
  const [activeTab, setActiveTab] = useState('rules');

  // 获取告警规则列表
  const fetchAlertRules = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/alert-rules');
      if (response.data.success) {
        setAlertRules(response.data.data);
        calculateStatistics(response.data.data);
      }
    } catch (error) {
      message.error('获取告警规则失败');
      console.error('Failed to fetch alert rules:', error);
    } finally {
      setLoading(false);
    }
  };

  // 获取告警历史
  const fetchAlertHistory = async (ruleId = null) => {
    try {
      // 使用正确的API端点
      if (ruleId) {
        const response = await axios.get(`/api/alert-rules/${ruleId}/history`);
        if (response.data.success) {
          setAlertHistory(response.data.data);
        }
      } else {
        // 暂时设置为空，因为后端还没有全局历史API
        setAlertHistory([]);
      }
    } catch (error) {
      message.error('获取告警历史失败');
      console.error('Failed to fetch alert history:', error);
    }
  };

  // 计算统计数据
  const calculateStatistics = (rules) => {
    const stats = {
      totalRules: rules.length,
      activeRules: rules.filter(r => r.is_active).length,
      todayAlerts: 0, // 需要从后端获取
      criticalAlerts: 0, // 需要从后端获取
    };
    setStatistics(stats);
  };

  // 初始化加载
  useEffect(() => {
    fetchAlertRules();
    fetchAlertHistory();
  }, []);

  // 处理添加/编辑规则
  const handleAddOrEditRule = () => {
    form.validateFields().then(async (values) => {
      try {
        // 处理webhook_headers
        if (values.webhook_headers) {
          try {
            values.webhook_headers = JSON.parse(values.webhook_headers);
          } catch (e) {
            message.error('Webhook头部格式错误，请输入有效的JSON');
            return;
          }
        }

        // 处理额外配置
        if (values.extra_config) {
          try {
            values.extra_config = JSON.parse(values.extra_config);
          } catch (e) {
            message.error('额外配置格式错误，请输入有效的JSON');
            return;
          }
        }

        const url = isEditMode 
          ? `/api/alert-rules/${selectedRule.id}` 
          : '/api/alert-rules';
        const method = isEditMode ? 'put' : 'post';

        const response = await axios[method](url, values);
        if (response.data.success) {
          message.success(isEditMode ? '规则更新成功' : '规则创建成功');
          setModalVisible(false);
          form.resetFields();
          fetchAlertRules();
        }
      } catch (error) {
        message.error(isEditMode ? '更新规则失败' : '创建规则失败');
        console.error('Failed to save rule:', error);
      }
    });
  };

  // 处理删除规则
  const handleDeleteRule = (rule) => {
    Modal.confirm({
      title: '确认删除',
      content: `确定要删除告警规则 "${rule.name}" 吗？`,
      onOk: async () => {
        try {
          const response = await axios.delete(`/api/alert-rules/${rule.id}`);
          if (response.data.success) {
            message.success('规则删除成功');
            fetchAlertRules();
          }
        } catch (error) {
          message.error('删除规则失败');
          console.error('Failed to delete rule:', error);
        }
      },
    });
  };

  // 处理启用/禁用规则
  const handleToggleRule = async (rule) => {
    try {
      const response = await axios.put(`/api/alert-rules/${rule.id}/toggle`, {
        enabled: !rule.enabled,
      });
      if (response.data.success) {
        message.success(rule.enabled ? '规则已禁用' : '规则已启用');
        fetchAlertRules();
      }
    } catch (error) {
      message.error('操作失败');
      console.error('Failed to toggle rule:', error);
    }
  };

  // 测试告警规则
  const handleTestRule = async (rule) => {
    try {
      const response = await axios.post(`/api/alert-rules/${rule.id}/test`);
      if (response.data.success) {
        message.success('测试告警已发送');
      }
    } catch (error) {
      message.error('测试失败');
      console.error('Failed to test rule:', error);
    }
  };

  // 打开添加/编辑模态框
  const openModal = (rule = null) => {
    setIsEditMode(!!rule);
    setSelectedRule(rule);
    if (rule) {
      form.setFieldsValue({
        ...rule,
        webhook_headers: rule.webhook_headers ? JSON.stringify(rule.webhook_headers) : '{}',
        extra_config: rule.extra_config ? JSON.stringify(rule.extra_config) : '{}',
      });
    } else {
      form.resetFields();
    }
    setModalVisible(true);
  };

  // 查看规则历史
  const viewRuleHistory = (rule) => {
    setSelectedRule(rule);
    fetchAlertHistory(rule.id);
    setHistoryModalVisible(true);
  };

  // 规则表格列定义
  const ruleColumns = [
    {
      title: '规则名称',
      dataIndex: 'name',
      key: 'name',
      width: 200,
    },
    {
      title: '类型',
      dataIndex: 'alert_type',
      key: 'alert_type',
      width: 120,
      render: (type) => {
        const config = ALERT_TYPE_CONFIG[type] || { label: type };
        return config.label;
      },
    },
    {
      title: '级别',
      dataIndex: 'level',
      key: 'level',
      width: 80,
      render: (level) => {
        const config = ALERT_LEVEL_CONFIG[level] || { label: level, color: 'default' };
        return <Tag color={config.color}>{config.label}</Tag>;
      },
    },
    {
      title: '条件',
      key: 'condition',
      width: 200,
      render: (_, record) => {
        const operator = OPERATORS[record.operator] || record.operator;
        const scope = record.scope === 'queue' ? `队列: ${record.queue_name || '全部'}` : '全局';
        return (
          <div>
            <div>{scope}</div>
            <div style={{ fontSize: 12, color: '#666' }}>
              {`${ALERT_TYPE_CONFIG[record.alert_type]?.label} ${operator} ${record.threshold}`}
              {record.time_window && ` (${record.time_window}秒内)`}
            </div>
          </div>
        );
      },
    },
    {
      title: 'Webhook',
      dataIndex: 'webhook_url',
      key: 'webhook_url',
      width: 200,
      ellipsis: true,
      render: (url) => url ? <span style={{ fontSize: 12 }}>{url}</span> : '-',
    },
    {
      title: '状态',
      dataIndex: 'enabled',
      key: 'enabled',
      width: 80,
      render: (enabled) => (
        <Badge status={enabled ? 'success' : 'default'} text={enabled ? '启用' : '禁用'} />
      ),
    },
    {
      title: '最后触发',
      dataIndex: 'last_triggered',
      key: 'last_triggered',
      width: 150,
      render: (time) => time ? dayjs(time).format('MM-DD HH:mm:ss') : '-',
    },
    {
      title: '操作',
      key: 'actions',
      width: 200,
      fixed: 'right',
      render: (_, record) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            onClick={() => handleToggleRule(record)}
          >
            {record.enabled ? '禁用' : '启用'}
          </Button>
          <Button
            type="link"
            size="small"
            onClick={() => handleTestRule(record)}
          >
            测试
          </Button>
          <Button
            type="link"
            size="small"
            onClick={() => viewRuleHistory(record)}
          >
            历史
          </Button>
          <Button
            type="link"
            size="small"
            onClick={() => openModal(record)}
          >
            编辑
          </Button>
          <Button
            type="link"
            size="small"
            danger
            onClick={() => handleDeleteRule(record)}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ];

  // 告警历史表格列
  const historyColumns = [
    {
      title: '触发时间',
      dataIndex: 'triggered_at',
      key: 'triggered_at',
      width: 150,
      render: (time) => dayjs(time).format('YYYY-MM-DD HH:mm:ss'),
    },
    {
      title: '规则名称',
      dataIndex: 'rule_name',
      key: 'rule_name',
      width: 200,
    },
    {
      title: '级别',
      dataIndex: 'level',
      key: 'level',
      width: 80,
      render: (level) => {
        const config = ALERT_LEVEL_CONFIG[level] || { label: level, color: 'default' };
        return <Tag color={config.color} icon={config.icon}>{config.label}</Tag>;
      },
    },
    {
      title: '告警内容',
      dataIndex: 'message',
      key: 'message',
      ellipsis: true,
    },
    {
      title: '通知状态',
      dataIndex: 'notification_status',
      key: 'notification_status',
      width: 100,
      render: (status) => (
        <Tag color={status === 'success' ? 'green' : 'red'}>
          {status === 'success' ? '已发送' : '发送失败'}
        </Tag>
      ),
    },
  ];

  return (
    <div className="page-wrapper">

      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card>
            <Statistic title="规则总数" value={statistics.totalRules} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="活跃规则" 
              value={statistics.activeRules} 
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="今日告警" 
              value={statistics.todayAlerts} 
              suffix="次"
              valueStyle={{ color: '#ff9800' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="严重告警" 
              value={statistics.criticalAlerts} 
              suffix="个"
              valueStyle={{ color: '#f50' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 主内容区域 */}
      <Card>
        <Tabs activeKey={activeTab} onChange={setActiveTab}>
          <TabPane tab="告警规则" key="rules">
            <div style={{ marginBottom: 16 }}>
              <Space>
                <Button 
                  icon={<ReloadOutlined />} 
                  onClick={fetchAlertRules}
                >
                  刷新
                </Button>
                <Button 
                  type="primary" 
                  icon={<PlusOutlined />}
                  onClick={() => openModal()}
                >
                  添加规则
                </Button>
              </Space>
            </div>
            <Table
              columns={ruleColumns}
              dataSource={alertRules}
              rowKey="id"
              loading={loading}
              scroll={{ x: 1300 }}
              pagination={{
                pageSize: 10,
                showSizeChanger: true,
                showTotal: (total) => `共 ${total} 条`,
              }}
            />
          </TabPane>
          
          <TabPane tab="告警历史" key="history">
            <div style={{ marginBottom: 16 }}>
              <Button 
                icon={<ReloadOutlined />} 
                onClick={() => fetchAlertHistory()}
              >
                刷新
              </Button>
            </div>
            <Table
              columns={historyColumns}
              dataSource={alertHistory}
              rowKey="id"
              pagination={{
                pageSize: 20,
                showSizeChanger: true,
                showTotal: (total) => `共 ${total} 条`,
              }}
            />
          </TabPane>
        </Tabs>
      </Card>

      {/* 添加/编辑规则模态框 */}
      <Modal
        title={isEditMode ? '编辑告警规则' : '添加告警规则'}
        open={modalVisible}
        onOk={handleAddOrEditRule}
        onCancel={() => {
          setModalVisible(false);
          form.resetFields();
        }}
        width={700}
      >
        <Form
          form={form}
          layout="vertical"
          initialValues={{
            enabled: true,
            level: 'warning',
            scope: 'global',
            operator: 'gt',
            time_window: 300,
            webhook_headers: '{}',
            extra_config: '{}',
          }}
        >
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="name"
                label="规则名称"
                rules={[{ required: true, message: '请输入规则名称' }]}
              >
                <Input placeholder="如：队列积压告警" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="level"
                label="告警级别"
                rules={[{ required: true, message: '请选择告警级别' }]}
              >
                <Select>
                  <Option value="info">信息</Option>
                  <Option value="warning">警告</Option>
                  <Option value="critical">严重</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="alert_type"
                label="告警类型"
                rules={[{ required: true, message: '请选择告警类型' }]}
              >
                <Select>
                  {Object.entries(ALERT_TYPE_CONFIG).map(([key, config]) => (
                    <Option key={key} value={key}>
                      {config.label}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="scope"
                label="监控范围"
                rules={[{ required: true, message: '请选择监控范围' }]}
              >
                <Select onChange={(value) => {
                  if (value === 'global') {
                    form.setFieldsValue({ queue_name: undefined });
                  }
                }}>
                  <Option value="global">全局</Option>
                  <Option value="queue">指定队列</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Form.Item noStyle shouldUpdate={(prevValues, currentValues) => prevValues.scope !== currentValues.scope}>
            {({ getFieldValue }) => {
              return getFieldValue('scope') === 'queue' ? (
                <Form.Item
                  name="queue_name"
                  label="队列名称"
                  rules={[{ required: true, message: '请输入队列名称' }]}
                >
                  <Input placeholder="输入要监控的队列名称" />
                </Form.Item>
              ) : null;
            }}
          </Form.Item>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                name="operator"
                label="比较操作"
                rules={[{ required: true, message: '请选择比较操作' }]}
              >
                <Select>
                  {Object.entries(OPERATORS).map(([key, label]) => (
                    <Option key={key} value={key}>{label}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="threshold"
                label="阈值"
                rules={[{ required: true, message: '请输入阈值' }]}
              >
                <InputNumber style={{ width: '100%' }} placeholder="如：80" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="time_window"
                label="时间窗口（秒）"
                rules={[{ required: true, message: '请输入时间窗口' }]}
              >
                <InputNumber min={1} style={{ width: '100%' }} placeholder="300" />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            name="description"
            label="规则描述"
          >
            <TextArea rows={2} placeholder="描述这个告警规则的用途" />
          </Form.Item>

          <Form.Item
            name="webhook_url"
            label="Webhook URL"
            rules={[{ type: 'url', message: '请输入有效的URL' }]}
          >
            <Input placeholder="https://example.com/webhook" />
          </Form.Item>

          <Form.Item
            name="webhook_headers"
            label="Webhook Headers (JSON)"
            extra={'例如: {"Authorization": "Bearer token"}'}
          >
            <TextArea rows={2} placeholder="{}" />
          </Form.Item>

          <Form.Item
            name="extra_config"
            label="额外配置 (JSON)"
            extra="其他自定义配置项"
          >
            <TextArea rows={2} placeholder="{}" />
          </Form.Item>

          <Form.Item
            name="enabled"
            label="启用状态"
            valuePropName="checked"
          >
            <Switch checkedChildren="启用" unCheckedChildren="禁用" />
          </Form.Item>
        </Form>
      </Modal>

      {/* 规则历史模态框 */}
      <Modal
        title={`告警历史 - ${selectedRule?.name}`}
        open={historyModalVisible}
        onCancel={() => {
          setHistoryModalVisible(false);
          setAlertHistory([]);
        }}
        width={900}
        footer={null}
      >
        <Table
          columns={historyColumns}
          dataSource={alertHistory}
          rowKey="id"
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
          }}
        />
      </Modal>

    </div>
  );
}

export default Alerts;