"""SQLAlchemy ORM models."""

from sqlalchemy import Boolean, Column, DateTime, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class Todo(Base):
    """Represents a to-do task in the database."""

    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(String(500), nullable=True)
    completed = Column(Boolean, default=False, nullable=False)
    
    # PRD-003: F1.1 - Champ parent_id pour les sous-tâches
    parent_id = Column(Integer, ForeignKey("todos.id"), nullable=True)
    
    # Relation pour accéder aux sous-tâches d'une tâche
    subtasks = relationship("Todo", backref="parent", remote_side=[id])
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
