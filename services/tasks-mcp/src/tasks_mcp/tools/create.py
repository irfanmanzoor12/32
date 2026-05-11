import json
from tasks_mcp.models import CreateInput, Task
from tasks_mcp.store import TaskStore


async def create_task(inp: CreateInput, store: TaskStore) -> str:
    task = Task(
        title=inp.title,
        user_id=inp.user_id,
        description=inp.description,
        priority=inp.priority,
        due_date=inp.due_date,
    )
    store.add(task)
    return json.dumps(task.to_dict())
