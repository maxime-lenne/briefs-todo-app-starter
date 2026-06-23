# FastAPI + SQLAlchemy 2.0 Skill

## Best Practices

### Project Structure
```
api/
├── main.py          # App + routes
├── database.py      # Engine + session
├── models.py        # SQLAlchemy models
├── schemas.py       # Pydantic schemas
├── crud.py          # Database operations
└── requirements.txt # Dependencies
```

## Database Connection Pattern
```python
# database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./todo.db")

# For SQLite, we need to allow same thread access
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """Dependency that provides a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## Model Definition
```python
# models.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from database import Base


class Todo(Base):
    """Todo model representing a task in the application."""

    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(String(500), nullable=True)
    completed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Todo(id={self.id}, title='{self.title}')>"
```

## Pydantic Schemas
```python
# schemas.py
from datetime import datetime
from pydantic import BaseModel, Field


class TodoBase(BaseModel):
    """Base schema for Todo with common fields."""

    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: str | None = Field(None, max_length=500, description="Task description")
    completed: bool = Field(False, description="Task completion status")


class TodoCreate(TodoBase):
    """Schema for creating a new Todo."""

    pass


class TodoUpdate(BaseModel):
    """Schema for updating an existing Todo (all fields optional)."""

    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=500)
    completed: bool | None = None


class TodoResponse(TodoBase):
    """Schema for Todo response including database-generated fields."""

    id: int
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
```

## CRUD Operations
```python
# crud.py
from sqlalchemy.orm import Session
from sqlalchemy import select
from models import Todo
from schemas import TodoCreate, TodoUpdate
from typing import Sequence


def get_todos(db: Session, skip: int = 0, limit: int = 100) -> Sequence[Todo]:
    """Get a list of todos with pagination."""
    return db.execute(
        select(Todo).offset(skip).limit(limit)
    ).scalars().all()


def get_todo(db: Session, todo_id: int) -> Todo | None:
    """Get a specific todo by ID."""
    return db.get(Todo, todo_id)
    # Alternative: return db.execute(select(Todo).filter(Todo.id == todo_id)).scalar_one_or_none()


def get_todos_by_status(db: Session, completed: bool, skip: int = 0, limit: int = 100) -> Sequence[Todo]:
    """Get todos filtered by completion status."""
    return db.execute(
        select(Todo).filter(Todo.completed == completed).offset(skip).limit(limit)
    ).scalars().all()


def create_todo(db: Session, todo: TodoCreate) -> Todo:
    """Create a new todo item."""
    db_todo = Todo(**todo.model_dump())
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo


def update_todo(db: Session, todo_id: int, todo: TodoUpdate) -> Todo | None:
    """Update an existing todo item."""
    db_todo = db.get(Todo, todo_id)
    if not db_todo:
        return None

    update_data = todo.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_todo, field, value)

    db.commit()
    db.refresh(db_todo)
    return db_todo


def delete_todo(db: Session, todo_id: int) -> bool:
    """Delete a todo item."""
    db_todo = db.get(Todo, todo_id)
    if not db_todo:
        return False

    db.delete(db_todo)
    db.commit()
    return True


def delete_all_todos(db: Session) -> int:
    """Delete all todos (use with caution)."""
    result = db.execute(select(Todo))
    todos = result.scalars().all()
    count = len(todos)
    for todo in todos:
        db.delete(todo)
    db.commit()
    return count
```

## FastAPI Routes
```python
# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import crud
import schemas
from database import Base, engine, get_db

