/**
 * 用户偏好设置管理工具
 */

const STORAGE_KEY = 'jettask_user_preferences';

/**
 * 获取用户偏好设置
 * @returns {Object} 用户偏好设置对象
 */
export const getUserPreferences = () => {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored ? JSON.parse(stored) : {};
  } catch (error) {
    console.error('Failed to load user preferences:', error);
    return {};
  }
};

/**
 * 保存用户偏好设置
 * @param {Object} preferences - 偏好设置对象
 */
export const saveUserPreferences = (preferences) => {
  try {
    const current = getUserPreferences();
    console.log('[saveUserPreferences] 当前值:', current);
    console.log('[saveUserPreferences] 要更新的值:', preferences);
    const updated = { ...current, ...preferences };
    console.log('[saveUserPreferences] 合并后的值:', updated);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
    console.log('[saveUserPreferences] 已保存到 localStorage');
  } catch (error) {
    console.error('Failed to save user preferences:', error);
  }
};

/**
 * 获取特定的偏好设置
 * @param {string} key - 设置项的键
 * @param {*} defaultValue - 默认值
 * @returns {*} 设置值
 */
export const getPreference = (key, defaultValue = null) => {
  const preferences = getUserPreferences();
  return preferences[key] !== undefined ? preferences[key] : defaultValue;
};

/**
 * 保存特定的偏好设置
 * @param {string} key - 设置项的键
 * @param {*} value - 设置值
 */
export const setPreference = (key, value) => {
  console.log('[setPreference] 保存偏好设置 - key:', key, 'value:', value);
  saveUserPreferences({ [key]: value });
  // 立即验证保存
  const saved = getUserPreferences();
  console.log('[setPreference] 保存后立即验证 - saved[key]:', saved[key]);
};

/**
 * 清除所有偏好设置
 */
export const clearPreferences = () => {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch (error) {
    console.error('Failed to clear user preferences:', error);
  }
};

// 偏好设置的键
export const PREFERENCE_KEYS = {
  QUEUE_MONITOR_TIME_RANGE: 'queueMonitor.timeRange',
  QUEUE_MONITOR_SELECTED_QUEUES: 'queueMonitor.selectedQueues',
  QUEUE_MONITOR_CUSTOM_TIME_RANGE: 'queueMonitor.customTimeRange',
  QUEUE_DETAILS_PAGE_SIZE: 'queueDetails.pageSize',
};

/**
 * 获取队列特定的筛选条件
 * @param {string} queueName - 队列名称
 * @returns {Object} 队列的筛选设置
 */
export const getQueueFilters = (queueName) => {
  const key = `queue.${queueName}.filters`;
  const preferences = getUserPreferences();
  const queueSettings = preferences[key] || {};
  
  // 返回默认结构
  return {
    filters: queueSettings.filters || [],
    timeRange: queueSettings.timeRange || '1h',
    customTimeRange: queueSettings.customTimeRange || null
  };
};

/**
 * 保存队列特定的筛选条件
 * @param {string} queueName - 队列名称
 * @param {Object} settings - 筛选设置
 */
export const saveQueueFilters = (queueName, settings) => {
  const key = `queue.${queueName}.filters`;
  const currentPrefs = getUserPreferences();
  
  // 限制存储的队列数量，防止localStorage过大
  const queueKeys = Object.keys(currentPrefs).filter(k => k.startsWith('queue.'));
  if (queueKeys.length > 50) {
    // 删除最旧的队列设置（简单策略：删除第一个）
    delete currentPrefs[queueKeys[0]];
  }
  
  // 保存新的设置
  currentPrefs[key] = {
    filters: settings.filters || [],
    timeRange: settings.timeRange || '1h',
    customTimeRange: settings.customTimeRange || null,
    lastUpdated: new Date().toISOString()
  };
  
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(currentPrefs));
  } catch (error) {
    console.error('Failed to save queue filters:', error);
    // 如果存储失败（可能是容量问题），清理旧数据
    if (error.name === 'QuotaExceededError') {
      // 清理最旧的一半队列设置
      const halfLength = Math.floor(queueKeys.length / 2);
      for (let i = 0; i < halfLength; i++) {
        delete currentPrefs[queueKeys[i]];
      }
      // 重试保存
      localStorage.setItem(STORAGE_KEY, JSON.stringify(currentPrefs));
    }
  }
};

/**
 * 清除特定队列的筛选设置
 * @param {string} queueName - 队列名称
 */
export const clearQueueFilters = (queueName) => {
  const key = `queue.${queueName}.filters`;
  const currentPrefs = getUserPreferences();
  delete currentPrefs[key];
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(currentPrefs));
  } catch (error) {
    console.error('Failed to clear queue filters:', error);
  }
};