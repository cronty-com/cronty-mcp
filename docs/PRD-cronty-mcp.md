# PRD: Cronty MCP

**Created**: 2025-12-30

## 1. Introduction & Overview

Cronty MCP is a Model Context Protocol (MCP) server that enables AI agents to schedule notifications. It provides a simple interface for scheduling one-off and recurring (cron-based) notifications delivered via NTFY webhooks.

The server acts as a bridge between AI agents and time-based notification delivery, using Upstash QStash for reliable, serverless job scheduling and NTFY for push notification delivery.

## 2. Problem Statement

AI agents lack the ability to perform actions at future times. When a user asks an agent to "remind me tomorrow at 9am" or "send me a weekly report every Monday," the agent has no native capability to fulfill this request—it can only act in the present moment.

Users want AI agents that can:
- Schedule reminders and notifications for future times
- Set up recurring alerts without manual intervention
- Deliver notifications to their devices even when not actively using the agent

## 3. Goals

### User Goals

- Schedule one-time notifications for specific future moments
- Set up recurring notifications using familiar cron expressions
- Receive notifications on their devices via NTFY
- Trust that scheduled notifications will be delivered reliably

### Business Goals

- Demonstrate a minimal, focused MCP server for scheduling
- Showcase integration between MCP, QStash, and NTFY
- Provide a working demo for AI agent scheduling capabilities

## 4. Target Audience

### Primary Users

**AI Agent Developers** - Developers building AI agents that need scheduling capabilities. They integrate Cronty MCP into their agent's tool ecosystem to enable time-based notifications.

### Secondary Users

**End Users** - People interacting with AI agents that use Cronty MCP. They benefit from the scheduling capabilities without directly interacting with the MCP server.

## 5. Core Features

### P0 - Must Have (MVP)

**Schedule One-Off Notification**
- Tool that accepts a message, delivery datetime, and timezone
- Schedules a single notification to be sent at the specified time
- Fires once and completes

**Schedule Cron Notification**
- Tool that accepts a message, cron expression, and timezone
- Schedules a recurring notification based on the cron pattern
- Continues firing according to schedule indefinitely

**NTFY Delivery**
- All notifications delivered via NTFY webhooks
- NTFY topic configurable via environment variable
- QStash handles retry logic automatically

### P1 - Should Have

**Plan-Based Delay Validation**
- Configurable `QSTASH_PLAN_LEVEL` (free / pay-as-you-go / fixed-fee)
- Validate scheduled dates against plan limits:
  - Free: max 7 day delay
  - Pay-as-you-go: max 1 year delay
  - Fixed-fee: no delay limits
- Return clear error if scheduled time exceeds plan limit

**Job Management**
- Tool to list scheduled jobs via QStash API
- Tool to cancel scheduled jobs by ID

### P2 - Deployment

**Cloud Deployment**
- Deploy MCP server to cloud infrastructure
- Documentation for self-hosting

## 6. Technical Requirements

### Stack

- **Runtime**: Python 3.15
- **Framework**: FastMCP
- **Scheduling**: Upstash QStash
- **Testing**: pytest

### Integrations

- **Upstash QStash**: Serverless message queue for scheduling
  - Handles delayed message delivery
  - Manages cron-based recurring schedules
  - Built-in retry logic
  - SDK: [qstash-py](https://github.com/upstash/qstash-py)

- **NTFY**: Push notification service for delivery
  - Uses NTFY HTTP API for sending notifications

### Configuration

| Variable                     | Description                                       | Required |
|------------------------------|---------------------------------------------------|----------|
| `QSTASH_TOKEN`               | QStash API token                                  | Yes      |
| `QSTASH_PLAN_LEVEL`          | QStash plan: `free`, `pay-as-you-go`, `fixed-fee` | No (P1)  |

Note: NTFY topic is passed as `notification_topic` parameter on each tool call, enabling multi-user deployments.

## 7. Constraints

### Scope Limitations

- **MVP is fire-and-forget**: No job listing or cancellation in initial release
- **NTFY only**: Single notification channel
- **No authentication**: Trust the MCP client environment
- **Local deployment**: MVP runs locally with user-provided API keys

### Technical Constraints

- QStash delay limits depend on plan level (free: 7 days max)
- NTFY has rate limits that may affect high-frequency notifications

## 8. Future Considerations

- Job management via QStash SDK (list, cancel)
- Cloud deployment options
- Additional notification channels
