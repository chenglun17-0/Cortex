## MODIFIED Requirements

### Requirement: Task Model Soft Delete
Task 模型 SHALL 支持软删除机制，通过 `deleted_at` 字段标记任务是否被删除。原实现使用硬删除。

#### Scenario: 软删除任务
- **WHEN** 用户发送 DELETE 请求到 `/tasks/{id}`
- **THEN** 任务的 deleted_at 字段被设置为当前时间，任务不会被物理删除

#### Scenario: 查询任务排除已删除
- **WHEN** 用户查询任务列表（GET /tasks/ 或 GET /tasks/project/{project_id}）
- **THEN** 返回的结果不包含 deleted_at 不为空的记录

#### Scenario: 查询单个已删除任务
- **WHEN** 用户尝试获取一个已软删除的任务详情
- **THEN** 返回 404 错误，提示任务不存在

#### Scenario: 任务不存在
- **WHEN** 用户尝试删除一个不存在的任务
- **THEN** 返回 404 错误，提示任务不存在

### Requirement: Task Read Response
TaskRead 接口的返回结构 SHALL 包含 deleted_at 字段，用于标识任务是否已被软删除。原实现不包含此字段。

#### Scenario: 获取任务详情包含删除标记
- **WHEN** 用户请求获取任务详情
- **THEN** 返回的任务信息中包含 deleted_at 字段，值为 null 表示未删除
