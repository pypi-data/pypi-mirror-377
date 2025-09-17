import { useState, useEffect } from 'react';
import { 
  Card, 
  Button, 
  Table, 
  Modal, 
  Form, 
  Input, 
  InputNumber,
  message, 
  Space, 
  Tag, 
  Popconfirm,
  Typography,
  Row,
  Col,
  Descriptions,
  Tooltip,
  Alert,
  Divider,
  Select,
  Switch
} from 'antd';
import { 
  PlusOutlined, 
  EditOutlined, 
  DeleteOutlined, 
  CopyOutlined,
  DatabaseOutlined,
  CloudServerOutlined,
  KeyOutlined,
  SettingOutlined,
  GlobalOutlined,
  BellOutlined,
  SecurityScanOutlined
} from '@ant-design/icons';
import axios from 'axios';
import { useNamespace } from '../contexts/NamespaceContext';

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;

function Settings() {
  const { refreshNamespaceList } = useNamespace();  // 获取刷新方法
  // 命名空间管理相关状态
  const [namespaces, setNamespaces] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingNamespace, setEditingNamespace] = useState(null);
  const [form] = Form.useForm();
  const [selectedNamespace, setSelectedNamespace] = useState(null);
  const [detailModalVisible, setDetailModalVisible] = useState(false);

  // 系统设置相关状态
  const [systemSettings, setSystemSettings] = useState({
    theme: 'light',
    autoRefresh: true,
    refreshInterval: 30,
    notifications: true,
    security: {
      sessionTimeout: 120,
      enableSSL: false
    }
  });

  // 获取命名空间列表
  const fetchNamespaces = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/namespaces');
      setNamespaces(response.data);
    } catch (error) {
      console.error('Failed to fetch namespaces:', error);
      message.error('获取命名空间列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNamespaces();
  }, []);

  // 创建或编辑命名空间
  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      
      if (editingNamespace) {
        // 编辑模式
        const updateData = {
          description: values.description,
          redis_config: {
            host: values.redis_host,
            port: values.redis_port,
            password: values.redis_password,
            db: values.redis_db || 0
          },
          pg_config: {
            host: values.pg_host,
            port: values.pg_port,
            user: values.pg_user,
            password: values.pg_password,
            database: values.pg_database
          }
        };
        
        const response = await axios.put(
          `/api/namespaces/${editingNamespace.name}`,
          updateData
        );
        
        message.success('命名空间配置已更新');
        setModalVisible(false);
        form.resetFields();
        setEditingNamespace(null);
        fetchNamespaces();
        refreshNamespaceList();  // 触发全局命名空间列表刷新
        
        // 显示更新后的版本信息
        Modal.success({
          title: '配置更新成功',
          content: (
            <div>
              <p>命名空间 "{editingNamespace.name}" 的配置已成功更新。</p>
              <p>新版本号：v{response.data.version}</p>
              <Alert
                message="版本自动递增"
                description="配置更新后，版本号会自动递增。Worker将在下次重启时获取最新配置。"
                type="info"
                showIcon
              />
            </div>
          ),
          width: 600
        });
      } else {
        // 创建新命名空间
        const response = await axios.post('/api/namespaces', {
          name: values.name,
          description: values.description,
          redis_config: {
            host: values.redis_host,
            port: values.redis_port,
            password: values.redis_password,
            db: values.redis_db || 0
          },
          pg_config: {
            host: values.pg_host,
            port: values.pg_port,
            user: values.pg_user,
            password: values.pg_password,
            database: values.pg_database
          }
        });
        
        message.success('命名空间创建成功');
        setModalVisible(false);
        form.resetFields();
        fetchNamespaces();
        refreshNamespaceList();  // 触发全局命名空间列表刷新
        
        // 显示连接URL
        const fullUrl = `http://localhost:8001${response.data.connection_url}`;
        Modal.success({
          title: '命名空间创建成功',
          content: (
            <div>
              <p>命名空间 "{values.name}" 已成功创建。</p>
              <p>连接路径：</p>
              <Input.TextArea 
                value={response.data.connection_url} 
                readOnly 
                autoSize={{ minRows: 1, maxRows: 2 }}
              />
              <Alert 
                style={{ marginTop: 12, marginBottom: 12 }}
                message="使用说明" 
                description={
                  <div>
                    <p>在JetTask应用中使用时，需要添加完整的服务器地址：</p>
                    <code style={{ background: '#f5f5f5', padding: '4px 8px', borderRadius: 3, display: 'block', marginTop: 8 }}>
                      task_center_url='http://[服务器地址]:8001{response.data.connection_url}'
                    </code>
                    <p style={{ marginTop: 8 }}>示例：</p>
                    <code style={{ background: '#f5f5f5', padding: '4px 8px', borderRadius: 3, display: 'block' }}>
                      task_center_url='{fullUrl}'
                    </code>
                  </div>
                } 
                type="info" 
                showIcon 
              />
              <Button 
                type="primary" 
                icon={<CopyOutlined />}
                onClick={() => {
                  navigator.clipboard.writeText(fullUrl);
                  message.success('完整URL已复制到剪贴板');
                }}
              >
                复制完整URL（本地开发）
              </Button>
              <Button 
                type="link" 
                icon={<CopyOutlined />}
                onClick={() => {
                  navigator.clipboard.writeText(response.data.connection_url);
                  message.success('路径已复制到剪贴板');
                }}
                style={{ marginLeft: 8 }}
              >
                仅复制路径
              </Button>
            </div>
          ),
          width: 700
        });
      }
    } catch (error) {
      console.error('Failed to save namespace:', error);
      message.error(error.response?.data?.detail || '操作失败');
    }
  };

  // 删除命名空间
  const handleDelete = async (namespace) => {
    if (namespace.name === 'default') {
      message.error('默认命名空间不能删除');
      return;
    }
    
    try {
      await axios.delete(`/api/namespaces/${namespace.name}`);
      message.success('命名空间已删除');
      fetchNamespaces();
      refreshNamespaceList();  // 触发全局命名空间列表刷新
    } catch (error) {
      console.error('Failed to delete namespace:', error);
      message.error(error.response?.data?.detail || '删除失败');
    }
  };

  // 查看命名空间详情
  const handleViewDetails = async (namespace) => {
    try {
      const response = await axios.get(`/api/namespaces/${namespace.name}`);
      setSelectedNamespace({
        ...namespace,
        config: response.data
      });
      setDetailModalVisible(true);
    } catch (error) {
      console.error('Failed to fetch namespace config:', error);
      message.error('获取命名空间配置失败');
    }
  };

  // 编辑命名空间
  const handleEdit = async (namespace) => {
    try {
      // 获取最新配置
      const response = await axios.get(`/api/namespaces/${namespace.name}`);
      const config = response.data;
      
      // 设置编辑状态
      setEditingNamespace(namespace);
      
      // 填充表单数据
      form.setFieldsValue({
        name: namespace.name,
        description: namespace.description || '',
        redis_host: config.redis_config?.host || 'localhost',
        redis_port: config.redis_config?.port || 6379,
        redis_password: config.redis_config?.password || '',
        redis_db: config.redis_config?.db || 0,
        pg_host: config.pg_config?.host || 'localhost',
        pg_port: config.pg_config?.port || 5432,
        pg_user: config.pg_config?.user || 'jettask',
        pg_password: config.pg_config?.password || '',
        pg_database: config.pg_config?.database || 'jettask'
      });
      
      setModalVisible(true);
    } catch (error) {
      console.error('Failed to fetch namespace config:', error);
      message.error('获取命名空间配置失败');
    }
  };

  // 系统设置保存
  const handleSystemSettingsSave = () => {
    message.success('系统设置已保存');
  };

  const namespaceColumns = [
    {
      title: '命名空间名称',
      dataIndex: 'name',
      key: 'name',
      width: 200,
      ellipsis: true,
      render: (text, record) => (
        <Space>
          <Tooltip title={text}>
            <Text strong style={{ maxWidth: 150, display: 'inline-block' }} ellipsis>{text}</Text>
          </Tooltip>
          {text === 'default' && <Tag color="blue">默认</Tag>}
        </Space>
      )
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
      render: (text) => text || '-'
    },
    {
      title: '版本',
      dataIndex: 'version',
      key: 'version',
      width: 80,
      render: (text) => <Tag color="blue">v{text || 1}</Tag>
    },
    {
      title: '连接路径',
      dataIndex: 'connection_url',
      key: 'connection_url',
      ellipsis: true,
      render: (text) => (
        <Tooltip title={`完整URL: http://[服务器]:8001${text}`}>
          <Text copyable={{ text }} style={{ maxWidth: 300 }} ellipsis>
            {text}
          </Text>
        </Tooltip>
      )
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (text) => text ? new Date(text).toLocaleString() : '-'
    },
    {
      title: '操作',
      key: 'actions',
      width: 250,
      render: (_, record) => (
        <Space>
          <Tooltip title="查看配置">
            <Button 
              type="link" 
              icon={<DatabaseOutlined />}
              onClick={() => handleViewDetails(record)}
            />
          </Tooltip>
          <Tooltip title="复制路径">
            <Button 
              type="link" 
              icon={<CopyOutlined />}
              onClick={() => {
                navigator.clipboard.writeText(record.connection_url);
                message.success(`路径已复制: ${record.connection_url}`);
              }}
            />
          </Tooltip>
          <Tooltip title="编辑配置">
            <Button 
              type="link" 
              icon={<EditOutlined />}
              onClick={() => handleEdit(record)}
            />
          </Tooltip>
          {record.name !== 'default' && (
            <Popconfirm
              title="确定要删除这个命名空间吗？"
              description="删除后无法恢复，请谨慎操作。"
              onConfirm={() => handleDelete(record)}
              okText="确定"
              cancelText="取消"
            >
              <Tooltip title="删除">
                <Button 
                  type="link" 
                  danger 
                  icon={<DeleteOutlined />}
                />
              </Tooltip>
            </Popconfirm>
          )}
        </Space>
      )
    }
  ];

  return (
    <div style={{ padding: 24 }}>
      {/* 页面标题 */}
      <Title level={2}>
        <SettingOutlined /> 系统设置
      </Title>
      <Text type="secondary" style={{ display: 'block', marginBottom: 24 }}>
        管理系统配置、命名空间、通知和安全设置等
      </Text>

      {/* 命名空间管理 */}
      <Card style={{ marginBottom: 24 }}>
        <Title level={3}>
          <GlobalOutlined style={{ marginRight: 8 }} />
          命名空间管理
        </Title>
        <Text type="secondary" style={{ display: 'block', marginBottom: 16 }}>
          管理多租户命名空间，每个命名空间拥有独立的配置和数据隔离
        </Text>

        <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
          <Col>
            <Alert
              message="使用说明"
              description={
                <div style={{ fontSize: '13px' }}>
                  <Space direction="vertical" size={4} style={{ width: '100%' }}>
                    <div>
                      <strong>快速使用：</strong> ① 创建命名空间 → ② 复制连接路径 → ③ 在代码中使用：
                      <code style={{ background: '#f5f5f5', padding: '2px 6px', borderRadius: 3, marginLeft: 8 }}>
                        Jettask(task_center_url='http://[服务器]:8001[路径]')
                      </code>
                    </div>
                    <div>
                      <strong>特性：</strong> 多租户隔离 | 配置热更新 | 版本自动递增 | 默认命名空间保护
                    </div>
                  </Space>
                </div>
              }
              type="info"
              showIcon
              closable
              style={{ marginBottom: 16 }}
            />
          </Col>
          <Col>
            <Button 
              type="primary" 
              icon={<PlusOutlined />}
              onClick={() => {
                setEditingNamespace(null);
                form.resetFields();
                setModalVisible(true);
              }}
            >
              创建命名空间
            </Button>
          </Col>
        </Row>

        <Table 
          columns={namespaceColumns}
          dataSource={namespaces}
          rowKey="id"
          loading={loading}
          pagination={false}
          size="small"
        />
      </Card>

      {/* 系统配置 */}
      <Card style={{ marginBottom: 24 }}>
        <Title level={3}>
          <SettingOutlined style={{ marginRight: 8 }} />
          系统配置
        </Title>
        <Text type="secondary" style={{ display: 'block', marginBottom: 16 }}>
          配置系统的基本行为和外观设置
        </Text>

        <Form layout="vertical" onFinish={handleSystemSettingsSave}>
          <Row gutter={24}>
            <Col span={12}>
              <Form.Item label="主题设置">
                <Select 
                  value={systemSettings.theme} 
                  onChange={(value) => setSystemSettings({...systemSettings, theme: value})}
                >
                  <Option value="light">浅色主题</Option>
                  <Option value="dark">深色主题</Option>
                  <Option value="auto">跟随系统</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item label="自动刷新间隔（秒）">
                <InputNumber 
                  value={systemSettings.refreshInterval}
                  onChange={(value) => setSystemSettings({...systemSettings, refreshInterval: value})}
                  min={5}
                  max={300}
                  style={{ width: '100%' }}
                />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={24}>
            <Col span={12}>
              <Form.Item label="启用自动刷新">
                <Switch 
                  checked={systemSettings.autoRefresh}
                  onChange={(checked) => setSystemSettings({...systemSettings, autoRefresh: checked})}
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item label="启用系统通知">
                <Switch 
                  checked={systemSettings.notifications}
                  onChange={(checked) => setSystemSettings({...systemSettings, notifications: checked})}
                />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Card>

      {/* 通知设置 */}
      <Card style={{ marginBottom: 24 }}>
        <Title level={3}>
          <BellOutlined style={{ marginRight: 8 }} />
          通知设置
        </Title>
        <Text type="secondary" style={{ display: 'block', marginBottom: 16 }}>
          配置系统告警和通知方式
        </Text>
        <Alert 
          message="功能开发中" 
          description="通知设置功能正在开发中，敬请期待。"
          type="info"
          showIcon
        />
      </Card>

      {/* 安全设置 */}
      <Card>
        <Title level={3}>
          <SecurityScanOutlined style={{ marginRight: 8 }} />
          安全设置
        </Title>
        <Text type="secondary" style={{ display: 'block', marginBottom: 16 }}>
          配置系统安全策略和访问控制
        </Text>
        
        <Row gutter={24}>
          <Col span={12}>
            <Form.Item label="会话超时时间（分钟）">
              <InputNumber 
                value={systemSettings.security.sessionTimeout}
                onChange={(value) => setSystemSettings({
                  ...systemSettings, 
                  security: {...systemSettings.security, sessionTimeout: value}
                })}
                min={15}
                max={480}
                style={{ width: '100%' }}
              />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item label="启用SSL">
              <Switch 
                checked={systemSettings.security.enableSSL}
                onChange={(checked) => setSystemSettings({
                  ...systemSettings, 
                  security: {...systemSettings.security, enableSSL: checked}
                })}
              />
            </Form.Item>
          </Col>
        </Row>

        <Alert 
          message="安全提示" 
          description="建议在生产环境中启用SSL，并设置合理的会话超时时间。"
          type="warning"
          showIcon
          style={{ marginTop: 16 }}
        />
      </Card>

      {/* 创建/编辑命名空间的模态框 */}
      <Modal
        title={editingNamespace ? '编辑命名空间' : '创建命名空间'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => {
          setModalVisible(false);
          form.resetFields();
          setEditingNamespace(null);
        }}
        width={700}
      >
        <Form
          form={form}
          layout="vertical"
          initialValues={{
            redis_host: 'localhost',
            redis_port: 6379,
            redis_db: 0,
            pg_host: 'localhost',
            pg_port: 5432,
            pg_user: 'jettask',
            pg_database: 'jettask'
          }}
        >
          <Form.Item
            name="name"
            label="命名空间名称"
            rules={[
              { required: true, message: '请输入命名空间名称' },
              { pattern: /^[a-zA-Z0-9_-]+$/, message: '只能包含字母、数字、下划线和中划线' }
            ]}
          >
            <Input 
              placeholder="例如：production、dev-team-1" 
              disabled={!!editingNamespace}
            />
          </Form.Item>
          
          <Form.Item
            name="description"
            label="描述"
          >
            <Input.TextArea 
              placeholder="命名空间的描述信息（可选）" 
              rows={2}
            />
          </Form.Item>

          <Row gutter={24}>
            <Col span={12}>
              <Card 
                title={<Space><CloudServerOutlined /> Redis 配置</Space>} 
                size="small"
                style={{ marginBottom: 16 }}
              >
                <Form.Item
                  name="redis_host"
                  label="主机地址"
                  rules={[{ required: true, message: '请输入Redis主机地址' }]}
                >
                  <Input placeholder="localhost" />
                </Form.Item>
                <Form.Item
                  name="redis_port"
                  label="端口"
                  rules={[{ required: true, message: '请输入Redis端口' }]}
                >
                  <InputNumber min={1} max={65535} style={{ width: '100%' }} />
                </Form.Item>
                <Form.Item
                  name="redis_password"
                  label="密码"
                >
                  <Input.Password placeholder="可选" />
                </Form.Item>
                <Form.Item
                  name="redis_db"
                  label="数据库索引"
                >
                  <InputNumber min={0} max={15} style={{ width: '100%' }} />
                </Form.Item>
              </Card>
            </Col>
            
            <Col span={12}>
              <Card 
                title={<Space><DatabaseOutlined /> PostgreSQL 配置</Space>} 
                size="small"
                style={{ marginBottom: 16 }}
              >
                <Form.Item
                  name="pg_host"
                  label="主机地址"
                  rules={[{ required: true, message: '请输入PostgreSQL主机地址' }]}
                >
                  <Input placeholder="localhost" />
                </Form.Item>
                <Form.Item
                  name="pg_port"
                  label="端口"
                  rules={[{ required: true, message: '请输入PostgreSQL端口' }]}
                >
                  <InputNumber min={1} max={65535} style={{ width: '100%' }} />
                </Form.Item>
                <Form.Item
                  name="pg_user"
                  label="用户名"
                  rules={[{ required: true, message: '请输入用户名' }]}
                >
                  <Input placeholder="jettask" />
                </Form.Item>
                <Form.Item
                  name="pg_password"
                  label="密码"
                  rules={[{ required: true, message: '请输入密码' }]}
                >
                  <Input.Password />
                </Form.Item>
                <Form.Item
                  name="pg_database"
                  label="数据库名"
                  rules={[{ required: true, message: '请输入数据库名' }]}
                >
                  <Input placeholder="jettask" />
                </Form.Item>
              </Card>
            </Col>
          </Row>
        </Form>
      </Modal>

      {/* 查看命名空间详情的模态框 */}
      <Modal
        title={`命名空间详情 - ${selectedNamespace?.name}`}
        open={detailModalVisible}
        onCancel={() => {
          setDetailModalVisible(false);
          setSelectedNamespace(null);
        }}
        footer={null}
        width={800}
      >
        {selectedNamespace && (
          <div>
            <Descriptions bordered column={1} style={{ marginBottom: 24 }}>
              <Descriptions.Item label="命名空间名称">
                {selectedNamespace.name}
              </Descriptions.Item>
              <Descriptions.Item label="描述">
                {selectedNamespace.description || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="版本">
                <Tag color="blue">v{selectedNamespace.version || 1}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="连接URL">
                <Paragraph copyable={{ text: selectedNamespace.connection_url }}>
                  {selectedNamespace.connection_url}
                </Paragraph>
              </Descriptions.Item>
              <Descriptions.Item label="创建时间">
                {selectedNamespace.created_at ? new Date(selectedNamespace.created_at).toLocaleString() : '-'}
              </Descriptions.Item>
              <Descriptions.Item label="更新时间">
                {selectedNamespace.updated_at ? new Date(selectedNamespace.updated_at).toLocaleString() : '-'}
              </Descriptions.Item>
            </Descriptions>

            {selectedNamespace.config && (
              <>
                <Title level={5}>Redis 配置</Title>
                <Descriptions bordered size="small" style={{ marginBottom: 24 }}>
                  <Descriptions.Item label="主机" span={2}>
                    {selectedNamespace.config.redis_config?.host}
                  </Descriptions.Item>
                  <Descriptions.Item label="端口">
                    {selectedNamespace.config.redis_config?.port}
                  </Descriptions.Item>
                  <Descriptions.Item label="密码" span={2}>
                    {selectedNamespace.config.redis_config?.password ? '******' : '未设置'}
                  </Descriptions.Item>
                  <Descriptions.Item label="数据库">
                    {selectedNamespace.config.redis_config?.db || 0}
                  </Descriptions.Item>
                </Descriptions>

                <Title level={5}>PostgreSQL 配置</Title>
                <Descriptions bordered size="small">
                  <Descriptions.Item label="主机" span={2}>
                    {selectedNamespace.config.pg_config?.host}
                  </Descriptions.Item>
                  <Descriptions.Item label="端口">
                    {selectedNamespace.config.pg_config?.port}
                  </Descriptions.Item>
                  <Descriptions.Item label="用户名" span={2}>
                    {selectedNamespace.config.pg_config?.user}
                  </Descriptions.Item>
                  <Descriptions.Item label="数据库">
                    {selectedNamespace.config.pg_config?.database}
                  </Descriptions.Item>
                </Descriptions>
              </>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
}

export default Settings;