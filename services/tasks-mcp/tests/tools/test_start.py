import json
import pytest
from tasks_mcp.models import Task, LookupInput, Status
from tasks_mcp.store import TaskStore
from tasks_mcp.tools.start import start_task


@pytest.fixture
def store():
    s = TaskStore()
    s.add(Task(title="Buy groceries", user_id="u1"))
    return s


async def test_start_sets_in_progress(store):
    inp = LookupInput(title="Buy groceries")
    result = json.loads(await start_task(inp, store, user_id="u1"))
    assert result["status"] == "in_progress"


async def test_start_already_in_progress(store):
    inp = LookupInput(title="Buy groceries")
    await start_task(inp, store, user_id="u1")
    result = json.loads(await start_task(inp, store, user_id="u1"))
    assert result["status"] == "in_progress"
    assert "already in progress" in result["message"]


async def test_start_already_done(store):
    task = store.resolve(id=None, title="Buy groceries", user_id="u1")
    task.status = Status.DONE
    inp = LookupInput(title="Buy groceries")
    result = json.loads(await start_task(inp, store, user_id="u1"))
    assert result["error"] is True
    assert "already done" in result["message"]


async def test_start_not_found(store):
    inp = LookupInput(title="Nonexistent")
    result = json.loads(await start_task(inp, store, user_id="u1"))
    assert result["error"] is True
