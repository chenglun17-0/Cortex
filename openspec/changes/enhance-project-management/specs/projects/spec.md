## ADDED Requirements

### Requirement: Project Update
系统 SHALL 支持更新项目的基本信息（名称、描述）。

#### Scenario: 更新项目名称
- **WHEN** 用户发送 PATCH 请求到 `/projects/{id}`，包含新的 name 字段
- **THEN** 项目的名称被更新为新值

#### Scenario: 更新项目描述
- **WHEN** 用户发送 PATCH 请求到 `/projects/{id}`，包含新的 description 字段
- **THEN** 项目的描述被更新为新值

#### Scenario: 项目不存在
- **WHEN** 用户尝试更新一个不存在的项目
- **THEN** 返回 404 错误，提示项目不存在

### Requirement: Project Deletion
系统 SHALL 支持软删除项目（设置 deleted_at 标记），删除前需检查关联数据。

#### Scenario: 软删除无任务的项目
- **WHEN** 用户删除一个没有关联任务的项目
- **THEN** 项目的 deleted_at 被设置为当前时间，项目状态变为已删除，返回 200

#### Scenario: 软删除有关联任务的项目
- **WHEN** 用户尝试删除一个有关联任务的项目
- **THEN** 返回 400 错误，提示该项目下还有未完成的任务

#### Scenario: 项目不存在
- **WHEN** 用户尝试删除一个不存在的项目
- **THEN** 返回 404 错误，提示项目不存在

#### Scenario: 查询已删除项目
- **WHEN** 用户查询一个已软删除的项目
- **THEN** 返回 404 错误，提示项目不存在

### Requirement: Project Member Management
系统 SHALL 支持获取、添加和移除项目成员。

#### Scenario: 获取成员列表
- **WHEN** 用户请求获取项目的成员列表
- **THEN** 返回包含所有成员信息的列表（id, username, email）

#### Scenario: 添加项目成员
- **WHEN** 用户发送 POST 请求到 `/projects/{id}/members`，包含 userId
- **THEN** 该用户被添加到项目的成员列表中

#### Scenario: 重复添加成员
- **WHEN** 尝试将已是项目成员的用户再次添加
- **THEN** 返回 400 错误，提示用户已是成员

#### Scenario: 移除项目成员
- **WHEN** 用户发送 DELETE 请求到 `/projects/{id}/members/{userId}`
- **THEN** 该用户从项目成员列表中移除

#### Scenario: 移除非成员用户
- **WHEN** 尝试移除一个不是项目成员的用户
- **THEN** 返回 404 错误，提示用户不是项目成员

### Requirement: User Search
系统 SHALL 支持按关键词搜索用户，用于成员添加。

#### Scenario: 按用户名搜索
- **WHEN** 用户请求搜索用户，关键字为 "john"
- **THEN** 返回用户名包含 "john" 的用户列表

#### Scenario: 无匹配用户
- **WHEN** 搜索关键字没有匹配的用户
- **THEN** 返回空列表

## MODIFIED Requirements

### Requirement: Project Read Response
ProjectRead 接口的返回结构 SHALL 包含 members 字段，用于返回项目的成员列表信息。原实现仅返回项目基本信息。

#### Scenario: 获取项目详情包含成员
- **WHEN** 用户请求获取项目详情
- **THEN** 返回的项目信息中包含 members 字段，列出所有成员
