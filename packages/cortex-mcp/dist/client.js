import { execa } from 'execa';
export async function executeCLI(args, timeout = 30000) {
    try {
        const result = await execa('ctx', args, {
            timeout,
            reject: false,
            nodeOptions: {
                stdio: ['inherit', 'pipe', 'pipe']
            }
        });
        if (result.failed) {
            const errorOutput = result.stderr || result.stdout || 'Command failed';
            return {
                success: false,
                error: errorOutput,
                stdout: result.stdout,
            };
        }
        return {
            success: true,
            data: result.stdout,
            stdout: result.stdout,
        };
    }
    catch (error) {
        if (error instanceof Error) {
            return {
                success: false,
                error: error.message,
            };
        }
        return {
            success: false,
            error: 'Unknown error occurred',
        };
    }
}
export async function executeCLIJSON(args, timeout = 30000) {
    const result = await executeCLI(args, timeout);
    if (!result.success || !result.data) {
        return result;
    }
    try {
        const parsed = JSON.parse(result.data);
        return {
            success: true,
            data: parsed,
            stdout: result.stdout,
        };
    }
    catch (error) {
        return {
            success: false,
            error: `Failed to parse JSON: ${error instanceof Error ? error.message : 'Unknown error'}`,
            stdout: result.stdout,
        };
    }
}
//# sourceMappingURL=client.js.map