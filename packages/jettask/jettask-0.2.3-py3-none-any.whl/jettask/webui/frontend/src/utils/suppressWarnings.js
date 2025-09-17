// 在开发环境中临时屏蔽特定的控制台警告
// 注意：这只是为了减少开发时的控制台噪音，不影响实际功能

if (process.env.NODE_ENV === 'development') {
  const originalWarning = console.warn;
  console.warn = (...args) => {
    const warningMessage = args[0]?.toString() || '';
    
    // 屏蔽 findDOMNode 相关警告（来自第三方库）
    if (warningMessage.includes('findDOMNode')) {
      return;
    }
    
    // 屏蔽 React Router v7 迁移提示
    if (warningMessage.includes('React Router Future Flag Warning')) {
      return;
    }
    
    // 其他警告正常显示
    originalWarning.apply(console, args);
  };
}