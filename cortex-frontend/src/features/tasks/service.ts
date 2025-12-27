// src/features/tasks/service.ts
import { http } from '../../lib/http';
import type { Task, TaskUpdate, TaskCreate } from '../../types';

// 获取指定项目的任务列表
// 假设后端接口支持过滤：GET /api/v1/tasks/?project_id=1
export const getTasksByProject = async (projectId: string): Promise<Task[]> => {
  const response = await http.get<Task[]>('/tasks/', {
    params: { project_id: projectId },
  });
  return response.data;
};

// 更新任务（用于拖拽后保存状态）
export const updateTask = async (taskId: number, data: TaskUpdate): Promise<Task> => {
  const response = await http.put<Task>(`/tasks/${taskId}`, data);
  return response.data;
};

export const createTask = async (data: TaskCreate): Promise<Task> => {
  const response = await http.post<Task>('/tasks/', data);
  return response.data;
};