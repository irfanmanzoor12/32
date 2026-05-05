from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
import uuid

from pydantic import BaseModel, ConfigDict, Field


class Status(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _new_id() -> str:
    return str(uuid.uuid4())


@dataclass
class Task:
    title: str
    id: str = field(default_factory=_new_id)
    user_id: str = "default"
    description: str = ""
    status: Status = Status.TODO
    priority: Priority = Priority.MEDIUM
    due_date: Optional[str] = None
    created_at: datetime = field(default_factory=_utcnow)
    updated_at: datetime = field(default_factory=_utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "priority": self.priority.value,
            "due_date": self.due_date,
            "created_at": self.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "updated_at": self.updated_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }


# --- Pydantic input models (one per tool) ---

class CreateInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    title: str = Field(..., min_length=1, description="Task title")
    user_id: str = Field(default="default", description="User id, defaults to 'default'")
    description: str = Field(default="", description="Optional details")
    priority: Priority = Field(default=Priority.MEDIUM, description="low | medium | high")
    due_date: Optional[str] = Field(default=None, description="Due date YYYY-MM-DD")


class LookupInput(BaseModel):
    """Base for tools that target an existing task by id or title."""
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    id: Optional[str] = Field(default=None, description="Task id")
    title: Optional[str] = Field(default=None, description="Task title (used if id not provided)")


class RescheduleInput(LookupInput):
    due_date: str = Field(..., description="New due date YYYY-MM-DD")


class EditInput(LookupInput):
    new_title: Optional[str] = Field(default=None, description="New title")
    description: Optional[str] = Field(default=None, description="New description")
    priority: Optional[Priority] = Field(default=None, description="New priority")


class QueryInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    user_id: str = Field(default="default", description="Filter by user, defaults to 'default'")
    status: Optional[Status] = Field(default=None, description="Filter by status")
    priority: Optional[Priority] = Field(default=None, description="Filter by priority")
    due_today: bool = Field(default=False, description="Return only tasks due today")
