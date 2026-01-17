export interface CLIResult {
    success: boolean;
    output?: string;
    error?: string;
}
export declare function executeCLI(args: string[], timeout?: number): Promise<CLIResult>;
export declare function executeCLIWithJson(args: string[], timeout?: number): Promise<any>;
export declare function listTasks(): Promise<any>;
export declare function startTask(taskId: number): Promise<any>;
export declare function submitPr(commitMessage?: string): Promise<any>;
export declare function completeTask(): Promise<any>;
export declare function getTaskStatus(): Promise<any>;
//# sourceMappingURL=tools.d.ts.map