# Tasks Management System

A multi-agent AI system that lets users manage tasks and book appointments through natural language. Built with the OpenAI Agents SDK, a custom MCP server, FastAPI, and Next.js — deployed on Kubernetes.

---

## What It Does

You tell it things like:

> "Add an 8 pm reminder for friends meetup"
> "Book a meeting with the team on Friday"
> "Delete all tasks for tomorrow"

The system understands your intent, manages your tasks, handles bookings, and sends you notifications — all automatically.

---

## Architecture

```
User
 └── Tasks Manager Agent        (understands and routes requests)
      ├── Tasks MCP Server       (add / update / delete tasks)
      │    └── Notifications API (sends alerts and reminders)
      └── Appointment Booking Agent (captures bookings → Google Sheets)
```

| Layer | Technology |
|---|---|
| Agent framework | OpenAI Agents SDK |
| MCP server | Python MCP SDK |
| Notifications API | FastAPI |
| Authentication | Better Auth |
| Frontend | Next.js 16 |
| Deployment | Kubernetes |

---

## Project Structure

```
/
├── agents/
│   ├── tasks-manager/        # Main agent — talks to users
│   └── appointment-booking/  # Books appointments, logs to Google Sheets
├── mcp/
│   └── tasks-mcp/            # MCP server: add, update, delete tasks
├── api/
│   └── notifications/        # FastAPI service for sending notifications
├── ui/                       # Next.js 16 frontend
├── k8s/                      # Kubernetes manifests for all services
└── CLAUDE.md                 # How we build this project
```

---

## How We Build It

- **Test-driven** — tests are written before the implementation
- **Docs-first** — official SDK/framework docs are checked before every implementation
- **K8s-native** — every service is containerized and has a K8s manifest from day one
- **Observable** — structured logging and health checks on every service
- **Secure** — secrets managed via Kubernetes Secrets, never hardcoded

See [CLAUDE.md](./CLAUDE.md) for the full working principles.

---

## Getting Started

> Setup instructions will be added as each component is built.

---

## Status

Currently in initial setup. Components being built iteratively.
