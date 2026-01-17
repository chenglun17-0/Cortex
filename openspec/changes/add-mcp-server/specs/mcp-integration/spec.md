## ADDED Requirements

### Requirement: MCP Server Discovery
The system SHALL provide an MCP server that can be discovered and connected by AI systems using the Model Context Protocol.

#### Scenario: List available tools
- **WHEN** an AI system connects to the Cortex MCP server
- **THEN** the system SHALL respond with a list of available tools:
  - `list_tasks` - List assigned tasks
  - `start_task` - Start a task
  - `submit_pr` - Submit a pull request
  - `complete_task` - Complete a task
  - `get_task_status` - Get current task status

#### Scenario: Provide tool schemas
- **WHEN** an AI system requests tool definitions
- **THEN** the system SHALL provide JSON schemas for each tool
- **AND** each schema SHALL include: name, description, input properties, required fields

### Requirement: Task List via MCP
The system SHALL allow AI systems to retrieve the current user's task list through the MCP protocol.

#### Scenario: AI retrieves task list
- **WHEN** an AI system calls the `list_tasks` tool
- **THEN** the system SHALL execute `ctx tasks list --json`
- **AND** the system SHALL return a JSON response containing task data
- **AND** the response SHALL include: task ID, title, status, priority, branch name

#### Scenario: Handle empty task list
- **WHEN** the user has no assigned tasks
- **THEN** the system SHALL return an empty task list with a message
- **AND** the response format SHALL be consistent JSON

### Requirement: Task Start via MCP
The system SHALL allow AI systems to start a task through the MCP protocol.

#### Scenario: AI starts a task
- **WHEN** an AI system calls the `start_task` tool with a task_id
- **THEN** the system SHALL execute `ctx tasks start <task_id>`
- **AND** the system SHALL return success/failure status in JSON format
- **AND** on success, the response SHALL include: task ID, branch name created

#### Scenario: Handle invalid task ID
- **WHEN** an AI system provides an invalid task_id
- **THEN** the system SHALL return an error response
- **AND** the error response SHALL include the error message from CLI

#### Scenario: Handle git repository errors
- **WHEN** the current directory is not a git repository
- **THEN** the system SHALL return an error response
- **AND** the error message SHALL indicate that git operations are not available

### Requirement: Pull Request Submission via MCP
The system SHALL allow AI systems to submit code for review through the MCP protocol.

#### Scenario: AI submits a PR with commit message
- **WHEN** an AI system calls the `submit_pr` tool with a commit_message
- **THEN** the system SHALL execute `ctx tasks pr` with the commit message
- **AND** the system SHALL return success/failure status in JSON format
- **AND** on success, the response SHALL include: PR URL or confirmation

#### Scenario: AI submits a PR without commit message
- **WHEN** an AI system calls the `submit_pr` tool without a commit_message
- **THEN** the system SHALL execute `ctx tasks pr` interactively
- **AND** the system SHALL handle the CLI's interactive prompt
- **OR** return an error if interaction is not supported

### Requirement: Task Completion via MCP
The system SHALL allow AI systems to mark a task as complete through the MCP protocol.

#### Scenario: AI completes a task
- **WHEN** an AI system calls the `complete_task` tool
- **THEN** the system SHALL execute `ctx tasks done`
- **AND** the system SHALL return success/failure status in JSON format
- **AND** on success, the response SHALL include: task ID marked as done

#### Scenario: Handle branch cleanup
- **WHEN** task completion is successful
- **THEN** the system SHALL respect the user's configured cleanup settings
- **AND** local and remote branches SHALL be deleted if configured

### Requirement: Current Task Status via MCP
The system SHALL allow AI systems to check the current task context through the MCP protocol.

#### Scenario: AI checks current task status
- **WHEN** an AI system calls the `get_task_status` tool
- **THEN** the system SHALL check the current git branch
- **AND** the system SHALL determine if it's a Cortex task branch
- **AND** the system SHALL return: current branch name, is_task_branch boolean, task_id (if applicable)

#### Scenario: Not in a task branch
- **WHEN** the current git branch is not a Cortex task branch
- **THEN** the system SHALL return `is_task_branch: false`
- **AND** the system SHALL return `task_id: null`

#### Scenario: Not in a git repository
- **WHEN** the current directory is not a git repository
- **THEN** the system SHALL return an error response
- **AND** the error message SHALL indicate "Not in a git repository"

### Requirement: JSON Output Support
The system SHALL provide structured JSON output for CLI commands to enable AI parsing.

#### Scenario: List tasks with JSON output
- **WHEN** a user runs `ctx tasks list --json`
- **THEN** the system SHALL output task data in JSON format
- **AND** the JSON SHALL include: `{"tasks": [...], "message": "..."}`
- **AND** the output SHALL be valid, parseable JSON

#### Scenario: Empty tasks with JSON output
- **WHEN** a user runs `ctx tasks list --json` with no tasks
- **THEN** the system SHALL output `{"tasks": [], "message": "No assigned tasks"}`
- **AND** the format SHALL be consistent with non-empty responses

#### Scenario: Backward compatibility
- **WHEN** a user runs `ctx tasks list` without `--json` flag
- **THEN** the system SHALL display the table format as before
- **AND** the behavior SHALL be unchanged from the current implementation

### Requirement: MCP Server Configuration
The system SHALL provide documentation for configuring AI systems to use the Cortex MCP server.

#### Scenario: Claude Desktop configuration
- **WHEN** a user wants to use Cortex MCP with Claude Desktop
- **THEN** the system SHALL provide a configuration example
- **AND** the example SHALL show the command, args, and PYTHONPATH

#### Scenario: Standalone MCP server execution
- **WHEN** a user runs the cortex MCP server directly
- **THEN** the server SHALL start and listen for MCP protocol messages via stdio
- **AND** the server SHALL handle the MCP initialization handshake

### Requirement: Error Handling
The system SHALL handle errors gracefully and provide meaningful error messages to AI systems.

#### Scenario: CLI command timeout
- **WHEN** a CLI command takes longer than the configured timeout
- **THEN** the system SHALL return a timeout error response
- **AND** the error SHALL indicate which command timed out

#### Scenario: Network errors
- **WHEN** a CLI command fails due to network issues (e.g., API unreachable)
- **THEN** the system SHALL capture the CLI error output
- **AND** the system SHALL return the error in a structured JSON response

#### Scenario: Authentication errors
- **WHEN** the user is not logged in (no valid JWT token)
- **THEN** the system SHALL return an authentication error
- **AND** the error message SHALL indicate that login is required

### Requirement: Dependency Management
The system SHALL include MCP SDK as a dependency and ensure proper packaging.

#### Scenario: Install with pip
- **WHEN** a user runs `pip install -e .` in cortex-backend
- **THEN** the system SHALL install the MCP SDK (`mcp` package)
- **AND** the installation SHALL complete without errors

#### Scenario: MCP server entry point
- **WHEN** a user runs `cortex-mcp` command
- **THEN** the system SHALL execute the MCP server main function
- **AND** the server SHALL start listening for MCP connections
