/**
 * 命名空间上下文
 * 用于全局管理当前选中的命名空间
 */
import React, { createContext, useState, useContext, useEffect } from 'react';

const NamespaceContext = createContext();

export const useNamespace = () => {
  const context = useContext(NamespaceContext);
  if (!context) {
    throw new Error('useNamespace must be used within NamespaceProvider');
  }
  return context;
};

export const NamespaceProvider = ({ children }) => {
  // 从localStorage读取上次选择的命名空间
  const [currentNamespace, setCurrentNamespaceState] = useState(() => {
    const saved = localStorage.getItem('selectedNamespace');
    console.log('🔧 NamespaceContext初始化，从localStorage读取:', saved);
    return saved || 'default'; // 默认使用default命名空间
  });

  // 添加一个刷新触发器状态
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  // 当命名空间改变时，保存到localStorage
  useEffect(() => {
    console.log('🔧 NamespaceContext命名空间变化:', currentNamespace);
    if (currentNamespace) {
      localStorage.setItem('selectedNamespace', currentNamespace);
    }
  }, [currentNamespace]);

  const setCurrentNamespace = (namespace) => {
    console.log('🔧 NamespaceContext.setCurrentNamespace被调用:', namespace);
    console.log('🔧 当前值:', currentNamespace);
    setCurrentNamespaceState(namespace);
  };

  // 添加刷新命名空间列表的方法
  const refreshNamespaceList = () => {
    console.log('🔧 NamespaceContext.refreshNamespaceList被调用');
    setRefreshTrigger(prev => prev + 1);
  };

  const value = {
    currentNamespace,
    setCurrentNamespace,
    refreshTrigger,  // 暴露刷新触发器
    refreshNamespaceList,  // 暴露刷新方法
    // 辅助方法：构建带命名空间的API URL
    getApiUrl: (path) => {
      if (!currentNamespace) {
        throw new Error('No namespace selected');
      }
      // 如果路径中包含{namespace}占位符，替换它
      if (path.includes('{namespace}')) {
        return path.replace('{namespace}', currentNamespace);
      }
      // 否则在路径前添加命名空间
      return `/api/data/${currentNamespace}${path}`;
    }
  };

  return (
    <NamespaceContext.Provider value={value}>
      {children}
    </NamespaceContext.Provider>
  );
};