// src/features/tasks/service.ts
import { http } from '../../lib/http';
import type { Task, TaskUpdate, TaskCreate, TaskComment, TaskCommentListResponse } from '../../types';

// 获取指定项目的任务列表
// 后端接口：GET /api/v1/tasks/project/{project_id}
export const getTasksByProject = async (projectId: string): Promise<Task[]> => {
  const response = await http.get<Task[]>(`/tasks/project/${projectId}`);
  return response.data;
};

// 获取当前用户的任务列表
// 后端接口：GET /api/v1/tasks/
export const getMyTasks = async (): Promise<Task[]> => {
  const response = await http.get<Task[]>('/tasks/');
  return response.data;
};

// 更新任务（用于拖拽后保存状态）
export const updateTask = async (taskId: number, data: TaskUpdate): Promise<Task> => {
  const response = await http.patch<Task>(`/tasks/${taskId}`, data);
  return response.data;
};

export const createTask = async (data: TaskCreate): Promise<Task> => {
  const response = await http.post<Task>('/tasks/', data);
  return response.data;
};

// 获取单个任务详情
// 后端接口：GET /api/v1/tasks/{task_id}
export const getTaskById = async (taskId: number): Promise<Task> => {
  const response = await http.get<Task>(`/tasks/${taskId}`);
  return response.data;
};

// 获取任务评论列表
export const getTaskComments = async (
  taskId: number,
  page = 1,
  pageSize = 10,
): Promise<TaskCommentListResponse> => {
  const response = await http.get<TaskCommentListResponse>(`/tasks/${taskId}/comments`, {
    params: { page, page_size: pageSize },
  });
  return response.data;
};

// 创建任务评论
export const createTaskComment = async (taskId: number, content: string): Promise<TaskComment> => {
  const response = await http.post<TaskComment>(`/tasks/${taskId}/comments`, { content });
  return response.data;
};
