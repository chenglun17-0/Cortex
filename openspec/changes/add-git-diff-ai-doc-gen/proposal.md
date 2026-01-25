# Change: Add AI-powered Git Diff Documentation Generation

## Why
Currently, when developers use `ctx pr` command to submit tasks, they must manually enter commit messages and PR descriptions. This manual process is:
- Time-consuming and repetitive
- Inconsistent across developers
- Often results in poor-quality commit messages and PR descriptions

AI-powered documentation generation will automate this process, improving developer productivity and maintaining consistent documentation quality.

## What Changes
- **New AI Service Module** (`cli/ai/`):
  - Multi-provider support (OpenAI, Anthropic, local models)
  - Commit message generation following Conventional Commits规范
  - PR description generation with structured format

- **Enhanced CLI Commands**:
  - `ctx pr` command will auto-generate commit messages from Git diff
  - `ctx pr` command will auto-generate PR descriptions
  - Users can confirm/edit before committing

- **New Configuration**:
  - `ai_provider`: AI provider selection
  - `ai_api_key`: API key for AI service
  - `ai_model`: Model selection
  - `ai_base_url`: Custom endpoint for local models

- **New Dependencies**:
  - langchain, langchain-openai, langchain-anthropic
  - openai, anthropic

## Impact
- Affected specs: `cli` (new capability)
- Affected code:
  - `pyproject.toml` - dependencies
  - `cli/config.py` - new config keys
  - `cli/git.py` - new diff function
  - `cli/ai/` - new service module
  - `cli/commands/tasks.py` - modified pr command
- Breaking changes: None (backward compatible with `--no-ai` flag)
