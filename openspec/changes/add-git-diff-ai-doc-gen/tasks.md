## 1. Dependencies
- [ ] 1.1 Add AI dependencies to `pyproject.toml`
- [ ] 1.2 Run `uv sync` to install new packages

## 2. Configuration
- [ ] 2.1 Add AI config keys to `cli/config.py`
- [ ] 2.2 Add config validation logic

## 3. Git Operations
- [ ] 3.1 Add `get_diff()` function to `cli/git.py`

## 4. AI Service Module
- [ ] 4.1 Create `cli/ai/__init__.py`
- [ ] 4.2 Create `cli/ai/service.py` with base class and providers
- [ ] 4.3 Implement OpenAI provider
- [ ] 4.4 Implement Anthropic provider
- [ ] 4.5 Implement local model provider
- [ ] 4.6 Add prompt templates for commit message and PR description
- [ ] 4.7 Add sensitive data filtering

## 5. CLI Integration
- [ ] 5.1 Modify `ctx pr` command in `cli/commands/tasks.py`
- [ ] 5.2 Add `--ai/--no-ai` flag
- [ ] 5.3 Implement commit message generation flow
- [ ] 5.4 Implement PR description generation flow
- [ ] 5.5 Add graceful fallback when AI unavailable

## 6. Documentation
- [ ] 6.1 Update `docs/project.md` with new feature
- [ ] 6.2 Add CLI help text for new config options

## 7. Testing
- [ ] 7.1 Test with mock AI service (no API key)
- [ ] 7.2 Test with real OpenAI API
- [ ] 7.3 Test edge cases (empty diff, large diff, timeout)
