## Context
Cortex CLI needs to generate commit messages and PR descriptions from Git diffs using AI. This feature should support multiple AI providers and integrate seamlessly with the existing `ctx pr` command.

## Goals / Non-Goals

### Goals
- Auto-generate commit messages following Conventional Commits规范
- Auto-generate PR descriptions with structured format
- Support multiple AI providers (OpenAI, Anthropic, local models)
- Provide user confirmation before committing
- Graceful fallback when AI unavailable

### Non-Goals
- Real-time code review (separate feature)
- Semantic duplicate detection (separate feature)
- Git hooks integration (future enhancement)

## Decisions

### 1. Multi-Provider Architecture
**Decision**: Use factory pattern with provider interface
```python
class AIService:
    def generate_commit_message(self, diff: str, task_title: str) -> str: ...
    def generate_pr_description(self, diff: str, task_info: dict) -> str: ...

class OpenAIService(AIService): ...
class AnthropicService(AIService): ...
class LocalModelService(AIService): ...
```
**Rationale**: Easy to add new providers, clear separation of concerns

### 2. LLM Framework
**Decision**: Use LangChain for provider abstraction
**Rationale**:
- Unified interface for multiple LLM providers
- Built-in prompt templates and chains
- Easy to switch providers without code changes

### 3. Commit Message Format
**Decision**: Conventional Commits规范
```
<type>(<scope>): <subject>

<body>

<footer>
```
Types: feat, fix, docs, style, refactor, test, chore

### 4. PR Description Format
**Decision**: Structured template
```
## Summary
<AI-generated summary>

## Changes
- <change 1>
- <change 2>

## Testing
- [ ] Tests added/updated
- [ ] Manual testing completed

## Related Issues
Task #<task_id>
```

### 5. Configuration Storage
**Decision**: Use existing `~/.cortex/config.json`
**Rationale**: Consistent with existing config pattern

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| API key exposure | Store in config file with appropriate permissions |
| API timeout/failure | Timeout + fallback to manual input |
| Large diff size | Truncate or summarize before sending to AI |
| Sensitive data in diff | Add filtering for tokens/keys |

## Migration Plan
1. Add new config keys (backward compatible)
2. Install new dependencies
3. Deploy AI service module
4. Update CLI command with `--ai/--no-ai` flag (default: True)
5. Users configure their API keys via `ctx config set ai_provider=openai` etc.

## Open Questions
- [ ] Should we cache generated messages to avoid repeated API calls?
- [ ] Should we allow custom prompt templates per organization?
- [ ] Should we support streaming for real-time generation feedback?
