export interface User {
    id: number;
    email: string;
    username: string;
    is_active: boolean;
}

export interface UserUpdateProfile {
    username?: string;
    old_password?: string;
    password?: string;
}

export interface Project {
    id: number;
    name: string;
    description?: string;
    owner_id: number;
    organization_id?: number;
    members: User[];
    created_at?: string;
    updated_at?: string;
}

export interface ProjectCreate {
    name: string;
    description?: string;
}

export interface ProjectUpdate {
    name?: string;
    description?: string;
}

// 从 constants 导入，保持一致性
import { TaskStatus } from '../constants';

export { TaskStatus };

export interface Task {
  id: number;
  title: string;
  description?: string;
  status: TaskStatus;
  priority?: string;
  assignee_id?: number;
  project_id: number;
  branch_name?: string;
  created_at?: string;
  updated_at?: string;
}

export interface TaskUpdate {
  status?: TaskStatus;
  title?: string;
  description?: string;
}

export interface TaskCreate {
  title: string;
  description?: string;
  priority?: string;
  project_id: number;
  status?: TaskStatus; // 可选，默认为 TODO
}