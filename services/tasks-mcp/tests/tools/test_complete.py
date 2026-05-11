import json
import pytest
from tasks_mcp.models import Task, LookupInput, Status
from tasks_mcp.store import TaskStore
from tasks_mcp.tools.complete import complete_task


@pytest.fixture
def store():
    s = TaskStore()
    s.add(Task(title="Buy groceries", user_id="u1", status=Status.IN_PROGRESS))
    return s


async def test_complete_sets_done(store):
    inp = LookupInput(title="Buy groceries")
    result = json.loads(await complete_task(inp, store, user_id="u1"))
    assert result["status"] == "done"


async def test_complete_already_done(store):
    inp = LookupInput(title="Buy groceries")
    await complete_task(inp, store, user_id="u1")
    result = json.loads(await complete_task(inp, store, user_id="u1"))
    assert result["status"] == "done"
    assert "already done" in result["message"]


async def test_complete_not_found(store):
    inp = LookupInput(title="Ghost task")
    result = json.loads(await complete_task(inp, store, user_id="u1"))
    assert result["error"] is True
