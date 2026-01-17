#!/usr/bin/env node

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { listTasks } from "./tools.js";
import { startTask } from "./tools.js";
import { submitPr } from "./tools.js";
import { completeTask } from "./tools.js";
import { getTaskStatus } from "./tools.js";

const TOOLS = [
  {
    name: "list_tasks",
    description: "列出分配给当前用户的任务",
    inputSchema: {
      type: "object",
      properties: {},
    }
  },
  {
    name: "start_task",
    description: "开始任务：创建分支、更新状态为 IN_PROGRESS、切换分支",
    inputSchema: {
      type: "object",
      properties: {
        task_id: {
          type: "number",
          description: "任务ID"
        }
      },
      required: ["task_id"]
    }
  },
  {
    name: "submit_pr",
    description: "提交任务：推送代码、创建PR、更新状态为REVIEW",
    inputSchema: {
      type: "object",
      properties: {
        commit_message: {
          type: "string",
          description: "Git提交信息（可选）"
        }
      }
    }
  },
  {
    name: "complete_task",
    description: "完成任务：切换回主分支、更新状态为DONE、清理分支",
    inputSchema: {
      type: "object",
      properties: {}
    }
  },
  {
    name: "get_task_status",
    description: "获取当前任务的状态（检查当前分支是否是任务分支）",
    inputSchema: {
      type: "object",
      properties: {}
    }
  },
];

async function main() {
  const server = new Server(
    {
      name: "cortex-task-manager",
      version: "1.0.0",
    },
    {
      capabilities: {
        tools: {},
      },
    }
  );

  server.setRequestHandler(ListToolsRequestSchema, async () => {
    return {
      tools: TOOLS,
    };
  });

  server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const { name, arguments: args } = request.params;

    try {
      switch (name) {
        case "list_tasks":
          return await listTasks();
        case "start_task":
          return await startTask(args?.task_id as number);
        case "submit_pr":
          return await submitPr(args?.commit_message as string | undefined);
        case "complete_task":
          return await completeTask();
        case "get_task_status":
          return await getTaskStatus();
        default:
          return {
            content: [{
              type: "text",
              text: JSON.stringify({
                success: false,
                error: `Unknown tool: ${name}`
              }, null, 2)
            }],
          };
      }
    } catch (error) {
      return {
        content: [{
          type: "text",
          text: JSON.stringify({
            success: false,
            error: error instanceof Error ? error.message : String(error)
          }, null, 2)
        }]
      };
    }
  });

  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((error) => {
  console.error("Fatal error running MCP server:", error);
  process.exit(1);
});
