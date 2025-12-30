---
description: Create a pull request using GitHub CLI
argument-hint: [optional title]
allowed-tools: Bash, Read, Grep, Glob
---

# Create Pull Request

Create a GitHub pull request for $ARGUMENTS using the GitHub CLI (`gh`).

## What This Command Does

Creates a GitHub pull request with:

- Automatic branch analysis and diff review
- Comprehensive PR description
- Proper title format with story ID
- GitHub CLI integration (no MCP required)

## Prerequisites

Ensure GitHub CLI is authenticated:

```bash
gh auth status
```

If not authenticated:

```bash
gh auth login
```

## Process

### 1. Check Git Status

Analyze current repository state:

```bash
git status
git log origin/main..HEAD --oneline
git diff origin/main...HEAD --stat
```

### 2. Verify Branch is Pushed

Ensure branch is synced with remote:

```bash
git branch -vv
git fetch origin
```

If not pushed:

```bash
git push -u origin $(git branch --show-current)
```

### 3. Run Final Validation

Before creating PR, ensure all checks pass:

```bash
ruff check . && pytest
```

### 4. Analyze Changes

Review all commits to understand:

- Main feature/fix being implemented
- Files changed and their purpose
- Related story and plan files
- Test coverage added

### 5. Generate PR Description

Create comprehensive description following the template below.

### 6. Create Pull Request

Use GitHub CLI to create the PR:

```bash
gh pr create \
  --title "[CRONTY-ID] Title here" \
  --body "$(cat <<'EOF'
PR body here...
EOF
)" \
  --base main
```

## PR Title Format

```
[CRONTY-ID] Brief description of the change
```

### Examples

```
[CRONTY-1] Implement cron job scheduling tool
[CRONTY-2] Add job history resource
[CRONTY-3] Create notification prompts
```

### Title Guidelines

- Start with story ID in square brackets
- Use present tense ("Add" not "Added")
- Be concise but descriptive (< 72 characters)
- Capitalize first word after story ID

## PR Description Template

````markdown
## Summary

Brief overview of what this PR accomplishes.

Implements [CRONTY-ID]: [Story title]

## Changes

- List of main changes
- New features added
- Components/modules created

## How to Test

1. Install dependencies: `pip install -e .`
2. Run the server: `fastmcp run server.py`
3. [Testing steps]

## BDD Scenarios Implemented

```gherkin
Scenario: [Name from story]
Given [context]
When [action]
Then [outcome]
```
````

## Checklist

- [ ] All phases completed (1-7)
- [ ] `ruff check . && pytest` passes
- [ ] Manual testing completed
- [ ] No console errors

## Screenshots

[If applicable, add screenshots of UI changes]

---

🤖 Generated with [Claude Code](https://claude.ai/code)

````

## GitHub CLI Commands Reference

```bash
# Check authentication
gh auth status

# Create PR (interactive)
gh pr create

# Create PR with options
gh pr create --title "Title" --body "Body" --base main

# Create PR from file
gh pr create --title "Title" --body-file pr-body.md --base main

# Create draft PR
gh pr create --title "Title" --body "Body" --draft

# View PR status
gh pr status

# List PRs
gh pr list

# View specific PR
gh pr view [PR-NUMBER]
````

## Example PR Creation

````bash
gh pr create \
  --title "[CRONTY-1] Implement cron job scheduling tool" \
  --body "$(cat <<'EOF'
## Summary

Implements the cron job scheduling tool where users can create, list, and manage scheduled jobs.

Implements CRONTY-1: Cron job scheduling

## Changes

- Added `create_cron_job` tool with validation
- Added `list_jobs` resource with filtering
- Added `delete_job` tool
- Full test coverage with pytest

## How to Test

1. Install: `pip install -e .`
2. Run: `fastmcp run server.py`
3. Use MCP client to test tools
4. Verify job creation and listing

## BDD Scenarios Implemented

```gherkin
Scenario: User creates a new cron job
Given I have the MCP server running
When I call create_cron_job with a valid cron expression
Then a new job should be created
And I should receive the job ID
```

## Checklist

- [x] All phases completed (1-7)
- [x] `ruff check . && pytest` passes
- [x] Manual testing completed
- [x] No console errors

---

🤖 Generated with [Claude Code](https://claude.ai/code)
EOF
)" \
  --base main
````

## After PR Creation

### What Happens Next

1. PR URL is returned
2. CI/CD pipelines run (if configured)
3. Request reviews from team members
4. Address feedback and push updates

### Updating the PR

```bash
# Make changes based on feedback
git add .
git commit -m "fix: address review feedback

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
git push
```

### Merging

```bash
# Merge PR (if you have permissions)
gh pr merge [PR-NUMBER] --squash --delete-branch
```

## Troubleshooting

### GitHub CLI Not Authenticated

```bash
gh auth login
# Follow prompts to authenticate
```

### Branch Not Pushed

```bash
git push -u origin $(git branch --show-current)
```

### Conflicts with Main

```bash
git fetch origin
git rebase origin/main
# Resolve conflicts if any
git push --force-with-lease
```

### PR Creation Fails

Check:

- GitHub CLI is authenticated: `gh auth status`
- Branch is pushed to remote
- You have write access to the repository

## Usage Examples

```
/pr

Create a PR for the current branch with auto-generated description.
```

```
/pr Implement cron job scheduling tool

Create a PR with the specified title.
```
