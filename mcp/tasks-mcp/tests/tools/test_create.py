import json
import pytest
from tasks_mcp.models import CreateInput, Priority, Status
from tasks_mcp.store import TaskStore
from tasks_mcp.tools.create import create_task


@pytest.fixture
def store():
    return TaskStore()


async def test_create_returns_task(store):
    inp = CreateInput(title="Buy groceries")
    result = json.loads(await create_task(inp, store))
    assert result["title"] == "Buy groceries"
    assert result["status"] == "todo"
    assert result["priority"] == "medium"
    assert result["user_id"] == "default"
    assert "id" in result


async def test_create_applies_defaults(store):
    inp = CreateInput(title="Task")
    result = json.loads(await create_task(inp, store))
    assert result["description"] == ""
    assert result["due_date"] is None


async def test_create_with_all_fields(store):
    inp = CreateInput(
        title="Report",
        user_id="u1",
        description="Write it",
        priority=Priority.HIGH,
        due_date="2026-05-10",
    )
    result = json.loads(await create_task(inp, store))
    assert result["user_id"] == "u1"
    assert result["priority"] == "high"
    assert result["due_date"] == "2026-05-10"


async def test_create_timestamps_utc(store):
    inp = CreateInput(title="Task")
    result = json.loads(await create_task(inp, store))
    assert result["created_at"].endswith("Z")
    assert result["updated_at"].endswith("Z")


async def test_create_stores_task(store):
    inp = CreateInput(title="Stored task")
    result = json.loads(await create_task(inp, store))
    fetched = store.get(result["id"])
    assert fetched.title == "Stored task"
