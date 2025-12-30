---
description: Create a Product Requirements Document for the product
argument-hint: [PRODUCT-NAME] [Description + context]
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# Create Product Requirements Document

Create a Product Requirements Document for $ARGUMENTS following the simplified template for training katas.

## What This Command Creates

Creates a comprehensive PRD with:

- Product vision and problem statement
- Target users and use cases
- Core features organized by priority
- Future considerations (next iterations or post-MVP in case of early product discovery)

## What NOT to Include

- No detailed acceptance criteria for each feature - only high level narrative
- No tracking plan (events, analytics)
- No rollout plan (feature flags)
- No API specifications
- No database schema details
- No SQL queries

## Process

### 1. Get Current Date

Retrieves current date for documentation timestamps using a shell command.

### 2. Ask Clarifying Questions

**IMPORTANT**: Only ask questions about genuinely unclear aspects. Do NOT ask about:

- Information already in the command definition
- Established project patterns from CLAUDE.md
- Information from recent conversation context

**Before writing ANY PRD:**

- Review the product description
- Ask clarifying questions about unclear requirements
- Uncover edge cases and important details
- Use lettered questions (a, b, c) with numbered answers (1, 2, 3)
- Wait for user responses before proceeding

### 3. Get Confirmation

- Present summary of what will be created
- Ask for explicit user confirmation
- Only proceed after receiving approval

### 4. Create the PRD

- Create PRD in appropriate directory
- Follow template structure below
- Include all required sections

## PRD Structure

### File Location

- **Directory**: `docs/`
- **File**: `PRD-{product-name}.md`
- **Example**: `docs/PRD-cronty-mcp.md`

### Template Structure

```markdown
# PRD: [Product Name]

**Created**: [Date]

## 1. Introduction & Overview

Brief description of what the product is and the problem it solves.

## 2. Problem Statement

What problem does this product solve? Who experiences this problem?

## 3. Goals

### User Goals

- What users want to achieve

### Business Goals

- What the business wants to achieve

## 4. Target Audience

### Primary Users

Description of primary user personas.

### Secondary Users

Description of secondary user personas (if any).

## 5. Core Features

### P0 - Must Have (MVP)

Features required for initial release.

### P1 - Should Have

Features important but not blocking release.

### P2 - Nice to Have

Features for future consideration.

## 6. Technical Requirements

### Stack

- Runtime: Python 3.11+
- Framework: FastMCP
- Testing: pytest

### Integrations

External services or APIs required.

## 7. Constraints

### Scope Limitations

What is explicitly out of scope.

### Technical Constraints

Technical limitations to consider.

## 8. Future Considerations

Post-MVP ideas and enhancements.
```

## Example Clarifying Questions

```
a) What is the primary use case for this MCP server?
  1) Cron job scheduling and management
  2) System monitoring and alerts
  3) Task automation and orchestration

b) Should the server support authentication?
  1) Yes, API key authentication
  2) No, trust the MCP client
  3) Optional - configurable

c) What persistence should be used for job storage?
  1) In-memory (ephemeral)
  2) SQLite (local file)
  3) External database (PostgreSQL, etc.)
```

## PRD Validation Checklist

Ensure all template sections are completed:

- [ ] Introduction & Overview
- [ ] Problem Statement
- [ ] Goals (user and business)
- [ ] Target Audience
- [ ] Core Features (prioritized P0/P1/P2)
- [ ] Technical Requirements
- [ ] Constraints
- [ ] Future Considerations

## After PRD Creation

- PRD is created but development doesn't start automatically
- Share with stakeholders for review if applicable
- Use `/story` command to create detailed user stories
- Use `/phased-plan` command to create implementation plans

## Usage Examples

When invoking the `/prd` command, provide a rich narrative description of the product including key features and functionalities.

```
/prd cronty-mcp

Create a PRD for an MCP server that manages cron jobs.

The server provides three main capabilities:

1. **Tools** - Users can create, update, and delete cron jobs. Each job has a cron expression, a command to execute, and optional metadata.

2. **Resources** - Users can list all jobs, view job details, and see execution history. Filtering by status and date range is supported.

3. **Prompts** - Pre-built prompts help users create common job types like daily backups, hourly health checks, or weekly reports.

The server should persist jobs to a local SQLite database so they survive restarts.
```

```
/prd notification-mcp

Create a PRD for an MCP server that sends notifications across multiple channels.

Key functionality:
- Send notifications via email, Slack, and webhooks
- Template support for consistent messaging
- Delivery status tracking and retry logic
- Rate limiting to prevent abuse
```
