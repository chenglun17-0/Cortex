export class CLIError extends Error {
    stdout;
    stderr;
    constructor(message, stdout, stderr) {
        super(message);
        this.stdout = stdout;
        this.stderr = stderr;
    }
}
//# sourceMappingURL=types.js.map