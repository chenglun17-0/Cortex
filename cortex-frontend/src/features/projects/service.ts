import { http } from '../../lib/http';
import type { Project, ProjectCreate, ProjectUpdate, User } from '../../types';


// 获取项目列表
export const getProjects = async (): Promise<Project[]> => {
  // 假设后端路由是 GET /api/v1/projects/
  const response = await http.get<Project[]>('/projects/');
  return response.data;
};

// 创建新项目
export const createProject = async (data: ProjectCreate): Promise<Project> => {
  const response = await http.post<Project>('/projects/', data);
  return response.data;
};

// 获取项目详情
export const getProject = async (id: number): Promise<Project> => {
  const response = await http.get<Project>(`/projects/${id}`);
  return response.data;
};

// 更新项目
export const updateProject = async (id: number, data: ProjectUpdate): Promise<Project> => {
  const response = await http.patch<Project>(`/projects/${id}`, data);
  return response.data;
};

// 删除项目
export const deleteProject = async (id: number): Promise<void> => {
  await http.delete(`/projects/${id}`);
};

// 获取项目成员列表
export const getProjectMembers = async (id: number): Promise<User[]> => {
  const response = await http.get<User[]>(`/projects/${id}/members`);
  return response.data;
};

// 添加项目成员
export const addProjectMember = async (projectId: number, userId: number): Promise<void> => {
  await http.post(`/projects/${projectId}/members`, null, { params: { user_id: userId } });
};

// 移除项目成员
export const removeProjectMember = async (projectId: number, userId: number): Promise<void> => {
  await http.delete(`/projects/${projectId}/members/${userId}`);
};

// 搜索用户
export const searchUsers = async (keyword: string): Promise<User[]> => {
  const response = await http.get<User[]>('/users/search', { params: { q: keyword } });
  return response.data;
};