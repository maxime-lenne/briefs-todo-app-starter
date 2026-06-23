"""Unit tests for the CRUD layer (no HTTP)."""

import crud
from schemas import TodoCreate, TodoUpdate


def test_create_and_get_todo(db_session):
    todo = crud.create_todo(db_session, TodoCreate(title="Buy milk"))

    assert todo.id is not None
    assert todo.title == "Buy milk"
    assert todo.completed is False

    fetched = crud.get_todo(db_session, todo.id)
    assert fetched is not None
    assert fetched.id == todo.id


def test_get_todo_returns_none_when_missing(db_session):
    assert crud.get_todo(db_session, 9999) is None


def test_list_todos_returns_all(db_session):
    crud.create_todo(db_session, TodoCreate(title="first"))
    crud.create_todo(db_session, TodoCreate(title="second"))

    todos = crud.get_todos(db_session)

    assert len(todos) == 2
    assert {t.title for t in todos} == {"first", "second"}


def test_update_todo_only_changes_provided_fields(db_session):
    todo = crud.create_todo(
        db_session,
        TodoCreate(title="Original", description="keep me"),
    )

    updated = crud.update_todo(
        db_session,
        todo.id,
        TodoUpdate(completed=True),
    )

    assert updated is not None
    assert updated.completed is True
    assert updated.title == "Original"
    assert updated.description == "keep me"


def test_update_todo_returns_none_when_missing(db_session):
    assert crud.update_todo(db_session, 9999, TodoUpdate(title="x")) is None


def test_delete_todo(db_session):
    todo = crud.create_todo(db_session, TodoCreate(title="Drop me"))

    assert crud.delete_todo(db_session, todo.id) is True
    assert crud.get_todo(db_session, todo.id) is None


def test_delete_todo_returns_false_when_missing(db_session):
    assert crud.delete_todo(db_session, 9999) is False
