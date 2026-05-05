import json
from tasks_mcp.models import LookupInput, Status
from tasks_mcp.store import TaskStore, NotFoundError, AmbiguousLookupError
from tasks_mcp.tools._helpers import err, utcnow


async def start_task(inp: LookupInput, store: TaskStore, user_id: str = "default") -> str:
    try:
        task = store.resolve(id=inp.id, title=inp.title, user_id=user_id)
    except (NotFoundError, AmbiguousLookupError) as e:
        return err(str(e))

    if task.status == Status.DONE:
        return err("Task is already done. Use tasks_edit to reopen it.")
    if task.status == Status.IN_PROGRESS:
        return json.dumps({**task.to_dict(), "message": "Task is already in progress."})

    task.status = Status.IN_PROGRESS
    task.updated_at = utcnow()
    return json.dumps(task.to_dict())
