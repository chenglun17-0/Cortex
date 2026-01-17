## MODIFIED Requirements

### Requirement: MCP Server Deployment
The system SHALL provide an MCP server that can be deployed using standard npm package management tools.

#### Scenario: Deploy via npx
- **WHEN** a user configures AI system with `"command": "npx", "args": ["@cortex/cli-mcp@latest"]`
- **THEN** system SHALL automatically download and execute the latest MCP server
- **AND** no Python environment or PYTHONPATH configuration SHALL be required

#### Scenario: Verify installation
- **WHEN** a user runs `npx @cortex/cli-mcp@latest --help`
- **THEN** system SHALL display MCP server usage information
- **AND** system SHALL respond to MCP initialization handshake

## REMOVED Requirements

### Requirement: Python-based MCP Server
**Reason**: Migrating to TypeScript/npm package for better ecosystem alignment and simpler deployment.

**Migration**: Update AI system configuration to use `npx @cortex/cli-mcp@latest` instead of Python-based configuration.

### Requirement: PYTHONPATH Configuration
**Reason**: npm packages do not require PYTHONPATH environment variables.

**Migration**: Remove PYTHONPATH from configuration files; use standard npm package installation.

### Requirement: Virtual Environment Setup
**Reason**: npm packages handle dependencies automatically via package.json.

**Migration**: No virtual environment setup required; npm manages dependencies.

### Requirement: Python Architecture Compatibility Handling
**Reason**: TypeScript implementation does not have Python architecture issues.

**Migration**: Remove start-mcp.sh script and architecture fix logic.

## ADDED Requirements

### Requirement: TypeScript-based MCP Implementation
The system SHALL implement the MCP server using TypeScript with @modelcontextprotocol/sdk-typescript.

#### Scenario: Type-safe implementation
- **WHEN** the MCP server code is developed
- **THEN** system SHALL use TypeScript for type safety
- **AND** all Tool definitions SHALL have proper type annotations
- **AND** JSON parsing SHALL be type-checked

#### Scenario: Standard SDK usage
- **WHEN** implementing MCP protocol communication
- **THEN** system SHALL use @modelcontextprotocol/sdk-typescript
- **AND** system SHALL follow SDK best practices

### Requirement: NPM Package Publishing
The system SHALL be packaged and published as an npm package named @cortex/cli-mcp.

#### Scenario: Install from npm registry
- **WHEN** a user runs `npm install @cortex/cli-mcp` or `npx @cortex/cli-mcp@latest`
- **THEN** system SHALL be installed from npm registry
- **AND** system SHALL be executable as a standalone MCP server

#### Scenario: Version management
- **WHEN** new features or bug fixes are released
- **THEN** system SHALL follow semantic versioning (MAJOR.MINOR.PATCH)
- **AND** users SHALL be able to specify exact versions (e.g., @cortex/cli-mcp@1.2.3)

### Requirement: CLI Command Execution via Node.js
The system SHALL execute Cortex CLI commands from Node.js using child process spawning.

#### Scenario: Execute ctx commands
- **WHEN** MCP Tools call ctx commands (e.g., `ctx tasks list --json`)
- **THEN** system SHALL spawn child processes to execute CLI
- **AND** system SHALL capture stdout and stderr
- **AND** system SHALL parse JSON responses from CLI output

#### Scenario: Error handling
- **WHEN** a CLI command fails
- **THEN** system SHALL capture the error output
- **AND** system SHALL return structured error response to AI
- **AND** system SHALL not crash the MCP server

### Requirement: Backwards Compatibility Notice
The system SHALL provide deprecation notice for Python-based MCP server.

#### Scenario: Python MCP startup warning
- **WHEN** a user runs the old Python-based cortex-mcp
- **THEN** system SHALL display a deprecation warning
- **AND** warning SHALL include migration instructions to npm package
- **AND** system SHALL continue to function (during migration period)

## ADDED Requirements

### Requirement: Node.js Runtime Requirement
The system SHALL require Node.js runtime (>=18.0.0) for execution.

#### Scenario: Runtime check
- **WHEN** a user attempts to run the MCP server
- **THEN** system SHALL check Node.js version
- **AND** system SHALL fail gracefully if version is incompatible
- **AND** error message SHALL specify minimum required version

### Requirement: Package Documentation
The system SHALL include comprehensive documentation in the npm package.

#### Scenario: README documentation
- **WHEN** a user views the package on npm registry
- **THEN** system SHALL display README.md with:
  - Quick start guide
  - Configuration examples for Claude Desktop, Cline, Cursor
  - Tool reference
  - Migration guide from Python version
