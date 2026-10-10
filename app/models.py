"""Pydantic models: shape of the data received (requests) and returned (responses)."""

from typing import Annotated

from pydantic import BaseModel, StringConstraints, model_validator

# A title is stripped of leading and trailing whitespace, then must contain
# between 1 and 100 characters. Otherwise FastAPI automatically returns a 422.
Title = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=100),
]


class TaskCreate(BaseModel):
    """Request body for POST /tasks."""

    title: Title


class TaskUpdate(BaseModel):
    """Request body for PATCH /tasks/{id}: every field is optional."""

    title: Title | None = None
    completed: bool | None = None

    @model_validator(mode="after")
    def check_at_least_one_field(self) -> "TaskUpdate":
        if self.title is None and self.completed is None:
            raise ValueError("Provide at least one field: title or completed")
        return self


class Task(BaseModel):
    """A task as returned by the API."""

    id: int
    title: str
    completed: bool = False


class HealthResponse(BaseModel):
    status: str


class VersionResponse(BaseModel):
    name: str
    version: str
