"""SQLAlchemy model for task dependencies."""

from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.sql import func

from database import Base


class TaskDependency(Base):
    """
    Represents a dependency relationship between tasks.
    
    PRD-003: F2.1 - Table task_dependencies (blocking_id, blocked_id)
    
    A task can block multiple other tasks, and a task can be blocked by multiple tasks.
    """

    __tablename__ = "task_dependencies"
    
    # The task that is blocking (must be completed first)
    blocking_id = Column(Integer, ForeignKey("todos.id"), nullable=False)
    
    # The task that is blocked (cannot be completed until blocking_id is done)
    blocked_id = Column(Integer, ForeignKey("todos.id"), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Ensure we don't have duplicate dependencies
    __table_args__ = (
        UniqueConstraint("blocking_id", "blocked_id", name="unique_dependency"),
    )
