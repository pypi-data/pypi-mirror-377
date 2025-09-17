import React from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { Layout, Menu } from 'antd'
import { 
  DashboardOutlined, 
  AppstoreOutlined, 
  TeamOutlined,
  RocketOutlined,
  LoadingOutlined,
  ClockCircleOutlined,
  AlertOutlined,
  CloudServerOutlined
} from '@ant-design/icons'
import { useLoading } from '../../contexts/LoadingContext'
import { useNamespace } from '../../contexts/NamespaceContext'
import NamespaceSelector from '../NamespaceSelector'
import './Header.css'

const { Header: AntHeader } = Layout

const Header = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { isLoading } = useLoading()
  const { currentNamespace, setCurrentNamespace } = useNamespace()

  const menuItems = [
    {
      key: '/dashboard',
      icon: <DashboardOutlined />,
      label: '概览',
    },
    {
      key: '/queues',
      icon: <AppstoreOutlined />,
      label: '队列',
    },
    // {
    //   key: '/workers',
    //   icon: <TeamOutlined />,
    //   label: 'Workers',
    // },
    {
      key: '/scheduled-tasks',
      icon: <ClockCircleOutlined />,
      label: '定时任务',
    },
    {
      key: '/alerts',
      icon: <AlertOutlined />,
      label: '监控告警',
    },
  ]

  const handleMenuClick = ({ key }) => {
    navigate(key)
  }

  return (
    <AntHeader className="app-header">
      <div className="header-container">
        <div className="header-left">
          <div className="app-logo">
            {isLoading ? (
              <LoadingOutlined 
                className="logo-icon"
                style={{ 
                  fontSize: 18,
                  color: '#1890ff'
                }} 
                spin 
              />
            ) : (
              <RocketOutlined className="logo-icon" />
            )}
            <span className="logo-text">JetTask Monitor</span>
          </div>
        </div>
        
        <div className="header-center">
          <Menu
            mode="horizontal"
            selectedKeys={[location.pathname]}
            items={menuItems}
            onClick={handleMenuClick}
            className="header-menu"
          />
        </div>
        
        <div className="header-right">
          <NamespaceSelector 
            value={currentNamespace}
            onChange={(namespace) => {
              console.log('🔧 Header收到命名空间切换:', namespace);
              setCurrentNamespace(namespace);
            }}
            style={{ marginLeft: 'auto' }}
          />
        </div>
        
      </div>
    </AntHeader>
  )
}

export default Header