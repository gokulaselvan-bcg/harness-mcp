"""HTTP routes for the tasks feature."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.common.db import get_session
from app.tasks.exceptions import TaskNotFound
from app.tasks.schemas import TaskCreate, TaskListResponse, TaskOut, TaskUpdate
from app.tasks.service import create_task, delete_task, list_tasks, update_task

router = APIRouter(prefix="/v1/tasks", tags=["tasks"])


@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create(
    payload: TaskCreate,
    db: Session = Depends(get_session),
) -> TaskOut:
    """Create a new task."""
    return create_task(db, title=payload.title, description=payload.description)


@router.get("", response_model=TaskListResponse)
def list_(db: Session = Depends(get_session)) -> TaskListResponse:
    """Return all tasks."""
    return TaskListResponse(tasks=list_tasks(db))


@router.put("/{task_id}", response_model=TaskOut)
def update(
    task_id: int,
    payload: TaskUpdate,
    db: Session = Depends(get_session),
) -> TaskOut:
    """Patch the given fields on a task."""
    try:
        return update_task(
            db,
            task_id,
            title=payload.title,
            description=payload.description,
            completed=payload.completed,
        )
    except TaskNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"task {task_id} not found",
        ) from None


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(
    task_id: int,
    db: Session = Depends(get_session),
) -> None:
    """Delete a task by id."""
    try:
        delete_task(db, task_id)
    except TaskNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"task {task_id} not found",
        ) from None
