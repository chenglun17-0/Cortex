// 状态配置
export const TaskStatus = {
  TODO: 'TODO',
  IN_PROGRESS: 'IN_PROGRESS',
  REVIEW: 'REVIEW',
  DONE: 'DONE',
} as const;

export type TaskStatus = (typeof TaskStatus)[keyof typeof TaskStatus];

export const TaskStatusConfig = {
  [TaskStatus.TODO]: { text: '待处理', color: 'default' },
  [TaskStatus.IN_PROGRESS]: { text: '进行中', color: 'processing' },
  [TaskStatus.REVIEW]: { text: '待审核', color: 'warning' },
  [TaskStatus.DONE]: { text: '已完成', color: 'success' },
} as const;

// 优先级配置
export const TaskPriority = {
  HIGH: 'HIGH',
  MEDIUM: 'MEDIUM',
  LOW: 'LOW',
} as const;

export type TaskPriority = (typeof TaskPriority)[keyof typeof TaskPriority];

export const TaskPriorityConfig = {
  [TaskPriority.HIGH]: { text: '高', color: 'red' },
  [TaskPriority.MEDIUM]: { text: '中', color: 'orange' },
  [TaskPriority.LOW]: { text: '低', color: 'blue' },
} as const;

// 看板列配置
export const KanbanColumns = [
  { id: TaskStatus.TODO, title: '待处理', color: '#64748b' },
  { id: TaskStatus.IN_PROGRESS, title: '进行中', color: '#3b82f6' },
  { id: TaskStatus.REVIEW, title: '待审核', color: '#f59e0b' },
  { id: TaskStatus.DONE, title: '已完成', color: '#10b981' },
] as const;

// 通用颜色配置
export const Colors = {
  primary: '#6366f1',
  success: '#10b981',
  warning: '#f59e0b',
  error: '#ef4444',
  info: '#3b82f6',
  text: {
    primary: '#1e293b',
    secondary: '#64748b',
    muted: '#94a3b8',
  },
  border: '#e2e8f0',
  background: {
    primary: '#f8fafc',
    card: '#ffffff',
  },
} as const;

// 分页配置
export const PaginationConfig = {
  pageSize: 20,
  pageSizeOptions: [10, 20, 50, 100],
  showTotal: (total: number) => `共 ${total} 条`,
};

// 日期格式配置
export const DateFormats = {
  display: 'YYYY-MM-DD',
  datetime: 'YYYY-MM-DD HH:mm:ss',
  locale: 'zh-CN',
};
