"""Business logic for the tasks feature."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.tasks.exceptions import TaskNotFound
from app.tasks.models import Task as TaskRow
from app.tasks.schemas import TaskOut


def create_task(db: Session, *, title: str, description: str | None) -> TaskOut:
    """Insert a new task and return its persisted representation."""
    row = TaskRow(title=title, description=description, completed=False)
    db.add(row)
    db.commit()
    db.refresh(row)
    return TaskOut.model_validate(row)


def list_tasks(db: Session) -> list[TaskOut]:
    """Return all tasks in creation order."""
    rows = db.execute(select(TaskRow).order_by(TaskRow.id)).scalars().all()
    return [TaskOut.model_validate(r) for r in rows]


def update_task(
    db: Session,
    task_id: int,
    *,
    title: str | None,
    description: str | None,
    completed: bool | None,
) -> TaskOut:
    """Patch the given fields on a task.

    None means "do not change this field"; absent fields in PUT body arrive
    here as None via TaskUpdate defaults.

    Raises:
        TaskNotFound: if no task exists with ``task_id``.
    """
    row = db.get(TaskRow, task_id)
    if row is None:
        raise TaskNotFound(task_id)
    if title is not None:
        row.title = title
    if description is not None:
        row.description = description
    if completed is not None:
        row.completed = completed
    db.commit()
    db.refresh(row)
    return TaskOut.model_validate(row)


def delete_task(db: Session, task_id: int) -> None:
    """Delete a task by id.

    Raises:
        TaskNotFound: if no task exists with ``task_id``.
    """
    row = db.get(TaskRow, task_id)
    if row is None:
        raise TaskNotFound(task_id)
    db.delete(row)
    db.commit()
