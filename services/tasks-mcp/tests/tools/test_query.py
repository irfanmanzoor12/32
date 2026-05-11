import json
import pytest
from datetime import datetime, timezone
from tasks_mcp.models import Task, QueryInput, Status, Priority
from tasks_mcp.store import TaskStore
from tasks_mcp.tools.query import query_tasks


@pytest.fixture
def store():
    s = TaskStore()
    s.add(Task(title="A", user_id="u1", status=Status.TODO, priority=Priority.HIGH))
    s.add(Task(title="B", user_id="u1", status=Status.DONE, priority=Priority.LOW))
    s.add(Task(title="C", user_id="u2", status=Status.TODO, priority=Priority.HIGH))
    return s


async def test_query_all_for_user(store):
    inp = QueryInput(user_id="u1")
    result = json.loads(await query_tasks(inp, store))
    assert result["total_count"] == 2


async def test_query_filter_status(store):
    inp = QueryInput(user_id="u1", status=Status.DONE)
    result = json.loads(await query_tasks(inp, store))
    assert result["total_count"] == 1
    assert result["tasks"][0]["title"] == "B"


async def test_query_filter_priority(store):
    inp = QueryInput(user_id="u1", priority=Priority.HIGH)
    result = json.loads(await query_tasks(inp, store))
    assert result["total_count"] == 1
    assert result["tasks"][0]["title"] == "A"


async def test_query_due_today(store):
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    store.add(Task(title="Due today", user_id="u1", due_date=today))
    inp = QueryInput(user_id="u1", due_today=True)
    result = json.loads(await query_tasks(inp, store))
    assert result["total_count"] == 1
    assert result["tasks"][0]["title"] == "Due today"


async def test_query_default_user(store):
    store.add(Task(title="Default user task", user_id="default"))
    inp = QueryInput()
    result = json.loads(await query_tasks(inp, store))
    assert result["total_count"] == 1


async def test_query_scoped_to_user(store):
    inp = QueryInput(user_id="u2")
    result = json.loads(await query_tasks(inp, store))
    assert result["total_count"] == 1
    assert result["tasks"][0]["title"] == "C"
