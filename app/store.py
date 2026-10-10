"""In-memory task storage.

Data is lost every time the server restarts and is not shared between
several processes: run a single Uvicorn process.

This is the only file to replace when moving to a database:
the routes in app/main.py only use the methods below.
"""

from threading import Lock

from app.models import Task


class TaskStore:
    def __init__(self) -> None:
        self._tasks: dict[int, Task] = {}
        self._next_id = 1
        # Uvicorn may handle several requests in parallel (threads):
        # the lock prevents two creations from getting the same id.
        self._lock = Lock()

    def list(self) -> list[Task]:
        with self._lock:
            return list(self._tasks.values())

    def get(self, task_id: int) -> Task | None:
        with self._lock:
            return self._tasks.get(task_id)

    def create(self, title: str) -> Task:
        with self._lock:
            task = Task(id=self._next_id, title=title, completed=False)
            self._tasks[task.id] = task
            self._next_id += 1
            return task

    def update(
        self,
        task_id: int,
        title: str | None = None,
        completed: bool | None = None,
    ) -> Task | None:
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                return None
            if title is not None:
                task.title = title
            if completed is not None:
                task.completed = completed
            return task

    def delete(self, task_id: int) -> bool:
        with self._lock:
            return self._tasks.pop(task_id, None) is not None

    def reset(self) -> None:
        """Empty the storage and reset the id counter to 1 (used by the tests)."""
        with self._lock:
            self._tasks.clear()
            self._next_id = 1


store = TaskStore()
