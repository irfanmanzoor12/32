import json
import pytest
from tasks_mcp.models import Task, EditInput, Priority
from tasks_mcp.store import TaskStore
from tasks_mcp.tools.edit import edit_task


@pytest.fixture
def store():
    s = TaskStore()
    s.add(Task(title="Report", user_id="u1", description="Old desc", priority=Priority.LOW))
    return s


async def test_edit_title(store):
    inp = EditInput(title="Report", new_title="Final Report")
    result = json.loads(await edit_task(inp, store, user_id="u1"))
    assert result["title"] == "Final Report"


async def test_edit_description(store):
    inp = EditInput(title="Report", description="New desc")
    result = json.loads(await edit_task(inp, store, user_id="u1"))
    assert result["description"] == "New desc"


async def test_edit_priority(store):
    inp = EditInput(title="Report", priority=Priority.HIGH)
    result = json.loads(await edit_task(inp, store, user_id="u1"))
    assert result["priority"] == "high"


async def test_edit_only_provided_fields_change(store):
    inp = EditInput(title="Report", priority=Priority.HIGH)
    result = json.loads(await edit_task(inp, store, user_id="u1"))
    assert result["title"] == "Report"
    assert result["description"] == "Old desc"


async def test_edit_no_fields_returns_error(store):
    inp = EditInput(title="Report")
    result = json.loads(await edit_task(inp, store, user_id="u1"))
    assert result["error"] is True


async def test_edit_not_found(store):
    inp = EditInput(title="Ghost", new_title="X")
    result = json.loads(await edit_task(inp, store, user_id="u1"))
    assert result["error"] is True
