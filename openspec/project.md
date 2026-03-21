# Project Context

## Purpose
**Cortex 智能研发项目管理系统**是一个采用前后端分离架构的系统，其核心特色为 **“Web 管理端 + CLI 开发端”** 的双端协同。
- **Web 前端**：提供类似于 Tower 和 Linear 的敏捷看板与数据报表，用于项目进度的宏观监控。
- **CLI 终端**：专为技术人员设计，实现“开发即管理”。将工单状态流转与 Git 操作（分支创建、切换、提交辅助、合并后清理）原子化绑定，消除上下文切换。
- **AI 能力**：已落地基础版工单智能聚合（语义查重、解决方案推荐）及代码智能辅助（Commit/PR 描述生成、CLI 智能审查），部分协作闭环仍在增强。

## Tech Stack
| 层级 | 模块 | 核心技术栈 | 备注 |
| --- | --- | --- | --- |
| 交互层 | Web前端 | React + Ant Design + React Query | 负责展示看板、报表 |
| | CLI终端 | Python + Typer | 负责git自动化、状态流转 |
| 接入层 | API网关 | FastAPI | |
| 业务层 | 任务引擎 | Python | |
| | Git桥接器 | GitPython + PyGithub/PyGitlab | 操纵代码仓库 |
| | AI引擎 | LangChain + OpenAI / Anthropic | 语义查重、代码审查、文档生成 |
| 数据层 | 关系型数据 | PostgreSQL + Tortoise ORM + Aerich | 存用户、工单状态 |
| | 向量数据 | pgvector | 存任务特征、人员画像 |
| | 缓存/队列 | Redis（规划中） | 当前仓库未接入 |

## Project Conventions

### Architecture Patterns
- **双端协同**：Web 端负责宏观管理，CLI 端负责微观执行。
- **前后端分离**：FastAPI 提供 RESTful API，React 负责 UI 渲染。
- **AI 集成**：通过向量数据库（pgvector）和 LLM（OpenAI）增强管理效率。

### Git Workflow
- **原子化操作**：工单状态与 Git 分支操作深度绑定。
- **分支命名**：如 `feature/task-101-<suffix>`，由 CLI 自动生成并与任务绑定。
- **自动化流转**：
  - `start <task_id>`：自动切出分支，状态变更为“处理中”。
  - `pr`：自动推送并触发 AI 生成 PR 描述，状态变更为“待审核”。
  - `done`：在远程已合并前提下清理分支并将状态变更为“已完成”。

## Domain Context
- **工单即分支**：每个开发任务对应一个规范化的 Git 分支。
- **开发即管理**：开发者通过 CLI 工具在完成代码工作的同时更新项目管理状态。
- **语义搜索**：利用 RAG 技术在提单和开发过程中进行知识发现。

## Important Constraints
- **分支一致性**：必须确保本地 Git 状态与后端任务状态的一致性。
- **认证安全**：CLI 需通过 JWT 进行身份验证，并安全存储凭证。

## External Dependencies
- **PostgreSQL / pgvector**：核心存储与向量检索。
- **Redis**：规划中的缓存与异步队列扩展。
- **OpenAI API**：提供 LLM 支持。
- **GitHub/GitLab API**：用于远程仓库操作与 PR 管理。

## Implementation Status (Current)
### 后端 (FastAPI)
- ✅ 核心架构：FastAPI + Tortoise ORM + JWT 认证。
- ✅ 用户/项目/任务管理已形成主流程闭环。
- ✅ 组织能力当前为创建与查询。
- ✅ 完整的 API 路由系统。

### CLI (Python/Typer)
- ✅ 认证：`login`, `logout`。
- ✅ 任务：`list`, `start`, `pr`, `done` 分支与状态联动。
- ✅ 配置：`list`, `set`, `keys` 基础配置管理。
- ✅ AI 审查：`review run`, `review status`。

### 前端 (React)
- ✅ 登录、工作台、项目列表/看板、任务列表/详情、全局看板、个人中心。
- ✅ 基础版 Analytics 页面与 AI 审查摘要展示。
