import React, { useState } from 'react';
import { Layout } from 'antd';
import { Outlet } from 'react-router-dom';
import SideMenu from './SideMenu';
import TabsNav from './TabsNav';
import UserInfo from './UserInfo';
import NamespaceSelector from '../NamespaceSelector';
import { useNamespace } from '../../contexts/NamespaceContext';
import './AppLayout.css';

const { Header, Content } = Layout;

const AppLayout = () => {
  const { currentNamespace, setCurrentNamespace } = useNamespace();
  
  console.log('🔧 AppLayout渲染，currentNamespace:', currentNamespace);
  console.log('🔧 AppLayout渲染，setCurrentNamespace:', typeof setCurrentNamespace);
  
  return (
    <Layout className="app-layout">
      {/* 左侧菜单 */}
      <SideMenu />
      
      {/* 右侧主体 */}
      <Layout className="main-layout" style={{ marginLeft: 64 }}>
        {/* 顶部导航栏 */}
        <Header className="app-header">
          <div className="header-left">
            <TabsNav />
          </div>
          <div className="header-right">
            <NamespaceSelector 
              value={currentNamespace}
              onChange={setCurrentNamespace}
            />
            <UserInfo />
          </div>
        </Header>
        
        {/* 内容区域 */}
        <Content className="app-content">
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
};

export default AppLayout;