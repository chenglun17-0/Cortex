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
  collaborator_ids: number[];
  project_id: number;
  branch_name?: string;
  deleted_at?: string | null;
  created_at?: string;
  updated_at?: string;
}

export interface TaskUpdate {
  title?: string;
  description?: string | null;
  type?: string | null;
  priority?: string | null;
  status?: TaskStatus;
  branch_name?: string | null;
  deadline?: string | null; // YYYY-MM-DD
  assignee_id?: number | null;
  collaborator_ids?: number[];
}

export interface TaskCreate {
  title: string;
  description?: string;
  priority?: string;
  project_id: number;
  status?: TaskStatus; // 可选，默认为 TODO
  type?: string; // 任务类型: feature, bug, docs, fix, refactor, chore
  deadline?: string; // 截止日期 YYYY-MM-DD
  assignee_id?: number;
  collaborator_ids?: number[];
}

export interface TaskComment {
  id: number;
  content: string;
  task_id: number;
  author_id: number;
  author: {
    id: number;
    username: string;
  };
  created_at: string;
  updated_at: string;
}

export interface TaskCommentListResponse {
  items: TaskComment[];
  total: number;
  page: number;
  page_size: number;
}
