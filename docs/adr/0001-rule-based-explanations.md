# 1. Rule-based alert explanations

## Status

Accepted

## Context

The API produces a plain-language explanation for each alert. These explanations must:

- Be generated instantly and at no cost.
- Work offline, including in CI.
- Be deterministic: the same alert must always produce the same explanation, so tests do not depend on variable LLM output.

## Decision

`generate_explanation()` in `services/explainer.py` builds explanations from fixed rules based on the alert's severity, metric value, and threshold. It does not call an external LLM API.

## Consequences

- Explanations are instant, free, available offline, and deterministic.
- Tests do not depend on variable LLM output.
- Explanations are more generic than LLM-generated text.
- Alert patterns that the rules do not anticipate cannot be handled.
