# AGENTS.md — How We Work

This is our constitution. It defines how every agent, developer, and AI assistant on this project must think and work — not what to build, but how to build it.

---

## 1. Always Verify What You Are Doing

Before taking any action, confirm you understand what it will do and why. Do not assume. Do not guess.

- Before writing code, verify you have read the relevant files and understand the current state.
- Before calling a tool, verify its inputs are correct and the action is reversible or intentional.
- Before marking anything done, verify it actually works — run it, test it, inspect the output.
- When something is unclear, stop and ask rather than proceed on a false assumption.

Verification is not optional overhead. An unverified action that goes wrong costs more than the time it would have taken to check.

---

## 2. Docs Before Code

Before using any SDK, framework, or library — fetch and read its official documentation first.

Do not rely on memory or training data for API signatures. Use agent skills or MCP tools to retrieve the latest docs at the time of implementation. If the docs have changed, the code must reflect the current version — not what was true six months ago.

This applies to everything: the agent framework, the MCP SDK, the API library, the auth system, the UI framework, and Kubernetes itself.

---

## 3. Test-Driven Development

We write the test before we write the code. Always.

The cycle is:
1. Write a failing test that describes the behavior you need.
2. Write the minimum code to make it pass.
3. Refactor without breaking it.

No feature ships without a test. No tool, agent behavior, or API endpoint is considered implemented until it has a corresponding test that verifies it works. "I'll add tests later" does not exist here.

---

## 4. Everything Runs on Kubernetes

This system does not run on localhost. From the first line of code, every component is designed assuming it will run inside a Kubernetes cluster.

This means:
- Services talk to each other over internal cluster DNS — never local ports.
- Configuration comes from environment variables, ConfigMaps, and Secrets — never hardcoded values.
- Every component is stateless by default; persistent state belongs in an external store.
- A Dockerfile and a Kubernetes manifest are written alongside the code — not after.
- We design for horizontal scaling from day one, not as an afterthought.

If it does not run in a container and cannot be described by a K8s manifest, it is not done.

---

## 5. Multi-Agent Thinking

This system is built from multiple agents that coordinate. Every design decision must account for how agents divide work, share findings, and avoid conflicts.

### Decompose before you act

Complex problems are broken into focused, parallel workstreams before any agent starts working. A single agent juggling multiple specialties produces shallow work because context degrades. Assign one specialty per agent; let them investigate simultaneously.

### Competing hypotheses over single-thread investigation

When root cause is unclear, spawn multiple agents to investigate different theories in parallel and have them challenge each other's findings. A single investigator finds one plausible explanation and stops looking. Parallel investigators who actively try to disprove each other surface the answer that actually survives scrutiny.

### The coordinator never implements

The lead agent coordinates: it creates tasks, assigns work, and synthesizes results. It does not conduct research or write deliverables itself. If the lead is doing the work, the team structure has failed.

### Plan before executing

For consequential work, an agent must present its plan — approach, scope, data sources — and receive approval before spending resources on execution. Review the plan, not just the output.

### Task dependencies must be explicit

When work is sequential, structure it with explicit dependencies. A downstream task does not start until its upstream dependency is marked complete. Never have agents assume a predecessor is done; encode it.

### Shared documents for shared findings

Agents write findings to shared files, not just messages. Messages live in one agent's context and disappear. A shared file persists, is readable by any agent, and produces a permanent record. Assign section ownership explicitly to avoid agents overwriting each other.

### Context is not inherited — make it explicit

A new agent or teammate does not inherit the conversation history of the agent that spawned it. Any context it needs — conventions, prior decisions, constraints — must be stated explicitly in the spawn prompt or in a shared project file like this one.

### Choose the right model for the right job

Use the strongest model for synthesis and judgment. Use efficient models for research and data gathering. The teammates do the bulk investigative work; the lead synthesizes. This delivers depth where it matters without overspending on routine tasks.

### Use subagents for reporting; use teams when agents must talk

If agents only report back to a caller, subagents are sufficient. If agents need to share findings with each other, challenge assumptions across specialties, or coordinate across functions — that is a team. Apply the right pattern to the complexity of the problem.

---

## 6. Small, Focused Components

Each agent, service, and tool does one thing and does it well.

No component reaches into the internals of another. They communicate through clearly defined interfaces. If two components need to share logic, that is a signal to define a proper interface — not to merge them or create a shortcut.

Build what is needed now. Do not design for hypothetical future requirements.

---

## 7. Security Is Not an Afterthought

Secrets never appear in code, configuration files, or logs. Authentication and authorization are enforced at the edge — at the ingress or gateway level — not scattered across individual services.

Every input that crosses a system boundary is validated. Trust nothing that comes from outside.

---

## 8. Observable by Default

Every service exposes a `/health` endpoint. Every service logs in structured JSON. Key agent decisions, tool calls, and handoffs are traced.

If something breaks in production and you cannot diagnose it from logs and traces alone, the service is not observable enough. Fix that before shipping.

---

## 9. Python Standards

All Python components in this project use **Python 3.12+** and **`uv`** as the package manager. No exceptions.

- Use `uv` to create virtual environments, add dependencies, and run scripts — not `pip`, `poetry`, or `pipenv`.
- Pin dependencies in `pyproject.toml`. Lock with `uv.lock`.
- Never commit a `requirements.txt` generated by `pip freeze`; let `uv` manage the lockfile.

```bash
uv init          # initialise a new component
uv add <pkg>     # add a dependency
uv run pytest    # run tests inside the managed environment
```

---

## 10. Iterate in Thin Slices

Build the smallest thing that works end-to-end first, then expand. Each iteration must be runnable, testable, and demonstrable on its own.

A thick design that cannot be exercised is not progress. A thin slice that runs is.
