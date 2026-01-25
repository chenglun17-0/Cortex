# 前端共享模块规范

本文档描述 cortex-frontend 项目中的共享常量模块和工具函数规范。

## 目录结构

```
cortex-frontend/src/
├── constants/          # 共享常量模块
│   └── index.ts        # 常量定义
├── utils/              # 工具函数模块
│   └── index.ts        # 工具函数
└── ...
```

## 常量模块 (constants/index.ts)

### 任务状态 (TaskStatus)

| 常量值 | 说明 |
|--------|------|
| `TaskStatus.TODO` | 待处理 |
| `TaskStatus.IN_PROGRESS` | 进行中 |
| `TaskStatus.REVIEW` | 待审核 |
| `TaskStatus.DONE` | 已完成 |

### 状态配置 (TaskStatusConfig)

状态显示配置，映射状态值到显示文本和颜色。

```typescript
const statusConfig = TaskStatusConfig[TaskStatus.TODO];
// { text: '待处理', color: 'default' }
```

| 状态 | 文本 | 颜色 |
|------|------|------|
| TODO | 待处理 | default |
| IN_PROGRESS | 进行中 | processing |
| REVIEW | 待审核 | warning |
| DONE | 已完成 | success |

### 任务优先级 (TaskPriority)

| 常量值 | 说明 |
|--------|------|
| `TaskPriority.HIGH` | 高优先级 |
| `TaskPriority.MEDIUM` | 中优先级 |
| `TaskPriority.LOW` | 低优先级 |

### 优先级配置 (TaskPriorityConfig)

优先级显示配置。

| 优先级 | 文本 | 颜色 |
|--------|------|------|
| HIGH | 高 | red |
| MEDIUM | 中 | orange |
| LOW | 低 | blue |

### 看板列配置 (KanbanColumns)

看板视图的列配置，包含每列的 ID、标题和指示颜色。

```typescript
import { KanbanColumns } from '../../constants';

// 遍历生成看板列
KanbanColumns.map(col => (
  <Droppable key={col.id} droppableId={col.id}>
    ...
  </Droppable>
))
```

### 通用颜色 (Colors)

| 类别 | 颜色值 |
|------|--------|
| primary | `#6366f1` |
| success | `#10b981` |
| warning | `#f59e0b` |
| error | `#ef4444` |
| info | `#3b82f6` |

### 分页配置 (PaginationConfig)

```typescript
PaginationConfig = {
  pageSize: 20,
  pageSizeOptions: [10, 20, 50, 100],
  showTotal: (total: number) => `共 ${total} 条`,
}
```

## 工具函数 (utils/index.ts)

### 状态相关函数

#### getStatusConfig(status: string)
获取状态的完整配置对象。

```typescript
import { getStatusConfig } from '../../utils';

const config = getStatusConfig(TaskStatus.IN_PROGRESS);
// { text: '进行中', color: 'processing' }
```

#### getStatusColor(status: string)
获取状态对应的 Ant Design 颜色。

```typescript
const color = getStatusColor(TaskStatus.DONE); // 'success'
```

#### getStatusText(status: string)
获取状态对应的中文文本。

```typescript
const text = getStatusText(TaskStatus.TODO); // '待处理'
```

### 优先级相关函数

#### getPriorityConfig(priority?: string)
获取优先级的完整配置对象。自动处理大小写。

```typescript
import { getPriorityConfig } from '../../utils';

const config = getPriorityConfig('high'); // { text: '高', color: 'red' }
const config = getPriorityConfig('HIGH'); // { text: '高', color: 'red' }
```

#### getPriorityColor(priority?: string)
获取优先级对应的 Ant Design 颜色。

```typescript
const color = getPriorityColor('MEDIUM'); // 'orange'
```

#### getPriorityText(priority?: string)
获取优先级对应的中文文本。

```typescript
const text = getPriorityText('low'); // '低'
```

### 日期格式化函数

#### formatDate(dateString?: string)
格式化日期为 `YYYY-MM-DD` 格式。

```typescript
import { formatDate } from '../../utils';

formatDate('2026-01-25T10:00:00Z'); // '2026/1/25'
formatDate(undefined); // '-'
```

#### formatDateTime(dateString?: string)
格式化日期时间为本地完整格式。

```typescript
import { formatDateTime } from '../../utils';

formatDateTime('2026-01-25T10:00:00Z'); // '2026/1/25 18:00:00'
formatDateTime(undefined); // '-'
```

### 其他函数

#### formatTaskId(id: number)
格式化任务 ID 显示。

```typescript
import { formatTaskId } from '../../utils';

formatTaskId(123); // '#123'
```

## 使用示例

### 在页面组件中使用

```typescript
import { TaskStatus, KanbanColumns, PaginationConfig } from '../../constants';
import { getStatusConfig, getPriorityConfig, formatDateTime } from '../../utils';

// 状态渲染
<Tag color={getStatusConfig(task.status).color}>
  {getStatusConfig(task.status).text}
</Tag>

// 或使用简写
<Tag color={getStatusColor(task.status)}>
  {getStatusText(task.status)}
</Tag>

// 优先级渲染
<PriorityTag priority={task.priority} />

// 看板列渲染
{KanbanColumns.map(col => (
  <Droppable key={col.id} droppableId={col.id}>
    ...
  </Droppable>
))}

// 分页配置
<Table
  pagination={{
    pageSize: PaginationConfig.pageSize,
    showTotal: PaginationConfig.showTotal,
  }}
/>

// 日期格式化
<span>{formatDateTime(task.updated_at)}</span>
```

### 在类型定义中使用

```typescript
import { TaskStatus } from '../../constants';

interface Task {
  status: TaskStatus;
  priority?: TaskPriority;
}
```

## 约束与规范

1. **禁止在组件中重复定义状态/优先级映射** - 应使用 constants 模块中的配置
2. **优先级统一使用大写** - HIGH / MEDIUM / LOW
3. **使用工具函数获取颜色/文本** - 保持代码一致性
4. **日期格式化使用工具函数** - 统一显示格式

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0 | 2026-01-25 | 初始版本，提取共享常量模块和工具函数 |
