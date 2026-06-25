"""Services for calculating task progress and handling subtask completion."""

from sqlalchemy.orm import Session
from ..models import Todo


def calculate_completion_percentage(db: Session, todo_id: int) -> float:
    """
    Calculate the completion percentage for a task including its subtasks.
    
    PRD-003: F3.1 - Calcul automatique du % de complétion
    
    Args:
        db: Database session
        todo_id: ID of the task
        
    Returns:
        float: Completion percentage (0.0 to 100.0)
    """
    # Get the task and all its subtasks recursively
    todo = db.get(Todo, todo_id)
    if not todo:
        return 0.0
    
    # Collect all tasks in the hierarchy (todo + subtasks)
    all_tasks = _get_task_hierarchy(db, todo)
    
    if not all_tasks:
        return 0.0
    
    # Count completed tasks
    completed_count = sum(1 for task in all_tasks if task.completed)
    
    # Calculate percentage
    return (completed_count / len(all_tasks)) * 100


def _get_task_hierarchy(db: Session, todo: Todo) -> list[Todo]:
    """
    Recursively get all tasks in a hierarchy (parent + all subtasks).
    
    PRD-003: F3.3 - Une tâche est complétée si toutes ses sous-tâches le sont
    """
    tasks = [todo]
    
    # Recursively add subtasks
    for subtask in todo.subtasks:
        tasks.extend(_get_task_hierarchy(db, subtask))
    
    return tasks


def can_complete_task(db: Session, todo_id: int) -> tuple[bool, str]:
    """
    Check if a task can be marked as completed.
    A task can only be completed if:
    1. All its subtasks are completed (PRD-003: F3.3)
    2. It is not blocked by any incomplete task
    
    PRD-003: F3.3 - Une tâche est complétée si toutes ses sous-tâches le sont
    
    Args:
        db: Database session
        todo_id: ID of the task
        
    Returns:
        tuple: (can_complete: bool, reason: str)
    """
    from ..dependency import TaskDependency
    
    todo = db.get(Todo, todo_id)
    if not todo:
        return False, "Task not found"
    
    # Check if all subtasks are completed
    if todo.subtasks:
        for subtask in todo.subtasks:
            if not subtask.completed:
                return False, f"Cannot complete: subtask '{subtask.title}' (ID: {subtask.id}) is not completed"
    
    # Check if this task is blocked by any incomplete task
    dependencies = db.query(TaskDependency).filter_by(blocked_id=todo_id).all()
    for dep in dependencies:
        blocking_task = db.get(Todo, dep.blocking_id)
        if blocking_task and not blocking_task.completed:
            return False, f"Cannot complete: blocked by '{blocking_task.title}' (ID: {blocking_task.id}) which is not completed"
    
    return True, ""


def can_delete_task(db: Session, todo_id: int) -> tuple[bool, str]:
    """
    Check if a task can be deleted.
    A task cannot be deleted if:
    - It is blocking other tasks (PRD-003: F2.2)
    
    Args:
        db: Database session
        todo_id: ID of the task
        
    Returns:
        tuple: (can_delete: bool, reason: str)
    """
    from ..dependency import TaskDependency
    
    # Check if this task is blocking other tasks
    dependencies = db.query(TaskDependency).filter_by(blocking_id=todo_id).all()
    if dependencies:
        blocked_tasks = [f"'{db.get(Todo, dep.blocked_id).title}' (ID: {dep.blocked_id})" for dep in dependencies]
        return False, f"Cannot delete: this task blocks {', '.join(blocked_tasks)}"
    
    return True, ""
