import json
from tasks_mcp.models import LookupInput
from tasks_mcp.store import TaskStore, NotFoundError, AmbiguousLookupError
from tasks_mcp.tools._helpers import err


async def remove_task(inp: LookupInput, store: TaskStore, user_id: str = "default") -> str:
    try:
        task = store.resolve(id=inp.id, title=inp.title, user_id=user_id)
        store.delete(task.id)
    except (NotFoundError, AmbiguousLookupError) as e:
        return err(str(e))

    return json.dumps({"deleted": True, "task": {"id": task.id, "title": task.title}})
