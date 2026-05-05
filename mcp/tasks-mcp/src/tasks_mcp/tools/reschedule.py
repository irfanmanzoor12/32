import json
from tasks_mcp.models import RescheduleInput
from tasks_mcp.store import TaskStore, NotFoundError, AmbiguousLookupError
from tasks_mcp.tools._helpers import err, utcnow


async def reschedule_task(inp: RescheduleInput, store: TaskStore, user_id: str = "default") -> str:
    try:
        task = store.resolve(id=inp.id, title=inp.title, user_id=user_id)
    except (NotFoundError, AmbiguousLookupError) as e:
        return err(str(e))

    task.due_date = inp.due_date
    task.updated_at = utcnow()
    return json.dumps(task.to_dict())
