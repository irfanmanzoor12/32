import json
from datetime import datetime, timezone


def err(message: str) -> str:
    return json.dumps({"error": True, "message": message})


def utcnow() -> datetime:
    return datetime.now(timezone.utc)
