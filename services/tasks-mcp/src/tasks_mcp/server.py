import os
from contextlib import asynccontextmanager
from typing import Optional
from mcp.server.fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

from tasks_mcp.models import (
    CreateInput, LookupInput, RescheduleInput, EditInput, QueryInput, Priority, Status
)
from tasks_mcp.store import TaskStore
from tasks_mcp.tools.create import create_task
from tasks_mcp.tools.start import start_task
from tasks_mcp.tools.complete import complete_task
from tasks_mcp.tools.reschedule import reschedule_task
from tasks_mcp.tools.edit import edit_task
from tasks_mcp.tools.remove import remove_task
from tasks_mcp.tools.query import query_tasks

_store = TaskStore()


@asynccontextmanager
async def lifespan(server: FastMCP):
    yield {"store": _store}


mcp = FastMCP(
    "tasks_mcp",
    lifespan=lifespan,
    host=os.getenv("MCP_HOST", "127.0.0.1"),
    port=int(os.getenv("MCP_PORT", "8000")),
)


@mcp.tool(
    name="tasks_create",
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False},
)
async def tool_create(
    title: str,
    user_id: str = "default",
    description: str = "",
    priority: str = "medium",
    due_date: Optional[str] = None,
) -> str:
    """Create a new task. Returns the created task with its generated id."""
    inp = CreateInput(
        title=title, user_id=user_id, description=description,
        priority=Priority(priority), due_date=due_date,
    )
    return await create_task(inp, _store)


@mcp.tool(
    name="tasks_start",
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False},
)
async def tool_start(
    user_id: str = "default",
    id: Optional[str] = None,
    title: Optional[str] = None,
) -> str:
    """Begin working on a task. Sets status to in_progress. Provide id or title."""
    inp = LookupInput(id=id, title=title)
    return await start_task(inp, _store, user_id=user_id)


@mcp.tool(
    name="tasks_complete",
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True},
)
async def tool_complete(
    user_id: str = "default",
    id: Optional[str] = None,
    title: Optional[str] = None,
) -> str:
    """Mark a task as done. Provide id or title."""
    inp = LookupInput(id=id, title=title)
    return await complete_task(inp, _store, user_id=user_id)


@mcp.tool(
    name="tasks_reschedule",
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False},
)
async def tool_reschedule(
    due_date: str,
    user_id: str = "default",
    id: Optional[str] = None,
    title: Optional[str] = None,
) -> str:
    """Change the due date of a task. Provide id or title, and new due_date (YYYY-MM-DD)."""
    inp = RescheduleInput(id=id, title=title, due_date=due_date)
    return await reschedule_task(inp, _store, user_id=user_id)


@mcp.tool(
    name="tasks_edit",
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False},
)
async def tool_edit(
    user_id: str = "default",
    id: Optional[str] = None,
    title: Optional[str] = None,
    new_title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None,
) -> str:
    """Edit title, description, or priority. Only provided fields are changed."""
    inp = EditInput(
        id=id, title=title, new_title=new_title,
        description=description,
        priority=Priority(priority) if priority else None,
    )
    return await edit_task(inp, _store, user_id=user_id)


@mcp.tool(
    name="tasks_remove",
    annotations={"readOnlyHint": False, "destructiveHint": True, "idempotentHint": False},
)
async def tool_remove(
    user_id: str = "default",
    id: Optional[str] = None,
    title: Optional[str] = None,
) -> str:
    """Permanently delete a task. Not reversible. Provide id or title."""
    inp = LookupInput(id=id, title=title)
    return await remove_task(inp, _store, user_id=user_id)


@mcp.tool(
    name="tasks_query",
    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True},
)
async def tool_query(
    user_id: str = "default",
    status: Optional[str] = None,
    priority: Optional[str] = None,
    due_today: bool = False,
) -> str:
    """Query tasks. Filter by status, priority, or due_today. Returns list + total_count."""
    inp = QueryInput(
        user_id=user_id,
        status=Status(status) if status else None,
        priority=Priority(priority) if priority else None,
        due_today=due_today,
    )
    return await query_tasks(inp, _store)


@mcp.custom_route("/health", methods=["GET"])
async def health(request: Request) -> JSONResponse:
    return JSONResponse({"status": "ok"})


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
