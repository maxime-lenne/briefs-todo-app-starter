"""CRUD operations for the Todo model."""

from sqlalchemy.orm import Session

from models import Todo
from dependency import TaskDependency
from schemas import TodoCreate, TodoUpdate, TaskDependencyCreate
from services.progress import can_complete_task, can_delete_task


def get_todos(db: Session) -> list[Todo]:
    """Return all todos ordered by creation date (newest first)."""
    return db.query(Todo).order_by(Todo.created_at.desc()).all()


def get_todo(db: Session, todo_id: int) -> Todo | None:
    """Return a single todo by ID, or None if not found."""
    return db.query(Todo).filter(Todo.id == todo_id).first()


def create_todo(db: Session, todo: TodoCreate) -> Todo:
    """Create a new todo and return it."""
    db_todo = Todo(**todo.model_dump())
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo


def update_todo(db: Session, todo_id: int, todo: TodoUpdate) -> Todo | None:
    """Update an existing todo. Returns None if not found."""
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not db_todo:
        return None
    
    # PRD-003: F3.3 - Vérifier que toutes les sous-tâches sont complétées avant de compléter
    if todo.completed is True:
        can_complete, reason = can_complete_task(db, todo_id)
        if not can_complete:
            raise ValueError(reason)
    
    for key, value in todo.model_dump(exclude_unset=True).items():
        setattr(db_todo, key, value)
    db.commit()
    db.refresh(db_todo)
    return db_todo


def delete_todo(db: Session, todo_id: int) -> bool:
    """Delete a todo by ID. Returns True if deleted, False if not found."""
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not db_todo:
        return False
    
    # PRD-003: F2.2 - Empêcher la suppression d'une tâche bloquante
    can_delete, reason = can_delete_task(db, todo_id)
    if not can_delete:
        raise ValueError(reason)
    
    db.delete(db_todo)
    db.commit()
    return True


# PRD-003: F1.2 - Récupérer les sous-tâches d'une tâche
def get_subtasks(db: Session, todo_id: int) -> list[Todo]:
    """Return all subtasks of a given todo."""
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        return []
    return todo.subtasks


# PRD-003: F2.1, F2.3 - Gestion des dépendances
def get_dependencies(db: Session, todo_id: int) -> list[TaskDependency]:
    """Return all dependencies where the given todo is either blocking or blocked."""
    # Dependencies where this todo is blocking another
    blocking_deps = db.query(TaskDependency).filter_by(blocking_id=todo_id).all()
    
    # Dependencies where this todo is blocked by another
    blocked_deps = db.query(TaskDependency).filter_by(blocked_id=todo_id).all()
    
    return blocking_deps + blocked_deps


def create_dependency(db: Session, dependency: TaskDependencyCreate) -> TaskDependency:
    """Create a new dependency relationship."""
    # Check if the dependency would create a circular reference
    if _has_circular_dependency(db, dependency.blocking_id, dependency.blocked_id):
        raise ValueError(f"Circular dependency detected between tasks {dependency.blocking_id} and {dependency.blocked_id}")
    
    # Check if dependency already exists
    existing = db.query(TaskDependency).filter_by(
        blocking_id=dependency.blocking_id,
        blocked_id=dependency.blocked_id
    ).first()
    if existing:
        raise ValueError(f"Dependency between {dependency.blocking_id} and {dependency.blocked_id} already exists")
    
    db_dep = TaskDependency(**dependency.model_dump())
    db.add(db_dep)
    db.commit()
    db.refresh(db_dep)
    return db_dep


def delete_dependency(db: Session, dependency_id: int) -> bool:
    """Delete a dependency by ID."""
    db_dep = db.query(TaskDependency).filter(TaskDependency.id == dependency_id).first()
    if not db_dep:
        return False
    db.delete(db_dep)
    db.commit()
    return True


def _has_circular_dependency(db: Session, blocking_id: int, blocked_id: int) -> bool:
    """Check if creating a dependency would create a circular reference."""
    # If we're trying to create A -> B, check if B -> A exists (directly or indirectly)
    # This is a simplified check - for a full solution you'd need a graph traversal
    
    # Direct circular: A blocks B and B blocks A
    existing = db.query(TaskDependency).filter_by(
        blocking_id=blocked_id,
        blocked_id=blocking_id
    ).first()
    if existing:
        return True
    
    # For more complex circular dependencies, you'd need to implement a graph traversal
    # This is a simplified version that catches the most obvious cases
    return False
