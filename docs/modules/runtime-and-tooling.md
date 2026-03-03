# 运行与工具链模块（`scripts/` + 容器部署入口）

## 1. 脚本清单

| 脚本 | 作用 | 说明 |
|------|------|------|
| `scripts/start-all.sh` | 一键启动前后端 | 启动后端 `uvicorn` 与前端 `vite`，记录 PID 与日志 |
| `scripts/stop-all.sh` | 一键停止前后端 | 读取 `.pids` 或按进程名兜底停止 |
| `scripts/ctx` | CLI 包装脚本 | 调用后端虚拟环境中的 `ctx` |
| `scripts/deploy.sh` | 部署脚本 | 生产/发布相关操作入口 |

## 2. 本地运行约定

| 项目 | 约定 |
|------|------|
| PID 文件 | 根目录 `.pids` |
| 日志目录 | `logs/backend.log`、`logs/frontend.log` |
| 后端环境 | `cortex-backend/.venv` |
| 前端依赖 | `cortex-frontend/node_modules` |

## 3. 容器与代理入口

| 文件 | 作用 |
|------|------|
| `docker-compose.yml` | 编排 `postgres` / `backend` / `frontend` 三个服务 |
| `Dockerfile.backend` | 构建后端镜像并启动 `uvicorn` |
| `Dockerfile.frontend` | 构建前端静态资源并由 `nginx` 提供服务 |
| `nginx-frontend.conf` | 前端静态资源规则与 `/api` 代理到 `backend:8000` |
| `cortex-frontend/vite.config.ts` | 本地开发阶段 `/api` 代理到 `127.0.0.1:8000` |

## 4. 启停流程

### 启动

```bash
./scripts/start-all.sh
```

流程：
1. 检查 `.pids` 防止重复启动。
2. 检查后端 `.venv` 与 `.env`。
3. 启动后端 `uvicorn app.main:app --reload`。
4. 启动前端 `npm run dev`。
5. 写入 `.pids` 并输出访问地址。

### 停止

```bash
./scripts/stop-all.sh
```

流程：
1. 优先读取 `.pids` 停止进程。
2. 若 `.pids` 不存在，按进程名兜底查杀。
3. 清理 `.pids`。

## 5. 常用开发命令

```bash
# 前端
cd cortex-frontend && npm run lint
cd cortex-frontend && npm run build

# 后端测试（当前仓库）
cd cortex-backend && . .venv/bin/activate && python -m unittest discover -v
```
