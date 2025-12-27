import { http } from '../../lib/http';
import type { Project, ProjectCreate } from '../../types';


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