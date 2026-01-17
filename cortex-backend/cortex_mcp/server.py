#!/usr/bin/env python3
"""
Cortex MCP Server
将 Cortex CLI 命令封装为 MCP Tools
"""
import asyncio
import json
import subprocess
import re
import sys
from typing import Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

app = Server("cortex-task-manager")

# 工具定义
TOOLS = [
    Tool(
        name="list_tasks",
        description="列出分配给当前用户的任务",
        inputSchema={
            "type": "object",
            "properties": {},
        }
    ),
    Tool(
        name="start_task",
        description="开始任务：创建分支、更新状态为 IN_PROGRESS、切换分支",
        inputSchema={
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "integer",
                    "description": "任务ID"
                }
            },
            "required": ["task_id"]
        }
    ),
    Tool(
        name="submit_pr",
        description="提交任务：推送代码、创建PR、更新状态为REVIEW",
        inputSchema={
            "type": "object",
            "properties": {
                "commit_message": {
                    "type": "string",
                    "description": "Git提交信息（可选，如果不提供会提示用户输入）"
                },
                "auto_open": {
                    "type": "boolean",
                    "description": "是否自动打开浏览器创建PR，默认true",
                    "default": True
                }
            }
        }
    ),
    Tool(
        name="complete_task",
        description="完成任务：切换回主分支、更新状态为DONE、清理分支",
        inputSchema={
            "type": "object",
            "properties": {
                "delete_local": {
                    "type": "boolean",
                    "description": "是否删除本地分支，默认使用配置文件设置",
                    "default": None
                },
                "delete_remote": {
                    "type": "boolean",
                    "description": "是否删除远程分支，默认使用配置文件设置",
                    "default": None
                }
            }
        }
    ),
    Tool(
        name="get_task_status",
        description="获取当前任务的状态（检查当前分支是否是任务分支）",
        inputSchema={
            "type": "object",
            "properties": {},
        }
    ),
]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """处理工具调用"""
    try:
        if name == "list_tasks":
            return await list_tasks()
        elif name == "start_task":
            return await start_task(arguments["task_id"])
        elif name == "submit_pr":
            return await submit_pr(
                commit_message=arguments.get("commit_message"),
                auto_open=arguments.get("auto_open", True)
            )
        elif name == "complete_task":
            return await complete_task(
                delete_local=arguments.get("delete_local"),
                delete_remote=arguments.get("delete_remote")
            )
        elif name == "get_task_status":
            return await get_task_status()
        else:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": str(e)
            }, ensure_ascii=False, indent=2)
        )]


async def list_tasks() -> list[TextContent]:
    """列出任务"""
    result = subprocess.run(
        ["ctx", "tasks", "list", "--json"],
        capture_output=True,
        text=True,
        timeout=30
    )

    if result.returncode != 0:
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": result.stderr,
                "stdout": result.stdout
            }, ensure_ascii=False, indent=2)
        )]

    return [TextContent(
        type="text",
        text=result.stdout
    )]


async def start_task(task_id: int) -> list[TextContent]:
    """开始任务"""
    result = subprocess.run(
        ["ctx", "tasks", "start", str(task_id)],
        capture_output=True,
        text=True,
        timeout=60
    )

    if result.returncode != 0:
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "task_id": task_id,
                "error": result.stderr,
                "stdout": result.stdout
            }, ensure_ascii=False, indent=2)
        )]

    return [TextContent(
        type="text",
        text=json.dumps({
            "success": True,
            "task_id": task_id,
            "output": result.stdout
        }, ensure_ascii=False, indent=2)
    )]


async def submit_pr(commit_message: str = None, auto_open: bool = True) -> list[TextContent]:
    """提交PR"""
    cmd = ["ctx", "tasks", "pr"]

    try:
        if commit_message:
            # 使用 echo 管道传递输入，避免交互式提示
            process = subprocess.Popen(
                ["echo", commit_message],
                stdout=subprocess.PIPE
            )
            pr_process = subprocess.Popen(
                cmd,
                stdin=process.stdout,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = pr_process.communicate(timeout=60)

            if pr_process.returncode != 0:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": stderr,
                        "stdout": stdout
                    }, ensure_ascii=False, indent=2)
                )]

            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "commit_message": commit_message,
                    "output": stdout
                }, ensure_ascii=False, indent=2)
            )]
        else:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": result.stderr,
                        "stdout": result.stdout
                    }, ensure_ascii=False, indent=2)
                )]

            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "output": result.stdout
                }, ensure_ascii=False, indent=2)
            )]
    except subprocess.TimeoutExpired:
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": "Command timed out"
            }, ensure_ascii=False, indent=2)
        )]


async def complete_task(delete_local: bool = None, delete_remote: bool = None) -> list[TextContent]:
    """完成任务"""
    result = subprocess.run(
        ["ctx", "tasks", "done"],
        capture_output=True,
        text=True,
        timeout=60
    )

    if result.returncode != 0:
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": result.stderr,
                "stdout": result.stdout
            }, ensure_ascii=False, indent=2)
        )]

    return [TextContent(
        type="text",
        text=json.dumps({
            "success": True,
            "output": result.stdout
        }, ensure_ascii=False, indent=2)
    )]


async def get_task_status() -> list[TextContent]:
    """获取当前任务状态"""
    # 检查当前 Git 分支
    git_result = subprocess.run(
        ["git", "branch", "--show-current"],
        capture_output=True,
        text=True,
        timeout=10
    )

    if git_result.returncode != 0:
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": "Not in a git repository",
                "current_branch": None,
                "is_task_branch": False
            }, ensure_ascii=False, indent=2)
        )]

    current_branch = git_result.stdout.strip()

    # 检查是否是 Cortex 任务分支
    is_task_branch = bool(re.match(r"feature/task-(\d+)-", current_branch))

    task_id = None
    if is_task_branch:
        match = re.match(r"feature/task-(\d+)-", current_branch)
        if match:
            task_id = int(match.group(1))

    return [TextContent(
        type="text",
        text=json.dumps({
            "success": True,
            "current_branch": current_branch,
            "is_task_branch": is_task_branch,
            "task_id": task_id
        }, ensure_ascii=False, indent=2)
    )]


@app.list_tools()
async def list_tools() -> list[Tool]:
    """列出可用工具"""
    return TOOLS


async def main():
    """启动 MCP 服务器"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


def start():
    """入口函数"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nMCP server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error running MCP server: {e}")
        sys.exit(1)


# 如果是直接运行此文件，使用 start() 函数
if __name__ == "__main__":
    start()
