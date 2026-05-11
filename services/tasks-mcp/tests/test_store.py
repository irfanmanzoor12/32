import pytest
from tasks_mcp.models import Task, Status
from tasks_mcp.store import TaskStore, NotFoundError, AmbiguousLookupError


@pytest.fixture
def store():
    return TaskStore()


@pytest.fixture
def task(store):
    t = Task(title="Buy groceries", user_id="u1")
    store.add(t)
    return t


def test_add_and_get(store):
    t = Task(title="Test task")
    store.add(t)
    assert store.get(t.id) == t


def test_get_missing_raises(store):
    with pytest.raises(NotFoundError):
        store.get("nonexistent-id")


def test_resolve_by_id(store, task):
    result = store.resolve(id=task.id, title=None, user_id="u1")
    assert result == task


def test_resolve_by_exact_title(store, task):
    result = store.resolve(id=None, title="Buy groceries", user_id="u1")
    assert result == task


def test_resolve_by_case_insensitive_title(store, task):
    result = store.resolve(id=None, title="buy GROCERIES", user_id="u1")
    assert result == task


def test_resolve_ambiguous_title_raises(store):
    store.add(Task(title="Buy groceries", user_id="u1"))
    store.add(Task(title="Buy Groceries", user_id="u1"))
    with pytest.raises(AmbiguousLookupError):
        store.resolve(id=None, title="buy groceries", user_id="u1")


def test_resolve_not_found_raises(store):
    with pytest.raises(NotFoundError):
        store.resolve(id=None, title="nonexistent", user_id="u1")


def test_delete(store, task):
    store.delete(task.id)
    with pytest.raises(NotFoundError):
        store.get(task.id)


def test_delete_missing_raises(store):
    with pytest.raises(NotFoundError):
        store.delete("nonexistent-id")


def test_list_all_for_user(store):
    store.add(Task(title="A", user_id="u1"))
    store.add(Task(title="B", user_id="u1"))
    store.add(Task(title="C", user_id="u2"))
    results = store.list_tasks(user_id="u1")
    assert len(results) == 2


def test_list_filter_by_status(store):
    store.add(Task(title="A", user_id="u1", status=Status.TODO))
    store.add(Task(title="B", user_id="u1", status=Status.DONE))
    results = store.list_tasks(user_id="u1", status=Status.DONE)
    assert len(results) == 1
    assert results[0].title == "B"


def test_resolve_scoped_to_user(store):
    store.add(Task(title="My task", user_id="u1"))
    store.add(Task(title="My task", user_id="u2"))
    # Each user's lookup is unambiguous within their own scope
    r1 = store.resolve(id=None, title="My task", user_id="u1")
    r2 = store.resolve(id=None, title="My task", user_id="u2")
    assert r1.user_id == "u1"
    assert r2.user_id == "u2"
