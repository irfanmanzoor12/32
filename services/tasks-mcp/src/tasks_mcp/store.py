from __future__ import annotations
from typing import Optional
from tasks_mcp.models import Task, Status, Priority


class NotFoundError(Exception):
    pass


class AmbiguousLookupError(Exception):
    pass


class TaskStore:
    def __init__(self) -> None:
        self._tasks: dict[str, Task] = {}

    def add(self, task: Task) -> Task:
        self._tasks[task.id] = task
        return task

    def get(self, id: str) -> Task:
        if id not in self._tasks:
            raise NotFoundError(f"No task found with id '{id}'.")
        return self._tasks[id]

    def delete(self, id: str) -> Task:
        if id not in self._tasks:
            raise NotFoundError(f"No task found with id '{id}'.")
        return self._tasks.pop(id)

    def resolve(self, id: Optional[str], title: Optional[str], user_id: str) -> Task:
        if id:
            return self.get(id)
        if not title:
            raise NotFoundError("Provide either 'id' or 'title' to identify a task.")
        user_tasks = [t for t in self._tasks.values() if t.user_id == user_id]
        exact = [t for t in user_tasks if t.title == title]
        if len(exact) == 1:
            return exact[0]
        insensitive = [t for t in user_tasks if t.title.lower() == title.lower()]
        if len(insensitive) == 1:
            return insensitive[0]
        if len(insensitive) > 1:
            raise AmbiguousLookupError(
                f"Multiple tasks match '{title}'. Use id to be specific."
            )
        raise NotFoundError(f"No task found matching '{title}'.")

    def list_tasks(
        self,
        user_id: str,
        status: Optional[Status] = None,
        priority: Optional[Priority] = None,
        due_today: Optional[str] = None,
    ) -> list[Task]:
        results = [t for t in self._tasks.values() if t.user_id == user_id]
        if status:
            results = [t for t in results if t.status == status]
        if priority:
            results = [t for t in results if t.priority == priority]
        if due_today:
            results = [t for t in results if t.due_date == due_today]
        return results
