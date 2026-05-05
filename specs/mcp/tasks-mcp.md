# Spec: Tasks MCP Server

> Living document. Add decisions here as they are made. Never leave a decision implied — write it down.

---

## Status: In Design

---

## Decisions Made

| # | Decision | Choice | Reason |
|---|---|---|---|
| 1 | Transport | Streamable HTTP | K8s deployment, multiple agent clients |
| 2 | Session mode | Stateless JSON | Horizontal scaling, K8s-native |
| 3 | Auth | None (first version) | Internal cluster traffic only |
| 4 | Response format | JSON | Agents consume programmatically |
| 5 | Tool naming | `tasks_{action}_{resource}` | Avoid collision with other MCP servers |
| 6 | Tool set | 5 tools (see below) | Minimal complete set for agents to do real work |

---

## Decisions Pending

- [ ] Task data model — what fields does a task have
- [ ] Storage backend — where tasks live

---

## Tools

### `tasks_add_task`
Creates a new task.

### `tasks_update_task`
Updates any fields on an existing task by ID. Only the fields provided are changed.

### `tasks_delete_task`
Deletes a task by ID.

### `tasks_list_tasks`
Returns all tasks. Supports optional filters.

### `tasks_get_task`
Returns a single task by ID.

---

## Data Model

> To be defined after storage is agreed.

---

## Storage

> To be defined.

---

## Deployment

- Runs as a K8s Deployment
- Exposed via K8s Service (internal DNS: `tasks-mcp-svc`)
- Config via environment variables / ConfigMap
- Health check: `GET /health`
