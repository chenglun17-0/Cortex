# 运行与部署模块规则

## 1. 模块职责

| 项 | 内容 |
|----|------|
| 模块范围 | `scripts/`、`docker-compose.yml`、`Dockerfile.*` |
| 核心职责 | 本地开发启停、容器编排、部署发布 |

## 2. 子模块边界

| 子模块 | 文件 | 职责 |
|--------|------|------|
| 本地启动 | `scripts/start-all.sh` | 启动后端与前端并写入 PID |
| 本地停止 | `scripts/stop-all.sh` | 按 PID/进程名停止服务 |
| 部署脚本 | `scripts/deploy.sh` | 拉代码、校验配置、重建容器 |
| 容器编排 | `docker-compose.yml` | 编排 `postgres/backend/frontend` 服务 |
| 镜像构建 | `Dockerfile.backend`、`Dockerfile.frontend` | 后端/前端容器镜像构建 |

## 3. 数据来源

| 配置项 | 来源 |
|--------|------|
| 后端环境变量 | `cortex-backend/.env`（运行时） |
| 后端环境模板 | `cortex-backend/.env.example`（若存在）或由 `start-all.sh` 兜底复制根目录 `.env.example` |
| 根目录环境模板 | `.env.example`（开发默认模板） |
| PostgreSQL 参数 | `docker-compose.yml` 的 `POSTGRES_*` |
| 前端 API 代理 | `vite.config.ts`（开发）、`nginx-frontend.conf`（生产） |

## 4. 关键机制

| 机制 | 说明 |
|------|------|
| 启停机制 | 本地脚本通过 PID 管理前后端进程 |
| 健康检查机制 | 容器后端依赖数据库健康检查通过后启动 |
| 配置加载机制 | 启动脚本与应用层均依赖 `.env` |

## 5. 依赖关系

| 依赖模块 | 关系 |
|----------|------|
| 后端 API 模块 | 启动、部署、容器镜像均直接依赖 |
| 前端 Web 模块 | 本地开发和容器部署均依赖 |
| 数据库模块 | Compose 中为后端提供基础服务 |

## 6. 变更规则

1. 调整脚本参数或路径时，必须同步更新 README 命令说明。
2. 调整 Compose 服务名或端口时，必须同步更新前端代理配置。
3. 调整环境变量时，必须同步更新根目录 `.env.example`，并核对 `cortex-backend/.env(.example)` 是否一致。

## 7. 执行检查

```bash
# 检查启动脚本读取与复制逻辑
rg -n "\\.env|\\.env\\.example|export \\$\\(grep" scripts/start-all.sh

# 检查后端部署依赖的 env 文件
rg -n "cortex-backend/.env|env_file" scripts/deploy.sh docker-compose.yml
```

## 8. 严禁事项

- ⚠️ 严禁在脚本中回显明文密钥与密码。
- ⚠️ 严禁在未验证健康检查的情况下让后端先于数据库启动。
- ⚠️ 严禁将仅本地有效的路径写死到部署脚本。
