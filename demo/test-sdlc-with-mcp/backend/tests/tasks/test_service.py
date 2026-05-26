from datetime import datetime

import pytest
from sqlalchemy.orm import Session

from app.tasks.exceptions import TaskNotFound
from app.tasks.service import (
    create_task,
    delete_task,
    list_tasks,
    update_task,
)


def test_create_task_returns_persisted_task(session: Session) -> None:
    task = create_task(session, title="Write tests", description="cover CRUD")

    assert task.id > 0
    assert task.title == "Write tests"
    assert task.description == "cover CRUD"
    assert task.completed is False
    assert isinstance(task.created_at, datetime)
    assert isinstance(task.updated_at, datetime)


def test_create_task_allows_null_description(session: Session) -> None:
    task = create_task(session, title="No desc", description=None)

    assert task.description is None


def test_list_tasks_returns_all_in_creation_order(session: Session) -> None:
    create_task(session, title="first", description=None)
    create_task(session, title="second", description=None)

    tasks = list_tasks(session)

    assert [t.title for t in tasks] == ["first", "second"]


def test_list_tasks_empty_returns_empty_list(session: Session) -> None:
    tasks = list_tasks(session)

    assert tasks == []


def test_update_task_changes_title(session: Session) -> None:
    created = create_task(session, title="old", description=None)

    updated = update_task(
        session, created.id, title="new", description=None, completed=None
    )

    assert updated.title == "new"
    assert updated.id == created.id


def test_update_task_toggles_completed(session: Session) -> None:
    created = create_task(session, title="t", description=None)

    updated = update_task(
        session, created.id, title=None, description=None, completed=True
    )

    assert updated.completed is True


def test_update_task_leaves_unspecified_fields_unchanged(session: Session) -> None:
    created = create_task(session, title="keep me", description="keep desc")

    updated = update_task(
        session, created.id, title=None, description=None, completed=True
    )

    assert updated.title == "keep me"
    assert updated.description == "keep desc"


def test_update_task_missing_raises(session: Session) -> None:
    with pytest.raises(TaskNotFound):
        update_task(session, 999, title="x", description=None, completed=None)


def test_delete_task_removes_task(session: Session) -> None:
    created = create_task(session, title="t", description=None)

    delete_task(session, created.id)

    assert list_tasks(session) == []


def test_delete_task_missing_raises(session: Session) -> None:
    with pytest.raises(TaskNotFound):
        delete_task(session, 999)
