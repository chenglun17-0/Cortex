## 1. 后端接口开发

### 1.1 Schema 更新
- [x] 1.1.1 更新 ProjectRead 添加 members 字段和 deleted_at 字段
- [x] 1.1.2 新增 ProjectUpdate schema
- [x] 1.1.3 新增 ProjectMemberResponse schema

### 1.2 API 端点
- [x] 1.2.1 实现 PATCH /projects/{id} 更新项目
- [x] 1.2.2 实现 DELETE /projects/{id} 删除项目（含任务检查）
- [x] 1.2.3 实现 GET /projects/{id}/members 获取成员列表
- [x] 1.2.4 实现 POST /projects/{id}/members 添加成员
- [x] 1.2.5 实现 DELETE /projects/{id}/members/{userId} 移除成员
- [x] 1.2.6 实现 GET /users/search 用户搜索

## 2. 前端功能开发

### 2.1 类型更新
- [x] 2.1.1 更新 Project 接口添加 members 字段
- [x] 2.1.2 新增 ProjectUpdate 类型
- [x] 2.1.3 新增 User 类型用于成员列表

### 2.2 服务层
- [x] 2.2.1 新增 updateProject 服务方法
- [x] 2.2.2 新增 deleteProject 服务方法
- [x] 2.2.3 新增 getProjectMembers 服务方法
- [x] 2.2.4 新增 addProjectMember 服务方法
- [x] 2.2.5 新增 removeProjectMember 服务方法
- [x] 2.2.6 新增 searchUsers 服务方法

### 2.3 页面组件
- [x] 2.3.1 ProjectsPage 添加项目编辑功能
- [x] 2.3.2 KanbanBoard 新增成员管理面板（成员管理）
- [x] 2.3.3 添加成员搜索/选择功能

## 3. 测试与验证
- [ ] 3.1 API 接口测试
- [ ] 3.2 前端功能测试
- [ ] 3.3 更新 project.md 文档
