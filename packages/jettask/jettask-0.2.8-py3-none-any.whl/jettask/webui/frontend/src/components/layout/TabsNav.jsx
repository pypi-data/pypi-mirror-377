import React, { useState, useEffect } from 'react';
import { Tabs, Dropdown, Menu } from 'antd';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  CloseOutlined,
  ReloadOutlined,
  CloseCircleOutlined,
  VerticalRightOutlined,
  VerticalLeftOutlined,
  HomeOutlined
} from '@ant-design/icons';
import './TabsNav.css';

const TabsNav = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [activeKey, setActiveKey] = useState('/dashboard');
  const [tabs, setTabs] = useState([
    {
      key: '/dashboard',
      label: '概览',
      closable: false,
    }
  ]);

  // 路由与标签映射
  const routeToTab = {
    '/dashboard': { label: '概览', closable: false },
    '/queues': { label: '任务队列', closable: true },
    '/scheduled-tasks': { label: '定时任务', closable: true },
    '/alerts': { label: '监控告警', closable: true },
    '/analytics': { label: '数据分析', closable: true },
    '/performance': { label: '性能监控', closable: true },
    '/logs': { label: '日志查询', closable: true },
    '/api-docs': { label: 'API文档', closable: true },
    '/settings': { label: '系统设置', closable: true },
  };

  // 动态路由处理（如队列详情页）
  const getDynamicTabInfo = (pathname) => {
    if (pathname.startsWith('/queue/')) {
      const queueName = pathname.split('/queue/')[1];
      return {
        label: `队列: ${decodeURIComponent(queueName)}`,
        closable: true,
      };
    }
    return null;
  };

  useEffect(() => {
    const pathname = location.pathname;
    
    // 使用函数式更新来避免依赖 tabs 状态
    setTabs(prevTabs => {
      // 检查是否已存在该标签
      const existingTab = prevTabs.find(tab => tab.key === pathname);
      
      if (!existingTab) {
        // 获取标签信息
        let tabInfo = routeToTab[pathname] || getDynamicTabInfo(pathname);
        
        if (tabInfo) {
          const newTab = {
            key: pathname,
            ...tabInfo,
          };
          return [...prevTabs, newTab];
        }
      }
      
      return prevTabs;
    });
    
    setActiveKey(pathname);
  }, [location.pathname]);

  const handleTabChange = (key) => {
    setActiveKey(key);
    navigate(key);
  };

  const handleTabEdit = (targetKey, action) => {
    if (action === 'remove') {
      removeTab(targetKey);
    }
  };

  const removeTab = (targetKey) => {
    const targetIndex = tabs.findIndex(tab => tab.key === targetKey);
    const newTabs = tabs.filter(tab => tab.key !== targetKey);
    
    if (newTabs.length && targetKey === activeKey) {
      // 如果关闭的是当前标签，切换到相邻标签
      const newActiveKey = targetIndex === 0 
        ? newTabs[0].key 
        : newTabs[targetIndex - 1].key;
      setActiveKey(newActiveKey);
      navigate(newActiveKey);
    }
    
    setTabs(newTabs);
  };

  const handleRefresh = () => {
    window.location.reload();
  };

  const handleCloseAll = () => {
    const homeTabs = tabs.filter(tab => !tab.closable);
    setTabs(homeTabs);
    setActiveKey('/dashboard');
    navigate('/dashboard');
  };

  const handleCloseOthers = () => {
    const currentTab = tabs.find(tab => tab.key === activeKey);
    const homeTabs = tabs.filter(tab => !tab.closable);
    const newTabs = currentTab?.closable 
      ? [...homeTabs, currentTab]
      : homeTabs;
    setTabs(newTabs);
  };

  const handleCloseLeft = () => {
    const currentIndex = tabs.findIndex(tab => tab.key === activeKey);
    const rightTabs = tabs.slice(currentIndex);
    const homeTabs = tabs.filter(tab => !tab.closable && tabs.indexOf(tab) < currentIndex);
    setTabs([...homeTabs, ...rightTabs]);
  };

  const handleCloseRight = () => {
    const currentIndex = tabs.findIndex(tab => tab.key === activeKey);
    const leftTabs = tabs.slice(0, currentIndex + 1);
    setTabs(leftTabs);
  };

  const contextMenu = (
    <Menu
      items={[
        {
          key: 'refresh',
          icon: <ReloadOutlined />,
          label: '刷新当前',
          onClick: handleRefresh,
        },
        {
          type: 'divider',
        },
        {
          key: 'closeOthers',
          icon: <CloseCircleOutlined />,
          label: '关闭其他',
          onClick: handleCloseOthers,
        },
        {
          key: 'closeLeft',
          icon: <VerticalRightOutlined />,
          label: '关闭左侧',
          onClick: handleCloseLeft,
        },
        {
          key: 'closeRight',
          icon: <VerticalLeftOutlined />,
          label: '关闭右侧',
          onClick: handleCloseRight,
        },
        {
          key: 'closeAll',
          icon: <CloseOutlined />,
          label: '关闭所有',
          onClick: handleCloseAll,
        },
      ]}
    />
  );

  const tabItems = tabs.map(tab => ({
    key: tab.key,
    label: (
      <Dropdown overlay={contextMenu} trigger={['contextMenu']} >
        <span className={`tab-label ${tab.key === '/dashboard' ? 'tab-label-center' : ''}`} >
          {tab.label}
        </span>
      </Dropdown>
    ),
    closable: tab.closable,
  }));

  return (
    <div className="tabs-nav-container">
      <Tabs
        type="editable-card"
        hideAdd
        activeKey={activeKey}
        onChange={handleTabChange}
        onEdit={handleTabEdit}
        items={tabItems}
        className="tabs-nav"
        size="small"
      />
    </div>
  );
};

export default TabsNav;