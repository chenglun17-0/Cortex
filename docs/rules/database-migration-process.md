# 数据库迁移流程规范

## 问题记录

### 问题：aerich 迁移未正确应用

**发生日期**：2026-01-25

**问题描述**：
- Task 模型添加 `deleted_at` 字段后，迁移文件已生成（`2_20260124223945_None.py`）
- 但数据库中 `tasks` 表缺少 `deleted_at` 字段
- 执行 `aerich upgrade` 返回 "No upgrade items found"

**根本原因**：
aerich 迁移系统依赖 `aerich` 版本表记录已应用的迁移。当迁移文件生成但未在数据库中注册时，系统认为没有需要升级的内容。

**解决步骤**：
```bash
# 1. 检查 aerich 版本表
SELECT * FROM aerich;

# 2. 手动执行迁移 SQL（以 deleted_at 为例）
ALTER TABLE tasks ADD COLUMN deleted_at TIMESTAMPTZ;

# 3. 在 aerich 表中注册迁移版本
INSERT INTO aerich (version, app, content)
VALUES ('2_20260124223945_None.py', 'models', '{}');
```

## 规范流程

### 新增字段/表的标准流程

```bash
# 1. 修改模型文件
# 2. 生成迁移
aerich migrate

# 3. 立即应用迁移
aerich upgrade

# 4. 验证 aerich 版本表
SELECT * FROM aerich;

# 5. 验证数据库结构
\d <table_name>
```

### 迁移未应用时的排查

| 检查项 | 命令 |
|--------|------|
| 查看 aerich 版本表 | `SELECT * FROM aerich;` |
| 查看迁移文件 | `ls migrations/models/` |
| 检查模型状态 | `aerich inspect-db` |

### 手动修复步骤

1. **确认迁移文件存在**：`ls migrations/models/`
2. **执行迁移 SQL**：从迁移文件中提取 `upgrade()` 函数的 SQL
3. **注册迁移版本**：向 `aerich` 表插入版本记录
4. **验证**：重新执行 `aerich upgrade` 确认无新项

## 注意事项

1. **不要跳过 `upgrade`**：生成迁移后必须立即应用
2. **多人协作**：确保团队成员执行相同的迁移步骤
3. **备份**：生产环境执行前先备份数据库
