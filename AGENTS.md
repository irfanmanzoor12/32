# AGENTS.md — How We Work

This is our constitution. It defines how every agent, developer, and AI assistant on this project must think and work — not what to build, but how to build it.

---

## 1. Docs Before Code

Before using any SDK, framework, or library — fetch and read its official documentation first.

Do not rely on memory or training data for API signatures. Use agent skills or MCP tools to retrieve the latest docs at the time of implementation. If the docs have changed, the code must reflect the current version — not what was true six months ago.

This applies to everything: the agent framework, the MCP SDK, the API library, the auth system, the UI framework, and Kubernetes itself.

---

## 2. Test-Driven Development

We write the test before we write the code. Always.

The cycle is:
1. Write a failing test that describes the behavior you need.
2. Write the minimum code to make it pass.
3. Refactor without breaking it.

No feature ships without a test. No tool, agent behavior, or API endpoint is considered implemented until it has a corresponding test that verifies it works. "I'll add tests later" does not exist here.

---

## 3. Everything Runs on Kubernetes

This system does not run on localhost. From the first line of code, every component is designed assuming it will run inside a Kubernetes cluster.

This means:
- Services talk to each other over internal cluster DNS, not local ports.
- Configuration comes from environment variables, ConfigMaps, and Secrets — never hardcoded values.
- Every component is stateless by default; persistent state belongs in an external store.
- A Dockerfile and a Kubernetes manifest are written alongside the code, not after it ships.
- We design for horizontal scaling from day one, not as an afterthought.

If it does not run in a container and cannot be described by a K8s manifest, it is not done.

---

## 4. Small, Focused Components

Each agent, service, and tool does one thing and does it well.

No component reaches into the internals of another. They communicate through clearly defined interfaces. If two components need to share logic, that is a signal to define a proper interface — not to merge them or create a shortcut.

Build what is needed now. Do not design for hypothetical future requirements.

---

## 5. Security Is Not an Afterthought

Secrets never appear in code, configuration files, or logs. Authentication and authorization are enforced at the edge — at the ingress or gateway level — not scattered across individual services.

Every input that crosses a system boundary is validated. Trust nothing that comes from outside.

---

## 6. Observable by Default

Every service exposes a `/health` endpoint. Every service logs in structured JSON. Key agent decisions, tool calls, and handoffs are traced.

If something breaks in production and you cannot diagnose it from logs and traces alone, the service is not observable enough. Fix that before shipping.

---

## 7. Iterate in Thin Slices

Build the smallest thing that works end-to-end first, then expand. Each iteration must be runnable, testable, and demonstrable on its own.

A thick design that cannot be exercised is not progress. A thin slice that runs is.
