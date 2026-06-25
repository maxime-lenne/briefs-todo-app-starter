"""Pydantic schemas for request/response validation."""

from datetime import datetime

from pydantic import BaseModel, Field


class TodoBase(BaseModel):
    """Shared fields for todo operations."""

    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=500)
    completed: bool = False


class TodoCreate(TodoBase):
    """Schema for creating a new todo."""
    
    # PRD-003: F1.1 - Support pour parent_id (sous-tâches)
    parent_id: int | None = Field(None, description="ID de la tâche parente (pour les sous-tâches)")


class TodoUpdate(BaseModel):
    """Schema for updating an existing todo. All fields optional."""

    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=500)
    completed: bool | None = None
    
    # PRD-003: F1.1 - Support pour parent_id
    parent_id: int | None = Field(None, description="ID de la tâche parente")


class TodoResponse(TodoBase):
    """Schema for todo responses including database-generated fields."""

    id: int
    created_at: datetime
    updated_at: datetime | None = None
    
    # PRD-003: F1.1 - Champ parent_id
    parent_id: int | None = None

    model_config = {"from_attributes": True}


# PRD-003: F2.1 - Schéma pour les dépendances
class TaskDependencyBase(BaseModel):
    """Base schema for task dependencies."""
    blocking_id: int = Field(..., description="ID de la tâche qui bloque")
    blocked_id: int = Field(..., description="ID de la tâche bloquée")


class TaskDependencyCreate(TaskDependencyBase):
    """Schema for creating a new dependency."""
    pass


class TaskDependencyResponse(TaskDependencyBase):
    """Schema for dependency responses."""
    id: int
    created_at: datetime
    
    model_config = {"from_attributes": True}
