# Tasks Management System — Constitution

## Project Overview

A multi-agent Tasks Management System where users interact in natural language to manage tasks and book appointments. The system is composed of:

- **Tasks Manager Agent** — central agent, interacts with users (OpenAI Agents SDK)
- **Tasks MCP Server** — exposes add, update, delete task tools (Python MCP SDK)
- **Appointment Booking Agent** — captures booking intent, records to Google Sheets (OpenAI Agents SDK)
- **Notifications API** — sends notifications (FastAPI)
- **Auth Layer** — authentication (Better Auth)
- **UI** — frontend (Next.js 16)

All components are designed and deployed on **Kubernetes (K8s)** from day one.

---

## How We Work

### 1. Docs First
Before writing any code for a library, SDK, or framework — check the official documentation. Use agent skills or MCP tools to fetch and read the latest docs. Never assume API signatures from memory; always verify against the current version.

### 2. Test-Driven Development (TDD)
- Write the test before writing the implementation.
- Red → Green → Refactor is the development loop.
- Every feature, tool, and agent behavior must have a corresponding test.
- Tests are not optional and are never deferred to "later."

### 3. K8s-Native from Day One
Every component is built assuming it will run in Kubernetes:
- Services communicate via internal DNS, not localhost.
- Configuration comes from environment variables and K8s ConfigMaps/Secrets — never hardcoded.
- Each component is stateless where possible; state lives in external stores.
- Write Dockerfiles and K8s manifests (Deployment, Service, Ingress) alongside the code, not after.
- Design for horizontal scaling from the start.

### 4. Small, Focused Components
- Each agent, service, and MCP tool does one thing well.
- No component should need to know the internals of another — communicate through defined interfaces.
- Avoid premature abstractions; build what is needed now.

### 5. Iterative Delivery
- Build the thinnest working slice first, then expand.
- Each iteration must be runnable and testable end-to-end.
- Don't design for hypothetical future requirements.

### 6. Security by Default
- Secrets never appear in code or logs.
- Auth is applied at the edge (ingress/gateway), not scattered across services.
- Validate all external input at system boundaries.

### 7. Observability from the Start
- Every service logs structured output (JSON).
- Key agent actions and tool calls are traced.
- Health check endpoints (`/health`) are mandatory on every HTTP service.

---

## Stack & Official Docs

| Component | Technology | Official Docs |
|---|---|---|
| Agent framework | OpenAI Agents SDK (Python) | https://openai.github.io/openai-agents-python/ |
| MCP server | Python MCP SDK | https://github.com/modelcontextprotocol/python-sdk |
| Notifications API | FastAPI | https://fastapi.tiangolo.com |
| Auth | Better Auth | https://www.better-auth.com |
| UI | Next.js 16 | https://nextjs.org/docs |
| Container runtime | Docker | https://docs.docker.com |
| Orchestration | Kubernetes | https://kubernetes.io/docs |

Always pull the latest docs before implementing a feature in any of the above.

---

## Folder Structure (Target)

```
/
├── agents/
│   ├── tasks-manager/       # Tasks Manager Agent
│   └── appointment-booking/ # Appointment Booking Agent
├── mcp/
│   └── tasks-mcp/           # MCP server (add/update/delete tasks)
├── api/
│   └── notifications/       # FastAPI Notifications API
├── ui/                      # Next.js 16 frontend
├── k8s/                     # Kubernetes manifests for all components
│   ├── agents/
│   ├── mcp/
│   ├── api/
│   └── ui/
└── CLAUDE.md
```

---

## Definition of Done

A feature is done when:
1. Tests are written and passing.
2. The component runs in a Docker container locally.
3. A K8s manifest exists for it.
4. It is observable (logs, health check).
5. No secrets are hardcoded.
