"""FastAPI application entry point."""

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

import crud
import schemas
from database import Base, engine, get_db
from models import Todo
from dependency import TaskDependency

# Create all tables on startup
# PRD-003: F1.1, F2.1 - Inclure les nouveaux modèles
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="To-Do API",
    description="REST API for managing to-do tasks with subtasks and dependencies",
    version="0.1.0",
)


@app.get("/todos", response_model=list[schemas.TodoResponse])
def list_todos(db: Session = Depends(get_db)):
    """List all todos."""
    return crud.get_todos(db)


@app.get("/todos/{todo_id}", response_model=schemas.TodoResponse)
def get_todo(todo_id: int, db: Session = Depends(get_db)):
    """Get a single todo by ID."""
    todo = crud.get_todo(db, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@app.post("/todos", response_model=schemas.TodoResponse, status_code=201)
def create_todo(todo: schemas.TodoCreate, db: Session = Depends(get_db)):
    """Create a new todo."""
    return crud.create_todo(db, todo)


@app.put("/todos/{todo_id}", response_model=schemas.TodoResponse)
def update_todo(todo_id: int, todo: schemas.TodoUpdate, db: Session = Depends(get_db)):
    """Update an existing todo."""
    updated = crud.update_todo(db, todo_id, todo)
    if not updated:
        raise HTTPException(status_code=404, detail="Todo not found")
    return updated


@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    """Delete a todo."""
    if not crud.delete_todo(db, todo_id):
        raise HTTPException(status_code=404, detail="Todo not found")


# PRD-003: F1.2 - Endpoint pour lister les sous-tâches
@app.get("/todos/{todo_id}/subtasks", response_model=list[schemas.TodoResponse])
def get_subtasks(todo_id: int, db: Session = Depends(get_db)):
    """Get all subtasks of a todo."""
    subtasks = crud.get_subtasks(db, todo_id)
    return subtasks


# PRD-003: F2.3 - Endpoints pour gérer les dépendances
@app.get("/todos/{todo_id}/dependencies", response_model=list[schemas.TaskDependencyResponse])
def get_dependencies(todo_id: int, db: Session = Depends(get_db)):
    """Get all dependencies for a todo (blocking and blocked)."""
    dependencies = crud.get_dependencies(db, todo_id)
    return dependencies


@app.post("/todos/{todo_id}/dependencies", response_model=schemas.TaskDependencyResponse, status_code=201)
def create_dependency(
    todo_id: int,
    dependency: schemas.TaskDependencyCreate,
    db: Session = Depends(get_db)
):
    """Create a dependency where todo_id is the blocking task."""
    # Ensure the blocking_id is the current todo_id
    dependency.blocking_id = todo_id
    try:
        return crud.create_dependency(db, dependency)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/dependencies/{dependency_id}", status_code=204)
def delete_dependency(dependency_id: int, db: Session = Depends(get_db)):
    """Delete a dependency."""
    if not crud.delete_dependency(db, dependency_id):
        raise HTTPException(status_code=404, detail="Dependency not found")
