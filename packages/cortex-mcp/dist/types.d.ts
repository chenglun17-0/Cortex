export interface CLIResult<T = unknown> {
    success: boolean;
    data?: T;
    error?: string;
    stdout?: string;
}
export interface Task {
    id: number;
    title: string;
    status: string;
    priority: string;
    branch_name?: string | null;
}
export interface TaskStatusResult {
    success: boolean;
    current_branch: string;
    is_task_branch: boolean;
    task_id: number | null;
}
export interface StartTaskResult {
    success: boolean;
    task_id: number;
    output: string;
}
export interface SubmitPRResult {
    success: boolean;
    commit_message?: string;
    output: string;
}
export interface CompleteTaskResult {
    success: boolean;
    output: string;
}
export declare class CLIError extends Error {
    readonly stdout?: string | undefined;
    readonly stderr?: string | undefined;
    constructor(message: string, stdout?: string | undefined, stderr?: string | undefined);
}
//# sourceMappingURL=types.d.ts.map