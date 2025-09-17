/**
 * 命名空间选择器组件
 * 放置在页面顶部，用于切换不同的命名空间
 */
import React, { useState, useEffect } from 'react';
import { Select, Space, Tag, Tooltip, message, Button, Dropdown, Modal } from 'antd';
import { DatabaseOutlined, CloudServerOutlined, SettingOutlined, PlusOutlined, EditOutlined, ExclamationCircleOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useNamespace } from '../contexts/NamespaceContext';

const { Option } = Select;

const NamespaceSelector = ({ value, onChange, style }) => {
  const [namespaces, setNamespaces] = useState([]);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { refreshTrigger } = useNamespace();  // 获取刷新触发器

  // 获取命名空间列表
  const fetchNamespaces = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/data/namespaces');
      if (response.ok) {
        const data = await response.json();
        setNamespaces(data);
        
        // 如果没有选中的命名空间，默认选中第一个
        if (!value && data.length > 0) {
          const firstNamespace = data[0].name;
          if (onChange) {
            onChange(firstNamespace);
          }
        } else if (data.length === 0) {
          // 如果没有任何命名空间，弹出提示并引导到管理页面
          showNoNamespaceModal();
        }
      } else {
        message.error('获取命名空间列表失败');
      }
    } catch (error) {
      console.error('获取命名空间失败:', error);
      message.error('连接任务中心失败');
    } finally {
      setLoading(false);
    }
  };

  // 组件挂载时获取命名空间列表，以及当refreshTrigger变化时刷新
  useEffect(() => {
    fetchNamespaces();
  }, [refreshTrigger]);  // 监听刷新触发器而不是value

  // 处理命名空间切换
  const handleNamespaceChange = (namespaceName) => {
    console.log('🔧 NamespaceSelector切换命名空间:', namespaceName);
    console.log('🔧 当前props.value:', value);
    console.log('🔧 onChange函数存在:', !!onChange);
    
    if (onChange) {
      onChange(namespaceName);
      console.log('🔧 已调用onChange函数');
    }
    message.success(`已切换到命名空间: ${namespaceName}`);
  };

  // 显示无命名空间提示弹窗
  const showNoNamespaceModal = () => {
    Modal.confirm({
      title: '暂无可用命名空间',
      icon: <ExclamationCircleOutlined />,
      content: '当前系统中没有配置任何命名空间，请先创建一个命名空间。',
      okText: '去管理命名空间',
      cancelText: '取消',
      onOk: () => {
        navigate('/settings');
      },
    });
  };

  // 获取命名空间标签颜色
  const getNamespaceTagColor = (name) => {
    if (name === 'default') return 'blue';
    if (name.includes('test')) return 'orange';
    if (name.includes('prod')) return 'green';
    if (name.includes('dev')) return 'purple';
    return 'default';
  };


  return (
    <Space style={{ ...style }}>
      <span style={{ color: 'rgba(255, 255, 255, 0.65)', fontSize: '14px' }}>
        <DatabaseOutlined style={{ marginRight: '6px' }} />
        命名空间:
      </span>
      
      <Select
        value={value}
        onChange={handleNamespaceChange}
        loading={loading}
        style={{ minWidth: 200 }}
        placeholder="请选择命名空间"
        showSearch
        optionFilterProp="children"
        filterOption={(input, option) =>
          option.children.props.children[1]?.toLowerCase().includes(input.toLowerCase())
        }
        dropdownRender={(menu) => (
          <>
            {menu}
            <div 
              style={{ 
                padding: '8px 12px', 
                textAlign: 'center', 
                borderTop: '1px solid #f0f0f0',
                cursor: 'pointer'
              }}
              onClick={(e) => {
                e.stopPropagation();
                e.preventDefault();
                console.log('🔧 点击管理命名空间区域');
                navigate('/settings');
              }}
            >
              <SettingOutlined style={{ marginRight: 4 }} />
              管理命名空间
            </div>
          </>
        )}
      >
        {namespaces.map(ns => (
          <Option key={ns.name} value={ns.name}>
            <Space>
              <Tag color={getNamespaceTagColor(ns.name)} style={{ margin: 0 }}>
                {ns.name}
              </Tag>
              {ns.description && (
                <Tooltip title={ns.description}>
                  <span style={{ color: '#999', fontSize: '12px' }}>
                    {ns.description.length > 20 
                      ? `${ns.description.substring(0, 20)}...` 
                      : ns.description}
                  </span>
                </Tooltip>
              )}
            </Space>
          </Option>
        ))}
      </Select>

      {value && (
        <Tooltip title={`当前命名空间: ${value}`}>
          <CloudServerOutlined 
            style={{ 
              color: '#52c41a', 
              fontSize: '16px'
            }} 
          />
        </Tooltip>
      )}
    </Space>
  );
};

export default NamespaceSelector;