# Create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="To-Do API",
    version="0.1.0",
    description="A simple To-Do API with CRUD operations",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Middleware (configure for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Todo Endpoints ---

@app.get("/todos", response_model=list[schemas.TodoResponse])
def list_todos(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """List all todos with optional pagination."""
    todos = crud.get_todos(db, skip=skip, limit=limit)
    return todos


@app.get("/todos/{todo_id}", response_model=schemas.TodoResponse)
def get_todo(todo_id: int, db: Session = Depends(get_db)):
    """Get a specific todo by ID."""
    todo = crud.get_todo(db, todo_id)
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )
    return todo


@app.post("/todos", response_model=schemas.TodoResponse, status_code=status.HTTP_201_CREATED)
def create_todo(todo: schemas.TodoCreate, db: Session = Depends(get_db)):
    """Create a new todo."""
    return crud.create_todo(db, todo)


@app.put("/todos/{todo_id}", response_model=schemas.TodoResponse)
def update_todo(
    todo_id: int,
    todo: schemas.TodoUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing todo."""
    updated = crud.update_todo(db, todo_id, todo)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )
    return updated


@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    """Delete a todo."""
    if not crud.delete_todo(db, todo_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )
    return None


# --- Health Check ---

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
```

## Testing Patterns

### Test Fixtures
```python
# api/tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import sys, os

# Add api directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app
from database import Base, get_db

# Use in-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create all tables before tests and drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def session():
    """Create a new database session for each test."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(session):
    """Test client with database session override."""
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def cleanup_db(session):
    """Clean up database after each test."""
    yield
    session.rollback()
    for table in reversed(Base.metadata.tables.values()):
        session.execute(table.delete())
    session.commit()
```

### CRUD Tests
```python
# api/tests/test_crud.py
from schemas import TodoCreate, TodoUpdate


def test_create_todo(session):
    from crud import create_todo
    todo_data = TodoCreate(title="Test task", description="Test description")
    todo = create_todo(session, todo_data)
    assert todo.id is not None
    assert todo.title == "Test task"
    assert todo.description == "Test description"
    assert todo.completed is False
    assert todo.created_at is not None


def test_get_todo(session):
    from crud import create_todo, get_todo
    created = create_todo(session, TodoCreate(title="Get test"))
    fetched = get_todo(session, created.id)
    assert fetched.id == created.id
    assert fetched.title == "Get test"


def test_get_todo_not_found(session):
    from crud import get_todo
    assert get_todo(session, 999) is None


def test_update_todo(session):
    from crud import create_todo, update_todo
    created = create_todo(session, TodoCreate(title="Update test"))
    updated = update_todo(session, created.id, TodoUpdate(title="Updated title"))
    assert updated.title == "Updated title"
    assert updated.id == created.id


def test_update_todo_not_found(session):
    from crud import update_todo
    assert update_todo(session, 999, TodoUpdate(title="Test")) is None


def test_delete_todo(session):
    from crud import create_todo, delete_todo, get_todo
    created = create_todo(session, TodoCreate(title="Delete test"))
    assert delete_todo(session, created.id) is True
    assert get_todo(session, created.id) is None
    assert delete_todo(session, 999) is False


def test_get_todos_empty(session):
    from crud import get_todos
    assert get_todos(session) == []


def test_get_todos_with_data(session):
    from crud import create_todo, get_todos
    create_todo(session, TodoCreate(title="Task 1"))
    create_todo(session, TodoCreate(title="Task 2"))
    todos = get_todos(session)
    assert len(todos) == 2
```

### API Endpoint Tests
```python
# api/tests/test_routes.py
from schemas import TodoCreate


def test_list_todos_empty(client):
    response = client.get("/todos")
    assert response.status_code == 200
    assert response.json() == []


def test_create_todo(client):
    response = client.post("/todos", json={
        "title": "API test",
        "description": "API test description"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "API test"
    assert data["description"] == "API test description"
    assert data["id"] is not None
    assert data["completed"] is False


def test_get_todo(client):
    # Create first
    create_resp = client.post("/todos", json={"title": "Get by ID test"})
    todo_id = create_resp.json()["id"]

    # Get
    response = client.get(f"/todos/{todo_id}")
    assert response.status_code == 200
    assert response.json()["id"] == todo_id


def test_get_todo_not_found(client):
    response = client.get("/todos/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Todo not found"


def test_update_todo(client):
    create_resp = client.post("/todos", json={"title": "Update test"})
    todo_id = create_resp.json()["id"]

    response = client.put(f"/todos/{todo_id}", json={
        "title": "Updated via API",
        "completed": True
    })
    assert response.status_code == 200
    assert response.json()["title"] == "Updated via API"
    assert response.json()["completed"] is True


def test_update_todo_not_found(client):
    response = client.put("/todos/999", json={"title": "Test"})
    assert response.status_code == 404


def test_delete_todo(client):
    create_resp = client.post("/todos", json={"title": "Delete test"})
    todo_id = create_resp.json()["id"]

    response = client.delete(f"/todos/{todo_id}")
    assert response.status_code == 204

    # Verify deletion
    get_resp = client.get(f"/todos/{todo_id}")
    assert get_resp.status_code == 404


def test_delete_todo_not_found(client):
    response = client.delete("/todos/999")
    assert response.status_code == 404


# Test health check
def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

## Error Handling Patterns

### Custom Exceptions
```python
# api/exceptions.py
from fastapi import HTTPException, status


class TodoNotFoundException(HTTPException):
    def __init__(self, todo_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo with id {todo_id} not found"
        )


class ValidationException(HTTPException):
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
```

### Using Custom Exceptions
```python
# crud.py
from exceptions import TodoNotFoundException

def get_todo(db: Session, todo_id: int) -> Todo:
    todo = db.get(Todo, todo_id)
    if not todo:
        raise TodoNotFoundException(todo_id)
    return todo
```

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| `sqlalchemy.exc.InvalidRequestError` | Check session scope, ensure `db.commit()` |
| Pydantic validation error | Verify `Field` constraints in schemas |
| `AttributeError: 'NoneType' object` | Check if query returns `None`, handle 404 |
| Migration issues | Use Alembic for schema changes |
| CORS errors | Configure `CORSMiddleware` in FastAPI |
| Database connection fails | Check `DATABASE_URL` format and credentials |
| `ModuleNotFoundError` | Install missing package with `pip install` |
| Circular import | Reorganize imports or use lazy loading |

## Performance Tips

### Database Optimization
- Use `select()` instead of `query()` for SQLAlchemy 2.0
- Use `.scalars()` for single-column results
- Add indexes to frequently queried columns
- Use `yield_per` for large result sets
- Consider connection pooling for production

### FastAPI Optimization
- Use `response_model` for automatic serialization
- Enable compression with `GZipMiddleware`
- Use async endpoints for I/O-bound operations
- Cache repeated computations
- Use dependency injection for reusable logic

## Requirements.txt Example
```
# api/requirements.txt
fastapi>=0.115.0
uvicorn[standard]>=0.34.0
sqlalchemy>=2.0.0
pydantic>=2.0.0
python-dotenv>=1.0.0
alembic>=1.13.0

# Testing
pytest>=8.0.0
pytest-cov>=4.0.0
httpx>=0.27.0
pytest-asyncio>=0.23.0

# Development
ruff>=0.3.0

# Optional: For production
psycopg2-binary>=2.9.9  # PostgreSQL support
gunicorn>=21.0.0  # Alternative ASGI server
```

## When to Use This Skill
- Creating or modifying FastAPI endpoints
- Designing SQLAlchemy models and relationships
- Implementing CRUD operations
- Writing tests for the API
- Troubleshooting database or API issues
- Optimizing FastAPI performance

## Related Skills
- `todo-app` - For project-specific context
- `sveltekit-tailwind` - For frontend integration
- `docker` - For containerizing the API
- `testing` - For comprehensive testing strategies
- `security` - For FastAPI security best practices
