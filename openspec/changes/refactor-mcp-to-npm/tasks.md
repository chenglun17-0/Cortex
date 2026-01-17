## 1. Project Setup
- [ ] 1.1 初始化 TypeScript 项目（packages/cortex-mcp/）
- [ ] 1.2 配置 tsconfig.json、package.json
- [ ] 1.3 安装依赖（@modelcontextprotocol/sdk-typescript, execa）

## 2. MCP Server Implementation
- [ ] 2.1 创建 index.ts（MCP 服务器入口）
- [ ] 2.2 实现 MCP stdio 通信
- [ ] 2.3 注册 5 个 Tools 定义
- [ ] 2.4 实现工具调用处理器

## 3. Tools Implementation
- [ ] 3.1 实现 list_tasks Tool
- [ ] 3.2 实现 start_task Tool
- [ ] 3.3 实现 submit_pr Tool
- [ ] 3.4 实现 complete_task Tool
- [ ] 3.5 实现 get_task_status Tool

## 4. CLI Client Wrapper
- [ ] 4.1 创建 client.ts（CLI 调用封装）
- [ ] 4.2 实现 executeCLI 函数
- [ ] 4.3 添加错误处理和超时管理
- [ ] 4.4 实现 JSON 解析和验证

## 5. Testing
- [ ] 5.1 编写 Tools 单元测试
- [ ] 5.2 测试 CLI 集成
- [ ] 5.3 在 Claude Desktop 中测试
- [ ] 5.4 在 Cline 中测试

## 6. Documentation
- [ ] 6.1 更新 docs/mcp-integration.md（npm 包配置）
- [ ] 6.2 编写 README.md（npm 包使用说明）
- [ ] 6.3 添加 npm 发布说明

## 7. Deployment
- [ ] 7.1 编译 TypeScript（tsc）
- [ ] 7.2 发布到 npm（@cortex/cli-mcp）
- [ ] 7.3 测试 npx @cortex/cli-mcp@latest

## 8. Cleanup
- [ ] 8.1 在 Python MCP 中添加废弃提示
- [ ] 8.2 更新 cortex-backend/pyproject.toml（移除 cortex-mcp 入口）
- [ ] 8.3 归档 docs/mcp-integration.md（保留 Python 配置说明）
