import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { ConfigProvider, theme } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import AppLayout from './components/layout/AppLayout'
import Dashboard from './pages/Dashboard'
import Queues from './pages/Queues'
import Workers from './pages/Workers'
import QueueDetail from './pages/QueueDetail'
import ScheduledTasks from './pages/ScheduledTasks'
import Alerts from './pages/Alerts'
import Settings from './pages/Settings'
import { LoadingProvider } from './contexts/LoadingContext'
import { NamespaceProvider } from './contexts/NamespaceContext'
import './App.css'

function App() {
  // 自定义主题
  const customTheme = {
    algorithm: theme.defaultAlgorithm,
    token: {
      colorPrimary: '#1890ff',
      borderRadius: 4,
      colorBgContainer: '#ffffff',
    },
    components: {
      Layout: {
        siderBg: '#1a1d21',
        headerBg: '#2a2d31',
      },
      Menu: {
        darkItemBg: 'transparent',
        darkItemSelectedBg: '#1890ff',
        darkItemHoverBg: 'rgba(24, 144, 255, 0.1)',
      },
    },
  }

  return (
    <ConfigProvider theme={customTheme} locale={zhCN}>
      <LoadingProvider>
        <NamespaceProvider>
          <Router>
            <Routes>
              <Route path="/" element={<AppLayout />}>
                <Route index element={<Navigate to="/dashboard" replace />} />
                <Route path="dashboard" element={<Dashboard />} />
                <Route path="queues" element={<Queues />} />
                <Route path="queue/:queueName" element={<QueueDetail />} />
                <Route path="scheduled-tasks" element={<ScheduledTasks />} />
                <Route path="alerts" element={<Alerts />} />
                {/* 新增路由 */}
                <Route path="analytics" element={<div style={{ padding: 24 }}>数据分析页面开发中...</div>} />
                <Route path="performance" element={<div style={{ padding: 24 }}>性能监控页面开发中...</div>} />
                <Route path="logs" element={<div style={{ padding: 24 }}>日志查询页面开发中...</div>} />
                <Route path="api-docs" element={<div style={{ padding: 24 }}>API文档页面开发中...</div>} />
                <Route path="settings" element={<Settings />} />
              </Route>
            </Routes>
          </Router>
        </NamespaceProvider>
      </LoadingProvider>
    </ConfigProvider>
  )
}

export default App