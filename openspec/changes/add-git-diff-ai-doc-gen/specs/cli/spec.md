## ADDED Requirements

### Requirement: AI Documentation Generation
The system SHALL provide AI-powered generation of commit messages and PR descriptions from Git diffs.

#### Scenario: Generate commit message with AI
- **WHEN** a user runs `ctx pr` with uncommitted changes and AI is enabled
- **AND** AI provider is configured with valid API key
- **THEN** the system SHALL retrieve the Git diff
- **AND** the system SHALL send the diff to the configured AI provider
- **AND** the system SHALL display the generated commit message
- **AND** the system SHALL ask for user confirmation
- **IF** user confirms
  - **THEN** the system SHALL commit with the generated message
- **ELSE**
  - **THEN** the system SHALL prompt for manual commit message input

#### Scenario: Generate PR description with AI
- **WHEN** a user runs `ctx pr` and AI is enabled
- **AND** AI provider is configured with valid API key
- **THEN** the system SHALL generate PR description from the diff
- **AND** the system SHALL use the generated description when creating PR

#### Scenario: Fallback when AI unavailable
- **WHEN** AI provider is not configured or API call fails
- **THEN** the system SHALL fall back to manual input
- **AND** the system SHALL display a warning message

#### Scenario: Disable AI generation
- **WHEN** user runs `ctx pr --no-ai`
- **THEN** the system SHALL skip AI generation
- **AND** the system SHALL prompt for manual commit message

### Requirement: Multi-Provider Support
The system SHALL support multiple AI providers for documentation generation.

#### Scenario: Configure OpenAI provider
- **WHEN** user runs `ctx config set ai_provider=openai`
- **AND** user runs `ctx config set ai_api_key=<key>`
- **AND** user runs `ctx config set ai_model=gpt-4`
- **THEN** the system SHALL use OpenAI for AI generation

#### Scenario: Configure Anthropic provider
- **WHEN** user runs `ctx config set ai_provider=anthropic`
- **AND** user runs `ctx config set ai_api_key=<key>`
- **AND** user runs `ctx config set ai_model=claude-sonnet-4-20250514`
- **THEN** the system SHALL use Anthropic for AI generation

#### Scenario: Configure local model
- **WHEN** user runs `ctx config set ai_provider=local`
- **AND** user runs `ctx config set ai_base_url=http://localhost:11434`
- **THEN** the system SHALL use local LLM endpoint

### Requirement: Sensitive Data Filtering
The system SHALL filter sensitive information from diffs before sending to AI.

#### Scenario: Filter credentials
- **WHEN** the system processes a Git diff
- **THEN** the system SHALL remove patterns matching API keys, tokens, passwords
- **AND** the system SHALL NOT send sensitive data to external AI services
