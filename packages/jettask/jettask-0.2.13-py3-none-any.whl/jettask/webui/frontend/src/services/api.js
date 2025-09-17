import axios from 'axios';

// 智能获取 API 基础 URL
const getApiBaseUrl = () => {
  // 优先使用注入的 API URL
  if (typeof window !== 'undefined' && window.JETTASK_API_URL !== undefined) {
    const url = window.JETTASK_API_URL;
    // 如果是空字符串，表示使用相对路径（代理模式）
    if (url === '') {
      return '';  // 使用相对路径，不加前缀
    }
    // 否则确保 URL 以 /api 结尾
    return url.endsWith('/api') ? url : `${url}/api`;
  }
  
  // 在开发环境中使用 localhost
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    const protocol = window.location.protocol;
    
    // 如果是生产环境，使用相同的域名
    if (hostname !== 'localhost' && hostname !== '127.0.0.1') {
      return `${protocol}//${hostname}:8001/api`;
    }
  }
  
  // 默认开发环境
  return 'http://localhost:8001/api';
};

// 智能获取 WebSocket URL
const getWsBaseUrl = () => {
  // 优先使用注入的 API URL
  if (typeof window !== 'undefined' && window.JETTASK_API_URL !== undefined) {
    const url = window.JETTASK_API_URL;
    // 如果是空字符串，使用相对路径
    if (url === '') {
      const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      return `${wsProtocol}//${window.location.host}/ws`;
    }
    // 将 http 转换为 ws，https 转换为 wss
    const wsUrl = url.replace(/^http/, 'ws');
    return wsUrl.endsWith('/ws') ? wsUrl : `${wsUrl}/ws`;
  }
  
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    
    // 如果是生产环境，使用相同的域名
    if (hostname !== 'localhost' && hostname !== '127.0.0.1') {
      return `${wsProtocol}//${hostname}:8001/ws`;
    }
  }
  
  // 默认开发环境
  return 'ws://localhost:8001/ws';
};

const API_BASE_URL = getApiBaseUrl();
const WS_BASE_URL = getWsBaseUrl();

// 设置 axios 全局默认配置
// 空字符串时不设置 baseURL，让 axios 使用相对路径
if (API_BASE_URL !== '') {
  axios.defaults.baseURL = API_BASE_URL;
}

// 创建 axios 实例
// 如果 baseURL 为空，设置一个请求拦截器来处理路径
const api = axios.create({
  baseURL: API_BASE_URL === '' ? undefined : API_BASE_URL,  // 空字符串时不设置 baseURL
  timeout: 10000,
});

// 如果是代理模式，确保路径正确
if (API_BASE_URL === '') {
  api.interceptors.request.use(config => {
    // 确保路径以 /api/ 开头
    if (!config.url.startsWith('/api/')) {
      config.url = '/api/' + config.url;
    }
    return config;
  });
}

// 导出配置好的实例和URLs
export { api, API_BASE_URL, WS_BASE_URL };

// 获取全局统计信息
export const fetchGlobalStats = async () => {
  try {
    const response = await api.get('stats');  // 不要前导斜杠，axios 会自动处理
    return response.data.data;
  } catch (error) {
    console.error('Failed to fetch global stats:', error);
    throw error;
  }
};

// 获取队列列表
export const fetchQueues = async () => {
  try {
    const response = await api.get('queues');  // 不要前导斜杠
    return response.data;
  } catch (error) {
    console.error('Failed to fetch queues:', error);
    throw error;
  }
};

// 获取队列时间线数据
export const fetchQueueTimeline = async (params) => {
  try {
    // 从参数中提取命名空间，如果没有则使用 default
    const namespace = params.namespace || 'default';
    const response = await api.post(`queue-timeline/${namespace}`, params);  // 不要前导斜杠
    // 处理数据，确保不包含填充的空值
    const data = response.data.data || response.data || [];
    return {
      ...response.data,
      data: data.filter(item => item.value > 0) // 只返回有实际值的数据点
    };
  } catch (error) {
    console.error('Failed to fetch queue timeline:', error);
    throw error;
  }
};

// WebSocket 连接
export const connectWebSocket = (onMessage, onError) => {
  const ws = new WebSocket(`${WS_BASE_URL}/monitor`);
  
  ws.onopen = () => {
    console.log('WebSocket connected');
  };
  
  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data);
    } catch (error) {
      console.error('Failed to parse WebSocket message:', error);
    }
  };
  
  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
    if (onError) onError(error);
  };
  
  ws.onclose = () => {
    console.log('WebSocket disconnected');
  };
  
  return ws;
};

export default api;