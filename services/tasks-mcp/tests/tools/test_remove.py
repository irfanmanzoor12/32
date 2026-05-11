import json
import pytest
from tasks_mcp.models import Task, LookupInput
from tasks_mcp.store import TaskStore, NotFoundError
from tasks_mcp.tools.remove import remove_task


@pytest.fixture
def store():
    s = TaskStore()
    s.add(Task(title="Buy groceries", user_id="u1"))
    return s


async def test_remove_returns_deleted_snapshot(store):
    inp = LookupInput(title="Buy groceries")
    result = json.loads(await remove_task(inp, store, user_id="u1"))
    assert result["deleted"] is True
    assert result["task"]["title"] == "Buy groceries"


async def test_remove_deletes_from_store(store):
    task = store.resolve(id=None, title="Buy groceries", user_id="u1")
    inp = LookupInput(title="Buy groceries")
    await remove_task(inp, store, user_id="u1")
    with pytest.raises(NotFoundError):
        store.get(task.id)


async def test_remove_second_call_returns_error(store):
    inp = LookupInput(title="Buy groceries")
    await remove_task(inp, store, user_id="u1")
    result = json.loads(await remove_task(inp, store, user_id="u1"))
    assert result["error"] is True


async def test_remove_not_found(store):
    inp = LookupInput(title="Ghost")
    result = json.loads(await remove_task(inp, store, user_id="u1"))
    assert result["error"] is True
