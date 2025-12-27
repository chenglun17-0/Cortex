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