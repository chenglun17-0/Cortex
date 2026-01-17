import { execa } from "execa";
export async function executeCLI(args, timeout = 30000) {
    try {
        const result = await execa("ctx", args, {
            timeout,
            reject: false,
        });
        if (result.failed) {
            return {
                success: false,
                error: result.stderr || result.stdout || "Command failed",
            };
        }
        return {
            success: true,
            output: result.stdout,
        };
    }
    catch (error) {
        return {
            success: false,
            error: error instanceof Error ? error.message : String(error),
        };
    }
}
export async function executeCLIWithJson(args, timeout = 30000) {
    const result = await executeCLI(args, timeout);
    if (!result.success || !result.output) {
        return {
            success: false,
            error: result.error,
        };
    }
    try {
        return JSON.parse(result.output);
    }
    catch (error) {
        return {
            success: false,
            error: `Failed to parse JSON: ${error}`,
        };
    }
}
export async function listTasks() {
    const result = await executeCLIWithJson(["tasks", "list", "--json"]);
    return {
        content: [{
                type: "text",
                text: result.output || JSON.stringify(result),
            }],
    };
}
export async function startTask(taskId) {
    const result = await executeCLI(["tasks", "start", String(taskId)], 60000);
    if (!result.success) {
        return {
            content: [{
                    type: "text",
                    text: JSON.stringify({
                        success: false,
                        task_id: taskId,
                        error: result.error,
                        stdout: result.output,
                    }, null, 2),
                }],
        };
    }
    return {
        content: [{
                type: "text",
                text: JSON.stringify({
                    success: true,
                    task_id: taskId,
                    output: result.output,
                }, null, 2),
            }],
    };
}
export async function submitPr(commitMessage) {
    const args = ["tasks", "pr"];
    if (commitMessage) {
        args.push(commitMessage);
    }
    const result = await executeCLI(args, 60000);
    if (!result.success) {
        return {
            content: [{
                    type: "text",
                    text: JSON.stringify({
                        success: false,
                        error: result.error,
                        stdout: result.output,
                    }, null, 2),
                }],
        };
    }
    return {
        content: [{
                type: "text",
                text: JSON.stringify({
                    success: true,
                    commit_message: commitMessage,
                    output: result.output,
                }, null, 2),
            }],
    };
}
export async function completeTask() {
    const result = await executeCLI(["tasks", "done"], 60000);
    if (!result.success) {
        return {
            content: [{
                    type: "text",
                    text: JSON.stringify({
                        success: false,
                        error: result.error,
                        stdout: result.output,
                    }, null, 2),
                }],
        };
    }
    return {
        content: [{
                type: "text",
                text: JSON.stringify({
                    success: true,
                    output: result.output,
                }, null, 2),
            }],
    };
}
export async function getTaskStatus() {
    const gitResult = await executeCLI(["branch", "--show-current"], 10000);
    if (!gitResult.success) {
        return {
            content: [{
                    type: "text",
                    text: JSON.stringify({
                        success: false,
                        error: "Not in a git repository",
                        current_branch: null,
                        is_task_branch: false,
                    }, null, 2),
                }],
        };
    }
    const currentBranch = gitResult.output?.trim() || "";
    const isTaskBranch = /^feature\/task-(\d+)-/.test(currentBranch);
    const taskIdMatch = currentBranch.match(/feature\/task-(\d+)-/);
    const taskId = taskIdMatch ? parseInt(taskIdMatch[1], 10) : null;
    return {
        content: [{
                type: "text",
                text: JSON.stringify({
                    success: true,
                    current_branch: currentBranch,
                    is_task_branch: isTaskBranch,
                    task_id: taskId,
                }, null, 2),
            }],
    };
}
//# sourceMappingURL=tools.js.map