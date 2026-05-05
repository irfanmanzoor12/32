# Spec: Tasks MCP Server

> Living document. Add decisions here as they are made. Never leave a decision implied — write it down.

---

## Status: Specced — Ready to Build

Implementation plan: [tasks-mcp-implementation.md](./tasks-mcp-implementation.md)

---

## Decisions Made

| # | Decision | Choice | Reason |
|---|---|---|---|
| 1 | Transport | Streamable HTTP | K8s deployment, multiple agent clients |
| 2 | Session mode | Stateless JSON | Horizontal scaling, K8s-native |
| 3 | Auth | None (first version) | Internal cluster traffic only |
| 4 | Response format | JSON | Agents consume programmatically |
| 5 | Tool naming | `tasks_{intent}` | Intent-based, not resource-based |
| 6 | Tool design | Intent-based | One call = one complete human intent |
| 7 | Storage | In-memory (dict) | Simplest first version, no DB |
| 8 | Task lookup | `id` or `title` search | Agent never needs a separate fetch step |
| 9 | Multi-user | `user_id` optional, default `"default"` | Mock multi-user without auth |
| 10 | Timestamps | UTC, ISO 8601 with `Z` suffix | Consistent across all agents and timezones |

---

## Data Model

```python
Task:
  id          : str       # UUID, auto-generated
  user_id     : str       # optional, default "default"
  title       : str       # required
  description : str       # optional, default ""
  status      : enum      # "todo" | "in_progress" | "done", default "todo"
  priority    : enum      # "low" | "medium" | "high", default "medium"
  due_date    : str|None  # ISO date "YYYY-MM-DD", optional
  created_at  : datetime  # auto-set on create
  updated_at  : datetime  # auto-updated on every change
```

---

## Lookup Behaviour

Every tool that targets an existing task accepts either `id` or `title`. The server resolves internally:

1. If `id` is provided → look up directly.
2. If `title` is provided → exact match first, then case-insensitive match.
3. If multiple tasks match the title → return error: `"Multiple tasks match '{title}'. Use id to be specific."`
4. If no match → return error: `"No task found matching '{title}'."`

The agent never needs a separate fetch step to act on a task.

---

## Tools

---

### `tasks_create`
**Intent:** Add something to do.

**Input:**
| Field | Type | Required | Default |
|---|---|---|---|
| `title` | string | yes | — |
| `user_id` | string | no | `"default"` |
| `description` | string | no | `""` |
| `priority` | `"low"` \| `"medium"` \| `"high"` | no | `"medium"` |
| `due_date` | ISO date string `"YYYY-MM-DD"` | no | `null` |

**Output:**
```json
{
  "id": "uuid",
  "user_id": "default",
  "title": "Buy groceries",
  "description": "",
  "status": "todo",
  "priority": "medium",
  "due_date": "2026-05-06",
  "created_at": "2026-05-05T10:00:00Z",
  "updated_at": "2026-05-05T10:00:00Z"
}
```

**Annotations:** `readOnlyHint: false` · `destructiveHint: false` · `idempotentHint: false`

---

### `tasks_start`
**Intent:** Begin working on a task.

**Input:**
| Field | Type | Required |
|---|---|---|
| `id` | string | one of `id` or `title` required |
| `title` | string | one of `id` or `title` required |

**Behaviour:** Sets `status` → `"in_progress"`, updates `updated_at`.
If already `in_progress` → returns task with message `"Task is already in progress."`.
If already `done` → returns error `"Task is already done. Use tasks_edit to reopen it."`.

**Output:** Updated full task object.

**Annotations:** `readOnlyHint: false` · `destructiveHint: false` · `idempotentHint: false`

---

### `tasks_complete`
**Intent:** Finish a task.

**Input:**
| Field | Type | Required |
|---|---|---|
| `id` | string | one of `id` or `title` required |
| `title` | string | one of `id` or `title` required |

**Behaviour:** Sets `status` → `"done"`, updates `updated_at`.
If already `done` → returns task with message `"Task is already done."`.

**Output:** Updated full task object.

**Annotations:** `readOnlyHint: false` · `destructiveHint: false` · `idempotentHint: true`

---

### `tasks_reschedule`
**Intent:** Change when a task is due.

**Input:**
| Field | Type | Required |
|---|---|---|
| `id` | string | one of `id` or `title` required |
| `title` | string | one of `id` or `title` required |
| `due_date` | ISO date string `"YYYY-MM-DD"` | yes |

**Behaviour:** Updates `due_date`, updates `updated_at`.

**Output:** Updated full task object.

**Annotations:** `readOnlyHint: false` · `destructiveHint: false` · `idempotentHint: false`

---

### `tasks_edit`
**Intent:** Change the title, description, or priority of a task.

**Input:**
| Field | Type | Required |
|---|---|---|
| `id` | string | one of `id` or `title` required |
| `title` | string | one of `id` or `title` required |
| `new_title` | string | no |
| `description` | string | no |
| `priority` | `"low"` \| `"medium"` \| `"high"` | no |

**Behaviour:** Updates only the fields provided. `updated_at` is always refreshed.
At least one of `new_title`, `description`, `priority` must be provided.

**Output:** Updated full task object.

**Annotations:** `readOnlyHint: false` · `destructiveHint: false` · `idempotentHint: false`

---

### `tasks_remove`
**Intent:** Drop a task permanently.

**Input:**
| Field | Type | Required |
|---|---|---|
| `id` | string | one of `id` or `title` required |
| `title` | string | one of `id` or `title` required |

**Behaviour:** Removes task from storage permanently. Not reversible.

**Output:**
```json
{
  "deleted": true,
  "task": { "id": "uuid", "title": "Buy groceries" }
}
```

**Annotations:** `readOnlyHint: false` · `destructiveHint: true` · `idempotentHint: false`

---

### `tasks_query`
**Intent:** See tasks by context — what's pending, what's urgent, what's done.

**Input:**
| Field | Type | Required | Notes |
|---|---|---|---|
| `user_id` | string | no | omit to return tasks for `"default"` user |
| `status` | `"todo"` \| `"in_progress"` \| `"done"` | no | omit to return all |
| `priority` | `"low"` \| `"medium"` \| `"high"` | no | omit to return all |
| `due_today` | boolean | no | if `true`, returns tasks due on today's date |

**Behaviour:** Returns tasks for the given `user_id` (defaults to `"default"`). Additional filters are AND-ed together.
If no filters provided, returns all tasks for that user.

**Output:**
```json
{
  "tasks": [ ...task objects... ],
  "total_count": 3
}
```

**Annotations:** `readOnlyHint: true` · `destructiveHint: false` · `idempotentHint: true`

---

## Error Format

All errors return:
```json
{
  "error": true,
  "message": "Human-readable explanation with a suggested next step."
}
```

Errors are returned as tool result content, never as protocol-level failures.

---

## Deployment

- Language: Python 3.12+, package manager: `uv`
- Framework: FastMCP
- Runs as a K8s Deployment
- Exposed via K8s Service (internal DNS: `tasks-mcp-svc`)
- Config via environment variables / ConfigMap
- Health check: `GET /health`
