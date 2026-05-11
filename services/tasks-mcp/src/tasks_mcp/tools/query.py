import json
from datetime import datetime, timezone
from tasks_mcp.models import QueryInput
from tasks_mcp.store import TaskStore


async def query_tasks(inp: QueryInput, store: TaskStore) -> str:
    due_today = datetime.now(timezone.utc).strftime("%Y-%m-%d") if inp.due_today else None
    tasks = store.list_tasks(
        user_id=inp.user_id,
        status=inp.status,
        priority=inp.priority,
        due_today=due_today,
    )
    return json.dumps({"tasks": [t.to_dict() for t in tasks], "total_count": len(tasks)})
