# 前端模块（`cortex-frontend/src`）

## 1. 分层结构

| 分层 | 目录 | 职责 |
|------|------|------|
| 页面功能层 | `features/` | 按业务域组织页面与 service（auth/projects/tasks/dashboard） |
| 基础设施层 | `lib/` | HTTP 实例、React Query 客户端 |
| 类型层 | `types/` | 全局领域类型定义 |
| 常量层 | `constants/` | 状态、优先级、看板列、分页配置 |
| 工具层 | `utils/` | 文案/颜色映射、日期格式化等 |
| 组件层 | `components/` | 可复用 UI（当前以 `layout` 为主） |

## 2. 关键入口

| 文件 | 说明 |
|------|------|
| `src/main.tsx` | React 根挂载，注入 QueryClient 与 Antd 配置 |
| `src/App.tsx` | 路由定义、登录守卫、主布局挂载 |
| `src/components/layout/MainLayout.tsx` | 受保护页面布局骨架 |

## 3. 主要页面路由

| 路径 | 页面 | 说明 |
|------|------|------|
| `/login` | `features/auth/LoginPage` | 登录页（公开） |
| `/` | `features/dashboard/DashboardPage` | 工作台 |
| `/projects` | `features/projects/ProjectsPage` | 项目列表 |
| `/projects/:projectId` | `features/tasks/KanbanBoard` | 项目看板 + 成员管理 + 创建任务弹窗（含语义查重） |
| `/tasks` | `features/tasks/TaskListPage` | 我的任务列表 |
| `/tasks/:taskId` | `features/tasks/TaskDetailPage` | 任务详情 + 评论 |
| `/tasks/new` | `features/tasks/CreateTaskPage` | 创建任务 + 相似任务检测 |
| `/board` | `features/tasks/TaskBoardPage` | 全局任务看板 + 创建任务弹窗（含语义查重） |
| `/profile` | `features/auth/ProfilePage` | 个人中心 |

补充说明：`/tasks/new`、`/board` 与 `/projects/:projectId` 的创建任务入口均支持“负责人（单选）+协同人（多选）”，协同人选项会自动排除已选负责人；提交时会对协同人去重。`/board` 与 `/projects/:projectId` 的创建任务弹窗支持语义查重结果直达任务详情；全局看板（`/board`）中的任务卡片支持键盘 `Enter` 触发跳转。`/projects/:projectId` 的成员管理抽屉默认加载同组织可添加用户（可输入关键字进一步筛选）。查重请求会对标题/描述拼接文本做长度截断并使用 20s 超时；若查重请求失败，页面优先展示后端返回的具体原因（无明确原因时回退“服务连接异常，请稍后重试查重”），但不阻塞任务创建。

## 4. 数据流（React Query）

```text
Page Component
  -> useQuery/useMutation
  -> features/*/service.ts
  -> lib/http.ts (axios)
  -> /api/v1/*
```

| 层 | 关键点 |
|----|--------|
| `lib/http.ts` | 自动注入 token，401 清理登录态并跳转登录页 |
| `react-query` | 以 `queryKey` 管缓存，mutation 后 `invalidateQueries` 刷新 |
| `service.ts` | 负责接口封装，不承载复杂页面状态 |

## 5. 维护建议

1. 新业务优先放到对应 `features/<domain>` 下。
2. 状态/优先级映射统一复用 `constants` 与 `utils`。
3. 避免在组件中直接写后端地址，统一走 `lib/http.ts`。
