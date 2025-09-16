# Examples

This directory contains runnable demos and utilities.

## Streamlit Demo

Run the chatbot that showcases the three agents (Security, Context, Model Selection):

```bash
streamlit run examples/streamlit_demo.py
```

- Shows per-agent insights, costs, and tokens
- Short-circuits unsafe inputs
- Uses JSON-mode responses for reliable parsing

## Smoke Test (CLI)

Quickly exercise all agents and verify LLM calls:

```bash
python examples/agent_smoke_test.py
```

## Sample Queries for Model Selection

- Simple/fast (likely `gpt-3.5-turbo`):
  - "Summarize this short paragraph"
  - "Rewrite this sentence in active voice"
- Balanced/moderate (could pick `gpt-4o-mini` if enabled):
  - "Draft a friendly product update email with 3 bullet points"
  - "Generate 5 tagline variants for a landing page"
- Complex/high-quality (likely `gpt-4o`):
  - "Compare Bayesian and frequentist methods for hierarchical models with code"
  - "Explain how to optimize a transformer for long context with citations"

Notes:
- Agents use response_format={"type": "json_object"} for strict JSON outputs.
- Security metrics are populated per-response (1.0 for detected categories; 0.0 otherwise).
