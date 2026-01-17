# Design: Refactor MCP Server to NPM Package

## Architecture Overview

```
┌─────────────────┐     MCP Protocol      ┌──────────────────┐
│  AI System      │ <────────────────────> │  Cortex MCP      │
│  (Claude/Cline) │   stdio / HTTP        │  (TypeScript)     │
└─────────────────┘                        └──────────────────┘
                                                    │
                                                    │ exec / spawn
                                                    ▼
                                           ┌──────────────────┐
                                           │  Cortex CLI      │
                                           │  (ctx commands)  │
                                           └──────────────────┘
                                                    │
                                                    │ HTTP / JWT
                                                    ▼
                                           ┌──────────────────┐
                                           │  Cortex Backend  │
                                           │  (FastAPI)       │
                                           └──────────────────┘
```

## Component Design

### 1. NPM Package Structure

```
packages/cortex-mcp/
├── package.json          # npm 包配置
├── tsconfig.json        # TypeScript 配置
├── src/
│   ├── index.ts         # MCP 服务器入口
│   ├── tools.ts        # MCP Tools 定义
│   └── client.ts      # Cortex CLI 客户端封装
├── dist/              # 编译输出
└── README.md          # 包文档
```

### 2. MCP Server (src/index.ts)

**职责**：
- 使用 @modelcontextprotocol/sdk-typescript 实现 MCP 协议
- 定义并注册 5 个 Tools（复用 Python 版本的功能）
- 处理 stdio 通信

**依赖**：
```json
{
  "@modelcontextprotocol/sdk-typescript": "^1.0.0",
  "execa": "^8.0.0"
}
```

**Tool 定义**：
```typescript
Tools = [
  list_tasks() -> 执行 ctx tasks list --json
  start_task(task_id) -> 执行 ctx tasks start <id>
  submit_pr(commit_message?) -> 执行 ctx tasks pr
  complete_task() -> 执行 ctx tasks done
  get_task_status() -> 检查 git 分支状态
]
```

### 3. CLI Client Wrapper (src/client.ts)

**职责**：
- 封装 CLI 命令调用
- 处理 JSON 解析和错误
- 管理超时和重试

**实现**：
```typescript
import { execa } from 'execa';

export async function executeCLI(args: string[], timeout?: number): Promise<CLIResult> {
  const result = await execa('ctx', args, {
    timeout: timeout || 30000,
    reject: false
  });

  if (result.failed) {
    throw new CLIError(result.stderr || result.stdout);
  }

  return JSON.parse(result.stdout);
}
```

## Configuration

### Package Configuration

**package.json**：
```json
{
  "name": "@cortex/cli-mcp",
  "version": "1.0.0",
  "type": "module",
  "main": "./dist/index.js",
  "bin": {
    "cortex-mcp": "./dist/index.js"
  },
  "exports": {
    ".": "./dist/index.js"
  },
  "files": [
    "dist",
    "README.md"
  ]
}
```

### Claude Desktop Configuration

```json
{
  "mcpServers": {
    "cortex": {
      "command": "npx",
      "args": [
        "@cortex/cli-mcp@latest"
      ]
    }
  }
}
```

## Migration Strategy

### Phase 1: Development
1. 初始化 TypeScript 项目
2. 实现 MCP Server 基础框架
3. 迁移 5 个 Tools
4. 本地测试验证

### Phase 2: Testing
1. 单元测试（Tools 执行逻辑）
2. 集成测试（与 CLI 交互）
3. AI 工具测试（Claude Desktop, Cline）

### Phase 3: Rollout
1. 发布 npm 包
2. 更新文档
3. 废弃 Python MCP

## Trade-offs

### Approach 1: TypeScript NPM Package (Chosen) ✅
**优点**：
- 生态统一，使用 MCP 官方 TypeScript SDK
- 部署简单，npx 即可
- 维护成本低，社区支持好
- 类型安全

**缺点**：
- 需要维护额外的 TypeScript 项目
- 依赖 Node.js 运行时（用户需安装 Node）

### Approach 2: Keep Python, Improve Packaging
**优点**：
- 与 CLI 技术栈统一
- 无需额外运行时

**缺点**：
- 部署复杂（PYTHONPATH、虚拟环境）
- 生态不统一
- 配置繁琐

**决策**：选择 **Approach 1**，因为：
1. MCP 生态以 TypeScript/JavaScript 为主
2. 部署简单性 outweighs 技术栈统一
3. 长期维护成本更低

## Security Considerations

1. **认证复用**：继续使用 CLI 的 JWT 认证机制
2. **权限隔离**：MCP 继承 CLI 用户的权限
3. **输入验证**：所有参数经过 CLI 的验证逻辑
4. **Secrets 保护**：不直接访问 API，通过 CLI 代理

## Backwards Compatibility

### Migration Path

1. **Python MCP 保留期**：保留 1 个月作为迁移窗口
2. **废弃通知**：在 Python MCP 启动时提示用户升级到 npm 包
3. **功能对等**：确保 npm 包功能完全覆盖 Python 版本
4. **文档更新**：在文档中标注 Python MCP 已废弃

### Rollback Plan

如果 npm 包出现严重问题：
1. 回退到 Python MCP（cortex-mcp.py 仍保留）
2. 通知用户切换配置
3. 修复 npm 包问题后再迁移

## Open Questions

1. **包命名**：`@cortex/cli-mcp` vs `@cortex/mcp`？
2. **版本管理**：语义化版本策略？
3. **发布频率**：跟随 cortex-backend 发布节奏？
