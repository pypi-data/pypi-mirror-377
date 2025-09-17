import React, { useState } from 'react';
import { Dropdown, Menu, Avatar, Badge, Space, Button, Modal, Tooltip } from 'antd';
import {
  UserOutlined,
  BellOutlined,
  SettingOutlined,
  LogoutOutlined,
  QuestionCircleOutlined,
  InfoCircleOutlined,
  LockOutlined,
  GlobalOutlined,
  SkinOutlined,
  FullscreenOutlined,
  FullscreenExitOutlined,
  GithubOutlined,
  FileTextOutlined,
} from '@ant-design/icons';
import './UserInfo.css';

const UserInfo = () => {
  const [fullscreen, setFullscreen] = useState(false);
  const [notifications, setNotifications] = useState([
    { id: 1, title: '任务执行失败', description: '队列 payment_queue 有5个任务执行失败', time: '5分钟前', read: false },
    { id: 2, title: '系统性能警告', description: 'CPU使用率超过80%', time: '10分钟前', read: false },
    { id: 3, title: '定时任务完成', description: '数据备份任务已完成', time: '1小时前', read: true },
  ]);

  const unreadCount = notifications.filter(n => !n.read).length;

  const handleFullscreen = () => {
    if (!fullscreen) {
      document.documentElement.requestFullscreen();
    } else {
      document.exitFullscreen();
    }
    setFullscreen(!fullscreen);
  };

  const handleLogout = () => {
    Modal.confirm({
      title: '确认退出',
      content: '您确定要退出系统吗？',
      okText: '确定',
      cancelText: '取消',
      onOk: () => {
        // 这里处理退出逻辑
        console.log('Logout');
      },
    });
  };

  const handleMarkAllRead = () => {
    setNotifications(notifications.map(n => ({ ...n, read: true })));
  };

  const handleClearAll = () => {
    setNotifications([]);
  };

  const userMenu = (
    <Menu className="user-dropdown-menu">
      <Menu.Item key="profile" icon={<UserOutlined />}>
        个人中心
      </Menu.Item>
      <Menu.Item key="password" icon={<LockOutlined />}>
        修改密码
      </Menu.Item>
      <Menu.Item key="settings" icon={<SettingOutlined />}>
        个人设置
      </Menu.Item>
      <Menu.Divider />
      <Menu.Item key="theme" icon={<SkinOutlined />}>
        <Space>
          主题设置
          <span className="theme-badge">深色</span>
        </Space>
      </Menu.Item>
      <Menu.Item key="language" icon={<GlobalOutlined />}>
        <Space>
          语言
          <span className="language-badge">中文</span>
        </Space>
      </Menu.Item>
      <Menu.Divider />
      <Menu.Item key="logout" icon={<LogoutOutlined />} onClick={handleLogout}>
        退出登录
      </Menu.Item>
    </Menu>
  );

  const notificationMenu = (
    <div className="notification-dropdown">
      <div className="notification-header">
        <span>通知</span>
        <Space>
          <Button type="link" size="small" onClick={handleMarkAllRead}>
            全部已读
          </Button>
          <Button type="link" size="small" onClick={handleClearAll}>
            清空
          </Button>
        </Space>
      </div>
      <Menu className="notification-menu">
        {notifications.length > 0 ? (
          notifications.map(notification => (
            <Menu.Item key={notification.id} className={notification.read ? 'read' : 'unread'}>
              <div className="notification-item">
                <div className="notification-title">{notification.title}</div>
                <div className="notification-description">{notification.description}</div>
                <div className="notification-time">{notification.time}</div>
              </div>
            </Menu.Item>
          ))
        ) : (
          <div className="empty-notification">暂无通知</div>
        )}
      </Menu>
      <div className="notification-footer">
        <Button type="link" size="small">查看更多</Button>
      </div>
    </div>
  );

  const helpMenu = (
    <Menu className="help-dropdown-menu">
      <Menu.Item key="docs" icon={<FileTextOutlined />}>
        使用文档
      </Menu.Item>
      <Menu.Item key="api" icon={<InfoCircleOutlined />}>
        API文档
      </Menu.Item>
      <Menu.Item key="github" icon={<GithubOutlined />}>
        GitHub
      </Menu.Item>
      <Menu.Divider />
      <Menu.Item key="about" icon={<InfoCircleOutlined />}>
        关于系统
      </Menu.Item>
    </Menu>
  );

  return (
    <div className="user-info-container">
      <Space size={16}>
        {/* 全屏按钮 */}
        <Tooltip title={fullscreen ? '退出全屏' : '全屏'}>
          <Button
            type="text"
            icon={fullscreen ? <FullscreenExitOutlined /> : <FullscreenOutlined />}
            onClick={handleFullscreen}
            className="header-icon-btn"
          />
        </Tooltip>

        {/* 帮助菜单 */}
        <Dropdown overlay={helpMenu} placement="bottomRight" arrow>
          <Button
            type="text"
            icon={<QuestionCircleOutlined />}
            className="header-icon-btn"
          />
        </Dropdown>

        {/* 通知中心 */}
        <Dropdown 
          overlay={notificationMenu} 
          placement="bottomRight" 
          trigger={['click']}
          overlayClassName="notification-dropdown-container"
        >
          <Badge count={unreadCount} size="small">
            <Button
              type="text"
              icon={<BellOutlined />}
              className="header-icon-btn"
            />
          </Badge>
        </Dropdown>

        {/* 用户信息 */}
        <Dropdown overlay={userMenu} placement="bottomRight" arrow>
          <div className="user-avatar-container">
            <Avatar
              size={32}
              icon={<UserOutlined />}
              style={{ backgroundColor: '#1890ff' }}
            />
            <span className="username">管理员</span>
          </div>
        </Dropdown>
      </Space>
    </div>
  );
};

export default UserInfo;