---
description: Create a conventional commit with AI attribution following project standards
argument-hint: [optional custom message]
allowed-tools: Bash, Read, Grep, Glob
---

# Create Conventional Commit

Create a conventional commit with AI attribution for $ARGUMENTS following project standards.

## What This Command Does

Creates properly formatted commits with:

- Conventional commit format (`type(scope): description`)
- AI attribution with proper co-authorship
- Pre-commit validation (when needed)
- Automatic staging of changes

## Efficient Workflow Integration

### After `/implement` Command

If you just used `/implement` and tests passed:

- **Skips** pre-commit checks (already validated)
- Proceeds directly to staging and committing
- More efficient workflow

### Standalone Usage

When used independently:

- Runs full pre-commit validation
- Ensures code quality before commit

## Process

### 1. Check Current Changes

Analyzes what will be committed:

```bash
git status
git diff --staged
git diff  # unstaged changes
```

**Detect Code Files:**

Check if any modified files are code files that require validation:

```bash
# Check for Python file extensions in changed files
git diff --name-only --staged | grep -E '\.py$' || echo "No code files"
git diff --name-only | grep -E '\.py$' || echo "No code files"
```

If no code files are found, skip validation steps.

### 2. Pre-commit Validation

**Skipped if:**

- Recent `/implement` completed successfully, OR
- Only non-code files are modified (e.g., markdown, documentation, config files)

**Check for code files:**

- Python: `.py`

**Non-code files (skip checks):**

- Markdown: `.md`
- Documentation: `.txt`, `.rst`
- Images: `.png`, `.jpg`, `.svg`, etc.
- Config: `.json`, `.yaml`, `.yml`, `.toml` (unless they affect code)

**If code files are modified, runs:**

```bash
ruff check .          # Linting checks
pytest                # Run tests
```

### 3. Stage Changes

Stages all relevant changes:

```bash
git add .  # or specific files
```

### 4. Create Commit Message

Generates conventional commit with AI attribution

## Commit Message Format

### Structure

```
type(scope): description

[optional body]

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

### Types (Conventional Commits)

- **`feat`**: New feature
- **`fix`**: Bug fix
- **`docs`**: Documentation only
- **`style`**: Code formatting changes
- **`refactor`**: Code restructuring (no functionality change)
- **`test`**: Adding or updating tests
- **`chore`**: Maintenance tasks, dependency updates
- **`perf`**: Performance improvements
- **`ci`**: CI/CD changes
- **`build`**: Build system changes
- **`revert`**: Reverting previous commit

### Scope Guidelines

Use feature names or component areas:

**MCP Server:**
- `(server)` - General server changes
- `(tools)` - MCP tools implementation
- `(resources)` - MCP resources
- `(prompts)` - MCP prompts
- `(config)` - Configuration changes

**Infrastructure:**
- `(ci)` - CI/CD configuration
- `(docker)` - Docker configuration
- `(deps)` - Dependencies

For multiple areas: `(tools,resources)` or `(server,config)`

### Description Rules

- Use imperative mood ("add" not "added")
- Don't capitalize first letter
- No period at the end
- Max 100 characters
- Be specific and descriptive

## Example Commits

### Feature Implementation

```bash
feat(tools): implement cron job scheduling tool

- Add create_cron_job tool with validation
- Support standard cron expressions
- Add timezone handling

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

### Bug Fix

```bash
fix(server): resolve connection timeout issue

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

### Documentation

```bash
docs(readme): update installation instructions

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

## AI Attribution

**Always includes proper AI attribution:**

```
🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

## Multi-line Commits

For complex changes:

```bash
feat(resources): implement job history resource

- Add list_jobs resource with filtering
- Support pagination for large result sets
- Include job status and execution time

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

## Special Cases

### Work in Progress

```bash
chore(wip): temporary checkpoint for feature branch

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

### Reverting Changes

```bash
revert: feat(tools): implement cron job scheduling

This reverts commit abc123def456

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

## After Committing

### Verification

```bash
git log -1 --oneline  # Check commit was created
```

### If Mistakes Made

```bash
# Amend last commit (before pushing)
git commit --amend

# Change just the message
git commit --amend -m "new message"
```

## Best Practices

### Atomic Commits

- One logical change per commit
- Each commit should make sense independently
- Related changes should be grouped together

### Clear History

- Descriptive commit messages
- Logical progression of changes
- Easy to understand project evolution

### Quality Assurance

- Tests pass before committing
- Code follows project standards
- No linting errors

## Usage Examples

```
/commit
/commit "custom message" (will be formatted to convention)
```

## Troubleshooting

### Lint/Test Failures

- Fix linting errors: `ruff check . --fix`
- Ensure tests pass: `pytest`

### Staging Issues

- Check which files need to be committed
- Use `git add .` for all changes
- Use `git add <file>` for specific files
- Verify staged changes with `git diff --staged`

## Python Commands Reference

```bash
# Lint all files
ruff check .

# Lint and auto-fix
ruff check . --fix

# Format code
ruff format .

# Run tests
pytest

# Run tests with coverage
pytest --cov
```
