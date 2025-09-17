import React, { useState, useEffect } from 'react';
import { Layout, Menu, Tooltip } from 'antd';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  DashboardOutlined,
  AppstoreOutlined,
  ClockCircleOutlined,
  AlertOutlined,
  SettingOutlined,
  DatabaseOutlined,
  BarChartOutlined,
  TeamOutlined,
  CloudServerOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  FundOutlined,
  FileTextOutlined,
  SafetyOutlined,
  ApiOutlined
} from '@ant-design/icons';
import './SideMenu.css';

const { Sider } = Layout;

const SideMenu = ({ onMenuClick }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [collapsed, setCollapsed] = useState(false);
  const [selectedKeys, setSelectedKeys] = useState([]);

  const menuItems = [
    {
      key: 'dashboard',
      icon: <DashboardOutlined />,
      label: '概览',
      shortLabel: '概览',
      path: '/dashboard',
    },
    {
      key: 'queues',
      icon: <AppstoreOutlined />,
      label: '任务队列',
      shortLabel: '队列',
      path: '/queues',
    },
    {
      key: 'scheduled-tasks',
      icon: <ClockCircleOutlined />,
      label: '定时任务',
      shortLabel: '定时',
      path: '/scheduled-tasks',
    },
    {
      key: 'alerts',
      icon: <AlertOutlined />,
      label: '监控告警',
      shortLabel: '告警',
      path: '/alerts',
    },
    {
      key: 'analytics',
      icon: <BarChartOutlined />,
      label: '数据分析',
      shortLabel: '分析',
      path: '/analytics',
    },
    // {
    //   key: 'performance',
    //   icon: <FundOutlined />,
    //   label: '性能监控',
    //   shortLabel: '性能',
    //   path: '/performance',
    // },
    // {
    //   key: 'logs',
    //   icon: <FileTextOutlined />,
    //   label: '日志查询',
    //   shortLabel: '日志',
    //   path: '/logs',
    // },
    {
      key: 'divider2',
      type: 'divider',
    },
    {
      key: 'api-docs',
      icon: <ApiOutlined />,
      label: 'API文档',
      shortLabel: 'API',
      path: '/api-docs',
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: '系统设置',
      shortLabel: '设置',
      path: '/settings',
    },
  ];

  useEffect(() => {
    const currentItem = menuItems.find(item => item.path === location.pathname);
    if (currentItem) {
      setSelectedKeys([currentItem.key]);
    }
  }, [location.pathname]);

  const handleMenuClick = ({ key }) => {
    // 查找菜单项（包括子菜单项）
    let targetItem = null;
    for (const item of menuItems) {
      if (item.key === key) {
        targetItem = item;
        break;
      }
      if (item.children) {
        const childItem = item.children.find(child => child.key === key);
        if (childItem) {
          targetItem = childItem;
          break;
        }
      }
    }
    
    if (targetItem && targetItem.path) {
      navigate(targetItem.path);
      if (onMenuClick) {
        onMenuClick(targetItem);
      }
    }
  };

  return (
    <Sider
      trigger={null}
      collapsible
      collapsed={false}
      className="app-sider"
      width={64}
      style={{
        background: '#1a1d21',
        borderRight: '1px solid #303030',
      }}
    >
      <div className="sider-header">
        <div className="logo-container">
          <span className="logo-icon">A</span>
        </div>
      </div>
      
      <Menu
        mode="inline"
        selectedKeys={selectedKeys}
        onClick={handleMenuClick}
        className="side-menu compact"
        style={{
          background: 'transparent',
          borderRight: 0,
        }}
        items={menuItems.map(item => {
          if (item.type === 'divider') {
            return {
              type: 'divider',
              style: { margin: '8px 0', borderColor: '#303030' }
            };
          }
          
          // 如果有子菜单项
          if (item.children) {
            return {
              key: item.key,
              label: (
                <Tooltip placement="right" title={item.label}>
                  <div className="menu-item-content">
                    <div className="menu-icon-wrapper">
                      {item.icon}
                    </div>
                    <span className="menu-label">{item.shortLabel}</span>
                  </div>
                </Tooltip>
              ),
              children: item.children.map(child => ({
                key: child.key,
                label: child.label,
                icon: child.icon,
              }))
            };
          }
          
          return {
            key: item.key,
            label: (
              <Tooltip placement="right" title={item.label}>
                <div className="menu-item-content">
                  <div className="menu-icon-wrapper">
                    {item.icon}
                  </div>
                  <span className="menu-label">{item.shortLabel}</span>
                </div>
              </Tooltip>
            ),
          };
        })}
      />
    </Sider>
  );
};

export default SideMenu;