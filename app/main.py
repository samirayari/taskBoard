"""TaskBoard application: configuration and API routes."""

import os

from fastapi import FastAPI, HTTPException, Response, status

from app.models import HealthResponse, Task, TaskCreate, TaskUpdate, VersionResponse
from app.store import store

# Configuration read from environment variables, with default values.
APP_NAME = os.getenv("APP_NAME", "TaskBoard")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="Educational task management API (in-memory storage).",
)


def _not_found(task_id: int) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task {task_id} not found",
    )


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health():
    return {"status": "ok"}


@app.get("/version", response_model=VersionResponse, tags=["system"])
def version():
    return {"name": APP_NAME, "version": APP_VERSION}


@app.get("/tasks", response_model=list[Task], tags=["tasks"])
def list_tasks():
    return store.list()


@app.get("/tasks/{task_id}", response_model=Task, tags=["tasks"])
def get_task(task_id: int):
    task = store.get(task_id)
    if task is None:
        raise _not_found(task_id)
    return task


@app.post(
    "/tasks",
    response_model=Task,
    status_code=status.HTTP_201_CREATED,
    tags=["tasks"],
)
def create_task(payload: TaskCreate):
    return store.create(payload.title)


@app.patch("/tasks/{task_id}", response_model=Task, tags=["tasks"])
def update_task(task_id: int, payload: TaskUpdate):
    task = store.update(task_id, title=payload.title, completed=payload.completed)
    if task is None:
        raise _not_found(task_id)
    return task


@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["tasks"],
)
def delete_task(task_id: int):
    if not store.delete(task_id):
        raise _not_found(task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
