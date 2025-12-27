export interface Project {
    id: number;
    name: string;
    description?: string;
    owner_id: number;
    created_at?: string;
}

export interface ProjectCreate {
    name: string;
    description?: string;
}

export const TaskStatus = {
    TODO: 'TODO',
    IN_PROGRESS: 'IN_PROGRESS',
    REVIEW: 'REVIEW',
    DONE: 'DONE',
} as const;
export type TaskStatus = (typeof TaskStatus)[keyof typeof TaskStatus];

export interface Task {
  id: number;
  title: string;
  description?: string;
  status: TaskStatus;
  priority?: string;
  assignee_id?: number;
  project_id: number;
}

export interface TaskUpdate {
  status?: TaskStatus;
  title?: string;
  description?: string;
}