# Implementation Tasks

## Phase 1: Foundation Setup

### 1.1 Add MCP dependency
- [ ] Add `mcp` package to `pyproject.toml` dependencies
- [ ] Update `setuptools.packages.find` to include `cortex_mcp*`
- [ ] Add MCP server entry point: `cortex-mcp = "cortex_mcp.server:main"`
- [ ] Test: `pip install -e .` completes without errors
- **Validation**: `pip show mcp` shows package is installed

### 1.2 Create cortex_mcp module structure
- [ ] Create `cortex-backend/cortex_mcp/__init__.py`
- [ ] Create `cortex-backend/cortex_mcp/server.py` with basic MCP server skeleton
- [ ] Add TODO comments for each tool to be implemented
- **Validation**: Module can be imported: `python -c "import cortex_mcp"`

## Phase 2: MCP Server Implementation

### 2.1 Implement MCP server core
- [ ] Import MCP SDK components (Server, stdio_server, Tool, TextContent)
- [ ] Create `app = Server("cortex-task-manager")`
- [ ] Implement `main()` async function with stdio_server
- [ ] Implement `list_tools()` handler
- [ ] Add basic error handling wrapper
- **Validation**: Server starts and responds to MCP initialization

### 2.2 Implement list_tasks tool
- [ ] Define Tool schema for `list_tasks`
- [ ] Implement `call_tool()` handler for `list_tasks`
- [ ] Use subprocess to call `ctx tasks list --json`
- [ ] Parse and return JSON response
- [ ] Handle subprocess errors (timeout, non-zero exit)
- **Validation**: Tool call returns task list in JSON format

### 2.3 Implement start_task tool
- [ ] Define Tool schema for `start_task` with task_id parameter
- [ ] Implement `call_tool()` handler for `start_task`
- [ ] Use subprocess to call `ctx tasks start <task_id>`
- [ ] Return structured success/failure response
- [ ] Handle invalid task_id errors
- **Validation**: Tool call starts a task and returns branch name

### 2.4 Implement submit_pr tool
- [ ] Define Tool schema for `submit_pr` with optional commit_message
- [ ] Implement `call_tool()` handler for `submit_pr`
- [ ] Handle commit_message via stdin if provided
- [ ] Return PR URL or confirmation
- [ ] Handle git errors (no commits, unpushable state)
- **Validation**: Tool call submits PR and returns result

### 2.5 Implement complete_task tool
- [ ] Define Tool schema for `complete_task`
- [ ] Implement `call_tool()` handler for `complete_task`
- [ ] Use subprocess to call `ctx tasks done`
- [ ] Return success/failure response
- **Validation**: Tool call completes task and switches branch

### 2.6 Implement get_task_status tool
- [ ] Define Tool schema for `get_task_status`
- [ ] Implement `call_tool()` handler for `get_task_status`
- [ ] Use subprocess to call `git branch --show-current`
- [ ] Parse branch name with regex to extract task_id
- [ ] Return current branch, is_task_branch, task_id
- [ ] Handle non-git directory error
- **Validation**: Tool returns correct task status

## Phase 3: CLI Enhancement

### 3.1 Add JSON output to list_tasks
- [ ] Add `json` import to `cli/commands/tasks.py`
- [ ] Add `--json` parameter to `list_tasks()` function
- [ ] Implement JSON output path for task list
- [ ] Ensure backward compatibility (default table output unchanged)
- **Validation**: `ctx tasks list --json` outputs valid JSON

### 3.2 Test JSON output format
- [ ] Test with empty task list
- [ ] Test with multiple tasks
- [ ] Validate JSON structure is parseable
- **Validation**: JSON can be parsed by `json.loads()`

## Phase 4: Documentation

### 4.1 Create integration guide
- [ ] Create `docs/mcp-integration.md`
- [ ] Document Claude Desktop configuration
- [ ] Document standalone server execution
- [ ] Add example usage scenarios
- [ ] Document error handling and troubleshooting

### 4.2 Update project documentation
- [ ] Update `README.md` with MCP section
- [ ] Add MCP to "规划中功能" → "实现中功能"
- [ ] Document available MCP tools
- **Validation**: Documentation is clear and complete

## Phase 5: Testing & Validation

### 5.1 Unit testing (if applicable)
- [ ] Test MCP server tool handlers
- [ ] Test subprocess error handling
- [ ] Test JSON output parsing
- **Validation**: All tests pass

### 5.2 Integration testing
- [ ] Test MCP server startup
- [ ] Test each tool via MCP protocol
- [ ] Test error scenarios (invalid task_id, no git repo, etc.)
- **Validation**: All tools work as expected via MCP

### 5.3 End-to-end testing with Claude Desktop
- [ ] Configure Claude Desktop with Cortex MCP server
- [ ] Test tool discovery
- [ ] Test calling each tool
- [ ] Verify task lifecycle works end-to-end
- **Validation**: Claude Desktop can successfully use Cortex MCP

## Dependencies & Ordering

- **Phase 1** must complete before **Phase 2** (foundation needed)
- **Phase 2.1** must complete before other **Phase 2** tasks (server core needed)
- **Phase 3** can be done in parallel with **Phase 2** (CLI changes independent)
- **Phase 4** can be done after **Phase 2** (need implementation details)
- **Phase 5** must complete after **Phase 2** and **Phase 3** (need code complete)

## Estimated Complexity

- **Phase 1**: Low (dependency setup)
- **Phase 2**: Medium (MCP protocol handling, subprocess integration)
- **Phase 3**: Low (add JSON output parameter)
- **Phase 4**: Low (documentation)
- **Phase 5**: Medium (testing various scenarios)

## Risk Mitigation

1. **MCP SDK changes**: Pin version in requirements, test with specific SDK version
2. **Subprocess reliability**: Add timeouts, handle all exit codes, capture stderr
3. **JSON parsing**: Validate JSON output before returning to AI
4. **Git state issues**: Clearly indicate when not in git repo or task branch
5. **Authentication**: Rely on existing CLI auth, don't re-implement
