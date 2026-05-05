# Implementation Plan: Tasks MCP Server

> No code. This document specifies exactly how we will build, test, and verify the server before marking it done.

---

## Location

```
mcp/tasks-mcp/
```

---

## Project Setup (uv)

```
mcp/tasks-mcp/
├── pyproject.toml        # dependencies, project metadata
├── uv.lock               # lockfile — committed
├── src/
│   └── tasks_mcp/
│       ├── __init__.py
│       ├── server.py     # FastMCP init + tool registration + health endpoint
│       ├── models.py     # Task dataclass, enums, Pydantic input models
│       ├── store.py      # in-memory storage + lookup logic
│       └── tools/
│           ├── __init__.py
│           ├── create.py
│           ├── start.py
│           ├── complete.py
│           ├── reschedule.py
│           ├── edit.py
│           ├── remove.py
│           └── query.py
└── tests/
    ├── conftest.py       # shared fixtures: fresh store, test client
    ├── test_models.py
    ├── test_store.py
    └── tools/
        ├── test_create.py
        ├── test_start.py
        ├── test_complete.py
        ├── test_reschedule.py
        ├── test_edit.py
        ├── test_remove.py
        └── test_query.py
```

---

## Dependencies

```
Runtime:
  mcp[cli]     — FastMCP framework
  pydantic     — input validation (v2)

Dev/Test:
  pytest
  pytest-asyncio   — async test support
```

Installed with:
```bash
uv init tasks-mcp
uv add mcp[cli] pydantic
uv add --dev pytest pytest-asyncio
```

---

## Key Implementation Decisions

| Concern | Decision |
|---|---|
| Timestamps | `datetime.now(timezone.utc)` — always UTC, stored as ISO 8601 with `Z` suffix |
| Server name | `tasks_mcp` |
| Transport | `streamable_http`, port `8000` |
| In-memory store | `dict[str, Task]` keyed by `id` — lives in `store.py` |
| Lookup resolver | shared function in `store.py` used by every tool — resolves `id` or `title`, raises on ambiguity |
| All tools | `async def` |
| Input models | Pydantic v2 `BaseModel` with `ConfigDict(extra='forbid', str_strip_whitespace=True)` |
| Error returns | JSON string `{"error": true, "message": "..."}` — never raise at protocol level |

---

## Module Responsibilities

### `models.py`
- `Status` enum: `todo`, `in_progress`, `done`
- `Priority` enum: `low`, `medium`, `high`
- `Task` dataclass with all fields
- Pydantic input model for each tool (one model per tool)

### `store.py`
- `TaskStore` class wrapping a `dict[str, Task]`
- Methods: `add`, `get`, `update`, `delete`, `list`
- `resolve(id, title, user_id)` — shared lookup used by all mutation tools:
  1. If `id` given → return task or raise not-found
  2. If `title` given → search within user's tasks, exact then case-insensitive
  3. Multiple matches → raise ambiguity error
  4. No match → raise not-found error

### `tools/`
- One file per tool
- Each file exports a single async function
- Function receives validated Pydantic input + `store: TaskStore`
- Returns `str` (JSON)

### `server.py`
- Initialises `FastMCP("tasks_mcp")`
- Creates one shared `TaskStore` instance via lifespan
- Registers all 7 tools using `@mcp.tool`
- Registers `GET /health` → `{"status": "ok"}`
- Entry point: `mcp.run(transport="streamable_http", port=8000)`

---

## TDD Order

We build bottom-up. Each layer is tested before the layer above it is written.

### Step 1 — Models (`test_models.py`)
Tests to write first:
- Task can be created with required fields only — defaults fill the rest
- `created_at` and `updated_at` are UTC
- `status` defaults to `todo`, `priority` defaults to `medium`
- `user_id` defaults to `"default"`
- Invalid status or priority value raises validation error

### Step 2 — Store (`test_store.py`)
Tests to write first:
- `add` stores a task and returns it
- `get` returns task by id, raises on missing id
- `resolve` by exact title returns correct task
- `resolve` by case-insensitive title returns correct task
- `resolve` with ambiguous title raises with helpful message
- `resolve` with unknown title raises not-found
- `delete` removes task, second delete raises not-found
- `list` with no filter returns all tasks for user
- `list` with status filter returns only matching tasks

### Step 3 — Tools (one file at a time, Red → Green → Refactor)

Each tool test file covers:
1. **Happy path** — valid input, correct output shape
2. **Not found** — task doesn't exist
3. **Ambiguous title** — multiple matches
4. **Invalid state** — e.g. completing an already-done task

| File | Key edge cases to test |
|---|---|
| `test_create.py` | defaults applied, UTC timestamps, user_id fallback |
| `test_start.py` | already in_progress, already done |
| `test_complete.py` | already done (idempotent message) |
| `test_reschedule.py` | invalid date format rejected |
| `test_edit.py` | no fields provided → error, only provided fields change |
| `test_remove.py` | returns deleted task snapshot, second remove fails |
| `test_query.py` | no filters returns all, AND of filters, due_today matches date |

### Step 4 — Server registration (`server.py`)
- Tools are registered and callable via FastMCP
- Lifespan injects shared store into all tools
- `/health` returns `{"status": "ok"}`

---

## End-to-End Verification (before declaring done)

Run the server:
```bash
cd mcp/tasks-mcp
uv run python -m tasks_mcp
```

Connect MCP Inspector:
```bash
npx @modelcontextprotocol/inspector http://localhost:8000
```

Walk through every tool manually in this order — this is the human live test:

| # | Action | Tool | Verify |
|---|---|---|---|
| 1 | Create "Buy groceries" | `tasks_create` | Returns task with id, UTC timestamps, status=todo |
| 2 | Create "Write report" with priority=high | `tasks_create` | priority=high in response |
| 3 | Query all tasks | `tasks_query` | Both tasks returned |
| 4 | Start "Buy groceries" by title | `tasks_start` | status=in_progress |
| 5 | Start same task again | `tasks_start` | Returns task + "already in progress" message |
| 6 | Complete "Buy groceries" by title | `tasks_complete` | status=done |
| 7 | Complete same task again | `tasks_complete` | Idempotent — returns task + "already done" message |
| 8 | Reschedule "Write report" to next week | `tasks_reschedule` | due_date updated |
| 9 | Edit "Write report" — change priority to low | `tasks_edit` | Only priority changed, title unchanged |
| 10 | Query by status=done | `tasks_query` | Only "Buy groceries" returned |
| 11 | Query by priority=low | `tasks_query` | Only "Write report" returned |
| 12 | Remove "Write report" by title | `tasks_remove` | Returns deleted snapshot |
| 13 | Query all tasks | `tasks_query` | Only "Buy groceries" remains |
| 14 | Try to remove "Write report" again | `tasks_remove` | Not-found error returned |
| 15 | GET /health | HTTP | `{"status": "ok"}` |

All 15 checks must pass before the implementation is considered done.

---

## Definition of Done (this component)

- [ ] All unit tests pass (`uv run pytest`)
- [ ] Server starts without errors
- [ ] All 15 live checks pass via MCP Inspector
- [ ] No secrets hardcoded
- [ ] `Dockerfile` written alongside the code
- [ ] `k8s/mcp/` manifest written
- [ ] `/health` endpoint responds
- [ ] Timestamps are UTC throughout
