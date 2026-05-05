from datetime import timezone
import pytest
from tasks_mcp.models import Task, Status, Priority


def test_task_defaults():
    task = Task(title="Buy groceries")
    assert task.status == Status.TODO
    assert task.priority == Priority.MEDIUM
    assert task.user_id == "default"
    assert task.description == ""
    assert task.due_date is None


def test_task_id_is_generated():
    t1 = Task(title="A")
    t2 = Task(title="B")
    assert t1.id != t2.id
    assert len(t1.id) == 36  # UUID format


def test_task_timestamps_are_utc():
    task = Task(title="Test")
    assert task.created_at.tzinfo == timezone.utc
    assert task.updated_at.tzinfo == timezone.utc


def test_task_timestamps_iso_format():
    task = Task(title="Test")
    iso = task.created_at.isoformat()
    assert iso.endswith("+00:00") or iso.endswith("Z")


def test_task_custom_fields():
    task = Task(
        title="Report",
        user_id="user-42",
        description="Write Q1 report",
        status=Status.IN_PROGRESS,
        priority=Priority.HIGH,
        due_date="2026-05-10",
    )
    assert task.user_id == "user-42"
    assert task.status == Status.IN_PROGRESS
    assert task.priority == Priority.HIGH
    assert task.due_date == "2026-05-10"
