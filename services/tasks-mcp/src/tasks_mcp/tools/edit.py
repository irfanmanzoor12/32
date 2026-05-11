import json
from tasks_mcp.models import EditInput
from tasks_mcp.store import TaskStore, NotFoundError, AmbiguousLookupError
from tasks_mcp.tools._helpers import err, utcnow


async def edit_task(inp: EditInput, store: TaskStore, user_id: str = "default") -> str:
    if inp.new_title is None and inp.description is None and inp.priority is None:
        return err("Provide at least one of: new_title, description, priority.")

    try:
        task = store.resolve(id=inp.id, title=inp.title, user_id=user_id)
    except (NotFoundError, AmbiguousLookupError) as e:
        return err(str(e))

    if inp.new_title is not None:
        task.title = inp.new_title
    if inp.description is not None:
        task.description = inp.description
    if inp.priority is not None:
        task.priority = inp.priority
    task.updated_at = utcnow()
    return json.dumps(task.to_dict())
