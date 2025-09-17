Project approach and conventions

- Tooling
  - Use `uv` for project scaffolding, dependency management, running commands, and virtualenvs.
  - Python >= 3.9. Formatting via ruff default rules; type-check with mypy (settings in `pyproject.toml`).

- Architecture
  - HTTP via `httpx` with retries/backoff for `429` and `5xx`. Raise `DPDHTTPError` for `4xx`.
  - Models via `pydantic` v2. Allow extra fields for forward-compat.
  - Public client methods return lists of models; normalize single-object responses.
  - Optional in-memory caching: pass `cache_ttl` (seconds) to clients.
  - CLI via `typer`; commands mirror client methods.

- Testing
  - Use `pytest` with `respx` to mock HTTP calls; avoid real network usage.
  - Async tests use `pytest-asyncio`. Keep tests small and focused.

- Versioning and releases
  - Maintain `CHANGELOG.md` for every substantive change.
  - Update version in `pyproject.toml` when preparing a release; keep entries concise and dated.
  - Do not publish without explicit approval.
  - Use `uv run python scripts/release.py [--version X.Y.Z] [--publish]` to run the release checklist (loads `.env`, lint, type-check, tests, build, publish).

- General
  - Keep changes minimal and focused on the task.
  - Prefer explicit parameters mapped to API docs; default `lang='en'`, `type='json'`.
  - Avoid adding unrelated features; call out issues separately if found.
