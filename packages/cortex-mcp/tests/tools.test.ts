import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import {
  executeCLI,
  executeCLIWithJson,
  listTasks,
  startTask,
  submitPr,
  completeTask,
  getTaskStatus,
  type CLIResult,
} from "../src/tools.js";

// Mock execa
vi.mock("execa", () => ({
  execa: vi.fn(),
}));

import { execa } from "execa";

describe("executeCLI", () => {
  it("should return success when command succeeds", async () => {
    vi.mocked(execa).mockResolvedValue({
      stdout: "success output",
      stderr: "",
      failed: false,
    } as any);

    const result = await executeCLI(["test", "args"]);

    expect(result.success).toBe(true);
    expect(result.output).toBe("success output");
  });

  it("should return failure when command fails", async () => {
    vi.mocked(execa).mockResolvedValue({
      stdout: "",
      stderr: "error message",
      failed: true,
    } as any);

    const result = await executeCLI(["test", "args"]);

    expect(result.success).toBe(false);
    expect(result.error).toBe("error message");
  });

  it("should handle exceptions", async () => {
    vi.mocked(execa).mockRejectedValue(new Error("Connection refused"));

    const result = await executeCLI(["test", "args"]);

    expect(result.success).toBe(false);
    expect(result.error).toBe("Connection refused");
  });

  it("should respect timeout parameter", async () => {
    vi.mocked(execa).mockResolvedValue({
      stdout: "output",
      stderr: "",
      failed: false,
    } as any);

    await executeCLI(["test"], 5000);

    expect(execa).toHaveBeenCalledWith("ctx", ["test"], {
      timeout: 5000,
      reject: false,
    });
  });
});

describe("executeCLIWithJson", () => {
  it("should parse valid JSON output", async () => {
    vi.mocked(execa).mockResolvedValue({
      stdout: '{"tasks": []}',
      stderr: "",
      failed: false,
    } as any);

    const result = await executeCLIWithJson(["test"]);

    expect(result).toEqual({ tasks: [] });
  });

  it("should return error for invalid JSON", async () => {
    vi.mocked(execa).mockResolvedValue({
      stdout: "not json",
      stderr: "",
      failed: false,
    } as any);

    const result = await executeCLIWithJson(["test"]);

    expect(result.success).toBe(false);
    expect(result.error).toContain("Failed to parse JSON");
  });
});

describe("listTasks", () => {
  it("should return tasks in MCP content format", async () => {
    vi.mocked(execa).mockResolvedValue({
      stdout: '{"tasks": [{"id": 1, "title": "Test"}]}',
      stderr: "",
      failed: false,
    } as any);

    const result = await listTasks();

    expect(result.content).toBeDefined();
    expect(result.content[0].type).toBe("text");
  });
});

describe("startTask", () => {
  it("should return success response on successful start", async () => {
    vi.mocked(execa).mockResolvedValue({
      stdout: "Task updated to IN_PROGRESS",
      stderr: "",
      failed: false,
    } as any);

    const result = await startTask(1);

    expect(result.content).toBeDefined();
    const parsed = JSON.parse(result.content[0].text);
    expect(parsed.success).toBe(true);
    expect(parsed.task_id).toBe(1);
  });

  it("should return error response on failure", async () => {
    vi.mocked(execa).mockResolvedValue({
      stdout: "",
      stderr: "Task not found",
      failed: true,
    } as any);

    const result = await startTask(999);

    const parsed = JSON.parse(result.content[0].text);
    expect(parsed.success).toBe(false);
  });
});

describe("submitPr", () => {
  it("should submit PR with commit message", async () => {
    vi.mocked(execa).mockResolvedValue({
      stdout: "PR created",
      stderr: "",
      failed: false,
    } as any);

    const result = await submitPr("feat: new feature");

    const parsed = JSON.parse(result.content[0].text);
    expect(parsed.success).toBe(true);
    expect(parsed.commit_message).toBe("feat: new feature");
  });

  it("should submit PR without commit message", async () => {
    vi.mocked(execa).mockResolvedValue({
      stdout: "PR created",
      stderr: "",
      failed: false,
    } as any);

    const result = await submitPr();

    const parsed = JSON.parse(result.content[0].text);
    expect(parsed.success).toBe(true);
  });
});

describe("completeTask", () => {
  it("should return success response on successful completion", async () => {
    vi.mocked(execa).mockResolvedValue({
      stdout: "Task status updated to DONE",
      stderr: "",
      failed: false,
    } as any);

    const result = await completeTask();

    const parsed = JSON.parse(result.content[0].text);
    expect(parsed.success).toBe(true);
  });
});

describe("getTaskStatus", () => {
  it("should detect task branch", async () => {
    vi.mocked(execa).mockResolvedValue({
      stdout: "feature/task-123-test-branch",
      stderr: "",
      failed: false,
    } as any);

    const result = await getTaskStatus();

    const parsed = JSON.parse(result.content[0].text);
    expect(parsed.success).toBe(true);
    expect(parsed.is_task_branch).toBe(true);
    expect(parsed.task_id).toBe(123);
  });

  it("should handle non-task branch", async () => {
    vi.mocked(execa).mockResolvedValue({
      stdout: "main",
      stderr: "",
      failed: false,
    } as any);

    const result = await getTaskStatus();

    const parsed = JSON.parse(result.content[0].text);
    expect(parsed.success).toBe(true);
    expect(parsed.is_task_branch).toBe(false);
    expect(parsed.task_id).toBe(null);
  });

  it("should handle git error", async () => {
    vi.mocked(execa).mockResolvedValue({
      stdout: "",
      stderr: "Not a git repository",
      failed: true,
    } as any);

    const result = await getTaskStatus();

    const parsed = JSON.parse(result.content[0].text);
    expect(parsed.success).toBe(false);
    expect(parsed.error).toBe("Not in a git repository");
  });
});
