# MCP 服务器架构兼容性问题

## 问题描述

在 macOS 上，由于 Apple Silicon (ARM64) 和 Intel (x86_64) 两种架构的存在，可能会遇到 `pydantic_core` 二进制文件架构不兼容的问题。

## 检测方法

### 1. 检查系统架构
```bash
uname -m
```
输出应为 `arm64` (Apple Silicon) 或 `x86_64` (Intel)

### 2. 检查 pydantic_core 是否正常
```bash
cd cortex-backend
source .venv/bin/activate
python -c "import pydantic_core; print('OK')"
```

如果报错 `ImportError: incompatible architecture`，说明存在架构不匹配。

## 解决方案

### 方案 1: 使用启动脚本（推荐）

```bash
cd cortex-backend
./start-mcp.sh
```

启动脚本会自动检测架构并尝试修复。

### 方案 2: 手动修复（如果方案1失败）

```bash
cd cortex-backend
source .venv/bin/activate

# 卸载并重新安装 pydantic-core
pip uninstall -y pydantic-core
pip install pydantic-core

# 测试
python -c "import pydantic_core; print('OK')"

# 启动 MCP
python -m cortex_mcp.server
```

### 方案 3: Apple Silicon 强制 ARM64

如果系统是 Apple Silicon 但终端在 Rosetta 模式下运行：

```bash
# 终端 > 设置 > 常规 > 勾选"使用 Rosetta 打开"
# 或者直接使用 arch 命令
cd cortex-backend
source .venv/bin/activate
arch -arm64 python -m cortex_mcp.server
```

### 方案 4: Intel Mac 或 Rosetta 模式

```bash
cd cortex-backend
source .venv/bin/activate
python -m cortex_mcp.server
```

## 常见错误信息

### ImportError: incompatible architecture (have 'arm64', need 'x86_64')
- **原因**: pydantic_core 是 ARM64 版本，但 Python 运行在 x86_64 模式
- **解决**: 重新安装 pydantic-core，或使用 `arch -arm64` 强制运行

### ImportError: incompatible architecture (have 'x86_64', need 'arm64')
- **原因**: pydantic_core 是 x86_64 版本，但 Python 运行在 ARM64 模式
- **解决**: 重新安装 pydantic-core

## 预防措施

1. **保持一致性**: 确保虚拟环境在正确的架构下创建
2. **避免混合**: 不要在不同架构的终端间共享同一个虚拟环境
3. **使用脚本**: 始终使用 `./start-mcp.sh` 启动 MCP 服务器

## 技术细节

### 为什么会出现这个问题？

- `pydantic_core` 包含编译的二进制文件（`.so`）
- macOS 支持通用二进制（Universal Binary），但有时只安装特定架构
- Rosetta 可以让 x86_64 应用在 ARM64 Mac 上运行，但二进制文件架构必须匹配

### 虚拟环境迁移

如果需要在不同架构间迁移虚拟环境：

```bash
# 删除旧环境
rm -rf .venv

# 在新架构下创建
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```
