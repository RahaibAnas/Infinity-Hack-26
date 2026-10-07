from datetime import date
from pydantic import BaseModel, Field


class TaskDraft(BaseModel):
    title: str | None = None
    description: str | None = None
    assignee_id: str | None = None
    deadline: date | None = None
    estimated_hours: float | None = Field(default=None, gt=0)


class ProjectDraft(BaseModel):
    name: str | None = None
    client: str | None = None
    description: str | None = None
    manager_id: str | None = None
    deadline: date | None = None
    tasks: list[TaskDraft] = []


class UnresolvedField(BaseModel):
    project_index: int
    task_index: int | None = None
    field: str
    reason: str


class MeetingDraft(BaseModel):
    projects: list[ProjectDraft]
    unresolved_fields: list[UnresolvedField] = []
