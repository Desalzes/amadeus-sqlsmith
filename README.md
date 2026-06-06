# Amadeus SQLSmith

Amadeus SQLSmith is an AgentBeats purple agent specialized for Text-to-SQL
benchmarks. It exposes an A2A HTTP service, accepts SQL task payloads, generates
safe SELECT queries, validates identifiers with `sqlglot`, and returns the JSON
shape expected by the public `ashcastelinocs124/text-2-sql-agent` green agent:

```json
{
  "sql": "SELECT COUNT(*) AS total FROM customers",
  "reasoning": "strategy=customer_count; validation=ok",
  "task_id": "sqlite_count"
}
```

The v1 solver is SQLite-first and schema-aware. It has deterministic planners
for common benchmark shapes, plus an optional OpenAI fallback when
`OPENAI_API_KEY` is provided.

## Layout

```text
src/
  server.py             A2A server and agent card
  executor.py           A2A SDK request handling
  agent.py              Thin A2A adapter into SQLSmithController
  messenger.py          Template A2A helper
  sqlsmith/
    task.py             Task parsing and SQL extraction
    schema.py           Schema normalization
    planner.py          Deterministic SQL candidates
    validator.py        SELECT-only and identifier validation
    llm.py              Optional OpenAI fallback
    controller.py       Candidate orchestration and JSON result
tests/
  test_agent.py         A2A conformance and SQL artifact smoke
  test_sqlsmith_*.py    Unit tests for the solver core
```

## Local Setup

```powershell
uv sync --extra test
uv run pytest -q tests/test_sqlsmith_task.py tests/test_sqlsmith_schema.py tests/test_sqlsmith_planner.py tests/test_sqlsmith_validator.py tests/test_sqlsmith_controller.py
```

Run the A2A service:

```powershell
uv run python src/server.py --host 127.0.0.1 --port 9009
```

In another shell, run the live A2A conformance tests:

```powershell
uv run pytest -q tests/test_agent.py --agent-url http://127.0.0.1:9009
```

## Configuration

Environment variables:

- `OPENAI_API_KEY` - optional. Enables LLM fallback when the deterministic
  planner does not have a high-confidence candidate.
- `SQLSMITH_OPENAI_MODEL` - optional. Defaults to `gpt-5-mini`.

The deterministic planner and tests do not require network access or API keys.

## Docker

```powershell
docker build -t amadeus-sqlsmith .
docker run --rm -p 9009:9009 amadeus-sqlsmith
```

The AgentBeats manifest points at:

```text
ghcr.io/desalzes/amadeus-sqlsmith:latest
```

Change `amber-manifest.json5` if publishing under a different GitHub owner or
repository name.

## AgentBeats

1. Publish the Docker image to a public registry.
2. Register a purple agent on AgentBeats with the image and repository URL.
3. Submit it against `ashcastelinocs124/text-2-sql-agent`.
4. For local leaderboard testing, use the AgentBeats tutorial flow with
   `scenario.toml` and `generate_compose.py`.

This repo does not auto-submit paid or public assessments. Registration and
submission are operator-controlled.
