import { createContext, useContext, useState, useCallback, useEffect, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

const TabsContext = createContext();

export const useTabs = () => {
  const context = useContext(TabsContext);
  if (!context) {
    throw new Error('useTabs must be used within TabsProvider');
  }
  return context;
};

// 生成标签页的唯一ID
const generateTabId = (path, params = {}) => {
  // 对于队列详情页等需要区分不同参数的页面，将参数包含在ID中
  const paramStr = Object.keys(params).sort().map(key => `${key}=${params[key]}`).join('&');
  return paramStr ? `${path}?${paramStr}` : path;
};

// 获取页面标题
const getPageTitle = (path, params = {}) => {
  if (path === '/dashboard') return '概览';
  if (path === '/queues') return '队列';
  if (path === '/workers') return 'Workers';
  if (path === '/scheduled-tasks') return '定时任务';
  if (path === '/alerts') return '监控告警';
  if (path.startsWith('/queue/')) {
    const queueName = path.replace('/queue/', '');
    // 如果有scheduled_task_id参数，说明是从定时任务页面跳转过来的历史记录
    if (params.scheduled_task_id) {
      return `历史记录 (ID:${params.scheduled_task_id})`;
    }
    return `队列: ${decodeURIComponent(queueName)}`;
  }
  return '未知页面';
};

export const TabsProvider = ({ children }) => {
  const [tabs, setTabs] = useState([]);
  const [activeTabId, setActiveTabId] = useState(null);
  const [tabStates, setTabStates] = useState({}); // 保存每个标签页的状态
  const location = useLocation();
  const navigate = useNavigate();
  const isNavigatingRef = useRef(false); // 标记是否正在通过addOrActivateTab导航

  // 添加或激活标签页
  const addOrActivateTab = useCallback((path, title, params = {}, state = {}) => {
    const tabId = generateTabId(path, params);
    
    // 设置导航标记，防止useEffect重复创建标签页
    isNavigatingRef.current = true;
    
    setTabs(prevTabs => {
      const existingTab = prevTabs.find(tab => tab.id === tabId);
      
      if (existingTab) {
        // 标签页已存在，不需要创建新的
        return prevTabs;
      }
      
      // 创建新标签页
      const newTab = {
        id: tabId,
        path,
        title: title || getPageTitle(path, params),
        params,
        closable: true, // 除了某些页面外都可以关闭
      };
      
      // 限制最大标签页数量
      const maxTabs = 10;
      if (prevTabs.length >= maxTabs) {
        // 关闭最早的可关闭标签页
        const closableTab = prevTabs.find(tab => tab.closable);
        if (closableTab) {
              return [...prevTabs.filter(tab => tab.id !== closableTab.id), newTab];
        }
      }
      return [...prevTabs, newTab];
    });
    
    // 保存标签页状态
    if (state && Object.keys(state).length > 0) {
      setTabStates(prev => ({
        ...prev,
        [tabId]: state
      }));
    }
    // 无论标签页是否已存在，都激活并导航
    setActiveTabId(tabId);
    
    // 导航到新标签页的路径
    const fullPath = params && Object.keys(params).length > 0 
      ? `${path}?${new URLSearchParams(params).toString()}`
      : path;
    navigate(fullPath);
    
    // 导航完成后重置标记
    setTimeout(() => {
      isNavigatingRef.current = false;
    }, 100);
  }, [navigate]);

  // 关闭标签页
  const closeTab = useCallback((tabId, event) => {
    if (event) {
      event.stopPropagation();
    }
    
    setTabs(prevTabs => {
      const tabIndex = prevTabs.findIndex(tab => tab.id === tabId);
      const newTabs = prevTabs.filter(tab => tab.id !== tabId);
      
      // 如果关闭的是当前激活的标签页，需要切换到其他标签页
      if (tabId === activeTabId && newTabs.length > 0) {
        // 优先切换到右边的标签页，如果没有则切换到左边
        const newActiveTab = newTabs[Math.min(tabIndex, newTabs.length - 1)];
        setActiveTabId(newActiveTab.id);
        navigate(newActiveTab.path);
      }
      
      return newTabs;
    });
    
    // 清除标签页状态
    setTabStates(prev => {
      const newStates = { ...prev };
      delete newStates[tabId];
      return newStates;
    });
  }, [activeTabId, navigate]);

  // 切换标签页
  const switchTab = useCallback((tabId) => {
    const tab = tabs.find(t => t.id === tabId);
    if (tab) {
      setActiveTabId(tabId);
      navigate(tab.path);
    }
  }, [tabs, navigate]);

  // 保存当前标签页状态
  const saveTabState = useCallback((state) => {
    if (activeTabId) {
      setTabStates(prev => ({
        ...prev,
        [activeTabId]: {
          ...prev[activeTabId],
          ...state
        }
      }));
    }
  }, [activeTabId]);

  // 获取当前标签页状态
  const getTabState = useCallback(() => {
    return activeTabId ? (tabStates[activeTabId] || {}) : {};
  }, [activeTabId, tabStates]);

  // 关闭所有标签页
  const closeAllTabs = useCallback(() => {
    setTabs([]);
    setTabStates({});
    setActiveTabId(null);
  }, []);

  // 关闭其他标签页
  const closeOtherTabs = useCallback((tabId) => {
    const tab = tabs.find(t => t.id === tabId);
    if (tab) {
      setTabs([tab]);
      setTabStates(prev => ({
        [tabId]: prev[tabId]
      }));
      setActiveTabId(tabId);
    }
  }, [tabs]);

  // 监听路由变化
  useEffect(() => {
    // 如果是通过addOrActivateTab导航的，跳过处理
    if (isNavigatingRef.current) {
      return;
    }
    
    const path = location.pathname;
    const search = location.search;
    const params = Object.fromEntries(new URLSearchParams(search));
    
    // 生成标签页ID
    const tabId = generateTabId(path, params);
    const existingTab = tabs.find(tab => tab.id === tabId);
    
    if (!existingTab) {
      // 如果标签页不存在，创建新的（但不再调用navigate，因为已经在这个路径了）
      setTabs(prevTabs => {
        // 再次检查避免重复
        if (prevTabs.find(tab => tab.id === tabId)) {
          return prevTabs;
        }
        
        const newTab = {
          id: tabId,
          path,
          title: getPageTitle(path, params),
          params,
          closable: true,
        };
        
        const maxTabs = 10;
        if (prevTabs.length >= maxTabs) {
          const closableTab = prevTabs.find(tab => tab.closable);
          if (closableTab) {
            return [...prevTabs.filter(tab => tab.id !== closableTab.id), newTab];
          }
        }
        
        return [...prevTabs, newTab];
      });
      setActiveTabId(tabId);
    } else {
      // 如果标签页存在，激活它
      setActiveTabId(tabId);
    }
  }, [location, tabs]);

  const value = {
    tabs,
    activeTabId,
    addOrActivateTab,
    closeTab,
    switchTab,
    saveTabState,
    getTabState,
    closeAllTabs,
    closeOtherTabs,
  };

  return (
    <TabsContext.Provider value={value}>
      {children}
    </TabsContext.Provider>
  );
};