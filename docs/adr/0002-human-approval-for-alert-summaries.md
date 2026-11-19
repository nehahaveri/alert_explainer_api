# 2. Human approval for alert summaries

## Status

Accepted

## Context

The n8n alert-summary workflow generates a summary for each alert and delivers it to the on-call channel.

- An incorrect or misleading automated summary could cause the on-call engineer to under-react or over-react to a real incident.
- During an active incident, a few minutes of approval delay costs much less than a bad summary.

## Decision

The n8n alert-summary workflow routes each generated summary to a human for approval before it is sent to the on-call channel. Summaries are not sent automatically.

## Consequences

- A human reviews every summary before it reaches the on-call engineer.
- Summaries are delivered more slowly.
- Delivery depends on someone being available to approve.
