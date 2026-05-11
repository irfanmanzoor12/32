import json
import pytest
from tasks_mcp.models import Task, RescheduleInput
from tasks_mcp.store import TaskStore
from tasks_mcp.tools.reschedule import reschedule_task


@pytest.fixture
def store():
    s = TaskStore()
    s.add(Task(title="Report", user_id="u1"))
    return s


async def test_reschedule_updates_due_date(store):
    inp = RescheduleInput(title="Report", due_date="2026-06-01")
    result = json.loads(await reschedule_task(inp, store, user_id="u1"))
    assert result["due_date"] == "2026-06-01"


async def test_reschedule_updates_updated_at(store):
    task = store.resolve(id=None, title="Report", user_id="u1")
    original = task.updated_at
    inp = RescheduleInput(title="Report", due_date="2026-06-01")
    result = json.loads(await reschedule_task(inp, store, user_id="u1"))
    assert result["updated_at"].endswith("Z")


async def test_reschedule_not_found(store):
    inp = RescheduleInput(title="Ghost", due_date="2026-06-01")
    result = json.loads(await reschedule_task(inp, store, user_id="u1"))
    assert result["error"] is True
