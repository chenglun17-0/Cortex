<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

# AI 代理指南

## 项目：Cortex

用于 AI 驱动开发的轻量级规范方法。

## 基础规则
- **语言**：默认用中文回答；命令行输出可保持英文原样。
- **目标优先**：所有实现以"验收标准"与"测试通过"为准；不做与目标无关的改动。以最小的改动实现目标。
- **小步提交**：每一步都**先给出计划**与风险点，再最小改动、运行检查、展示 diff、再提交。
- **先写/补测试**：发现缺陷请先生成 failing spec；修复后跑全量/关键用例。
- **安全**：任何涉及数据库迁移、依赖升级、网络访问、Secrets，**必须先征求确认**并给出回滚方案。不要读取 `.env*`、`config/credentials*`、`secrets/**`。
- **整洁原则** 每次因调试，测试，获取数据产生的临时性的脚本、文档、工具都必须生成在 tmp 文件夹下，并且在完成当前事项之前，必须将其删除，保证目录干净整洁没有多余的东西
- 所有任务遵循 "Ask → Code"
- 粒度：目标耗时 ≤ 1 小时；超出则先拆分
- **目录规范** 根目录下不随意添加文件，文档优先生成在 docs 下，脚本优先生成在 scripts 下，如必须，则尽可能放在 tmp 目录下下
- **一致性原则**：本项目长期维护，需要尽可能保持约定和规则的一致，包括但不限于各类技术栈、约定、行为描述、规则、依赖等。如出现与本文描述不一致的情况，先提示确认，确保降低不一致性的情况是已知的、可控的

## 快速启动命令

### 启动前后端服务
```bash
./scripts/start-all.sh
```

### 停止前后端服务
```bash
./scripts/stop-all.sh
```

### 查看日志
```bash
# 后端日志
tail -f logs/backend.log

# 前端日志
tail -f logs/frontend.log
```

### 启动 MCP 服务器
```bash
# 使用 cortex-mcp 命令（需要先安装后端依赖）
cd cortex-backend
source .venv/bin/activate
cortex-mcp

# 或使用 Python 模块方式
python -m cortex_mcp.server
```

**说明**：MCP 服务器主要用于集成到 Claude Desktop 等 AI 工具，详见 [docs/mcp-integration.md](./docs/mcp-integration.md)

## Git 提交规范

### 查看当前状态
```bash
# 查看当前分支和未提交的文件
git status

# 查看未暂存的修改
git diff

# 查看已暂存的修改
git diff --staged
```

### 添加文件到暂存区
```bash
# 添加所有修改的文件
git add .

# 添加特定文件
git add <文件路径>
```

### 提交更改
```bash
# 提交暂存的文件
git commit -m "<业务功能描述>"

# 示例提交信息
git commit -m "feat: 添加用户登录功能"
git commit -m "fix: 修复任务状态更新的bug"
git commit -m "docs: 更新API文档"
git commit -m "style: 优化前端页面样式"
```

### Commit Message 规范
```
<类型>: <简短的业务功能描述>

[可选的详细说明]

类型：
- feat: 新功能
- fix: 修复bug
- docs: 文档更新
- style: 代码格式/样式调整
- refactor: 重构代码
- test: 测试相关
- chore: 构建/工具相关

示例：
feat: 实现用户注册和登录功能
fix: 修复任务列表分页显示错误
docs: 补充快速启动文档
```

### 推送到远程
```bash
# 推送当前分支
git push

# 推送并设置上游分支
git push -u origin <分支名>
```
