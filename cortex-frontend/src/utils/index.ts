import { TaskStatusConfig, TaskPriorityConfig, TaskPriority } from '../constants';

/**
 * 根据状态获取配置
 */
export const getStatusConfig = (status: string) => {
  return TaskStatusConfig[status as keyof typeof TaskStatusConfig] || { text: status, color: 'default' };
};

/**
 * 根据状态获取颜色
 */
export const getStatusColor = (status: string) => {
  return getStatusConfig(status).color;
};

/**
 * 根据状态获取文本
 */
export const getStatusText = (status: string) => {
  return getStatusConfig(status).text;
};

/**
 * 根据优先级获取配置
 */
export const getPriorityConfig = (priority?: string) => {
  const normalizedPriority = priority?.toUpperCase() as TaskPriority;
  return TaskPriorityConfig[normalizedPriority] || { text: priority || '中', color: 'default' };
};

/**
 * 根据优先级获取颜色
 */
export const getPriorityColor = (priority?: string) => {
  return getPriorityConfig(priority).color;
};

/**
 * 根据优先级获取文本
 */
export const getPriorityText = (priority?: string) => {
  return getPriorityConfig(priority).text;
};

/**
 * 格式化日期
 */
export const formatDate = (dateString?: string) => {
  if (!dateString) return '-';
  try {
    return new Date(dateString).toLocaleDateString('zh-CN');
  } catch {
    return dateString;
  }
};

/**
 * 格式化日期时间
 */
export const formatDateTime = (dateString?: string) => {
  if (!dateString) return '-';
  try {
    return new Date(dateString).toLocaleString('zh-CN');
  } catch {
    return dateString;
  }
};

/**
 * 格式化任务ID显示
 */
export const formatTaskId = (id: number) => `#${id}`;
