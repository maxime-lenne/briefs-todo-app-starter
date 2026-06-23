# Testing Skill

## Testing Strategy
| Layer | Tools | Coverage | Responsibility |
|-------|-------|----------|----------------|
| Unit (Python) | pytest + pytest-cov | API models, schemas, CRUD | API business logic |
| Unit (TypeScript) | vitest | Utility functions, components | Frontend logic |
| Integration | pytest + TestClient | API endpoints | API routes and middleware |
| E2E | Playwright | Full user flows | End-to-end user journeys |
| Linting | Ruff, ESLint, markdownlint | Code quality | Style and conventions |

## Python Testing (pytest)

### Setup

#### requirements.txt
```
# api/requirements.txt
pytest>=8.0.0
pytest-cov>=4.0.0
pytest-asyncio>=0.23.0
httpx>=0.27.0
sqlalchemy>=2.0.0
```

#### Test Directory Structure
```
api/
├── tests/
│   ├── __init__.py
│   ├── conftest.py        # Fixtures
│   ├── test_crud.py       # CRUD tests
│   ├── test_models.py     # Model tests
│   ├── test_routes.py     # API endpoint tests
│   ├── test_schemas.py    # Pydantic schema tests
│   └── test_dependencies.py # Dependency tests
```

### Fixtures

#### conftest.py
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
from models import Todo

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


@pytest.fixture
def test_todo(session):
    """Create a test todo for use in tests."""
    from schemas import TodoCreate
    from crud import create_todo
    return create_todo(session, TodoCreate(title="Test Todo", description="Test Description"))
```

### CRUD Tests

#### test_crud.py
```python
# api/tests/test_crud.py
from datetime import datetime
from schemas import TodoCreate, TodoUpdate
from models import Todo


def test_create_todo(session):
    """Test creating a new todo."""
    from crud import create_todo
    todo_data = TodoCreate(title="Test task", description="Test description")
    todo = create_todo(session, todo_data)
    
    assert todo.id is not None
    assert todo.title == "Test task"
    assert todo.description == "Test description"
    assert todo.completed is False
    assert isinstance(todo.created_at, datetime)
    assert todo.updated_at is None


def test_create_todo_minimal(session):
    """Test creating a todo with minimal data."""
    from crud import create_todo
    todo_data = TodoCreate(title="Minimal task")
    todo = create_todo(session, todo_data)
    
    assert todo.title == "Minimal task"
    assert todo.description is None
    assert todo.completed is False


def test_get_todo(session, test_todo):
    """Test getting a specific todo by ID."""
    from crud import get_todo
    fetched = get_todo(session, test_todo.id)
    
    assert fetched is not None
    assert fetched.id == test_todo.id
    assert fetched.title == test_todo.title


def test_get_todo_not_found(session):
    """Test getting a non-existent todo."""
    from crud import get_todo
    assert get_todo(session, 999) is None


def test_get_todos_empty(session):
    """Test getting todos from empty database."""
    from crud import get_todos
    todos = get_todos(session)
    assert todos == []


def test_get_todos_with_pagination(session):
    """Test pagination in get_todos."""
    from crud import create_todo, get_todos
    from schemas import TodoCreate
    
    # Create 5 todos
    for i in range(5):
        create_todo(session, TodoCreate(title=f"Task {i}"))
    
    # Get first 3
    todos = get_todos(session, skip=0, limit=3)
    assert len(todos) == 3
    
    # Get next 2
    todos = get_todos(session, skip=3, limit=3)
    assert len(todos) == 2


def test_update_todo(session, test_todo):
    """Test updating a todo."""
    from crud import update_todo
    
    updated = update_todo(session, test_todo.id, TodoUpdate(
        title="Updated title",
        description="Updated description",
        completed=True
    ))
    
    assert updated is not None
    assert updated.id == test_todo.id
    assert updated.title == "Updated title"
    assert updated.description == "Updated description"
    assert updated.completed is True
    assert updated.updated_at is not None


def test_update_todo_partial(session, test_todo):
    """Test partial update of a todo."""
    from crud import update_todo
    
    # Only update title
    updated = update_todo(session, test_todo.id, TodoUpdate(title="New title"))
    
    assert updated.title == "New title"
    assert updated.description == test_todo.description  # Unchanged
    assert updated.completed == test_todo.completed  # Unchanged


def test_update_todo_not_found(session):
    """Test updating a non-existent todo."""
    from crud import update_todo
    assert update_todo(session, 999, TodoUpdate(title="Test")) is None


def test_delete_todo(session, test_todo):
    """Test deleting a todo."""
    from crud import delete_todo, get_todo
    
    assert delete_todo(session, test_todo.id) is True
    assert get_todo(session, test_todo.id) is None


def test_delete_todo_not_found(session):
    """Test deleting a non-existent todo."""
    from crud import delete_todo
    assert delete_todo(session, 999) is False


def test_delete_all_todos(session):
    """Test deleting all todos."""
    from crud import create_todo, delete_all_todos, get_todos
    from schemas import TodoCreate
    
    # Create 3 todos
    for i in range(3):
        create_todo(session, TodoCreate(title=f"Task {i}"))
    
    # Verify 3 exist
    assert len(get_todos(session)) == 3
    
    # Delete all
    count = delete_all_todos(session)
    assert count == 3
    
    # Verify none remain
    assert len(get_todos(session)) == 0
```

### Model Tests

#### test_models.py
```python
# api/tests/test_models.py
import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Todo, Base

# Create test engine
engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)


def test_todo_model_creation():
    """Test Todo model creation."""
    db = Session()
    try:
        todo = Todo(
            title="Test",
            description="Description",
            completed=False
        )
        db.add(todo)
        db.commit()
        
        assert todo.id is not None
        assert todo.title == "Test"
        assert isinstance(todo.created_at, datetime)
    finally:
        db.close()


def test_todo_model_repr():
    """Test Todo model __repr__."""
    todo = Todo(id=1, title="Test", completed=False)
    assert repr(todo) == "<Todo(id=1, title='Test')>"


def test_todo_model_tablename():
    """Test Todo model table name."""
    assert Todo.__tablename__ == "todos"


def test_todo_model_columns():
    """Test Todo model columns."""
    assert hasattr(Todo, 'id')
    assert hasattr(Todo, 'title')
    assert hasattr(Todo, 'description')
    assert hasattr(Todo, 'completed')
    assert hasattr(Todo, 'created_at')
    assert hasattr(Todo, 'updated_at')
```

### Schema Tests

#### test_schemas.py
```python
# api/tests/test_schemas.py
import pytest
from pydantic import ValidationError
from datetime import datetime
from schemas import TodoBase, TodoCreate, TodoUpdate, TodoResponse


def test_todo_base_valid():
    """Test TodoBase with valid data."""
    todo = TodoBase(
        title="Test",
        description="Description",
        completed=False
    )
    assert todo.title == "Test"
    assert todo.description == "Description"
    assert todo.completed is False


def test_todo_base_missing_title():
    """Test TodoBase with missing required title."""
    with pytest.raises(ValidationError) as exc_info:
        TodoBase(description="Description")
    assert "title" in str(exc_info.value)


def test_todo_base_title_too_short():
    """Test TodoBase with title too short."""
    with pytest.raises(ValidationError) as exc_info:
        TodoBase(title="")
    assert "min_length" in str(exc_info.value)


def test_todo_base_title_too_long():
    """Test TodoBase with title too long."""
    with pytest.raises(ValidationError) as exc_info:
        TodoBase(title="a" * 201)
    assert "max_length" in str(exc_info.value)


def test_todo_base_description_too_long():
    """Test TodoBase with description too long."""
    with pytest.raises(ValidationError) as exc_info:
        TodoBase(title="Test", description="a" * 501)
    assert "max_length" in str(exc_info.value)


def test_todo_create_default_values():
    """Test TodoCreate default values."""
    todo = TodoCreate(title="Test")
    assert todo.title == "Test"
    assert todo.description is None
    assert todo.completed is False


def test_todo_update_all_optional():
    """Test TodoUpdate with all fields optional."""
    todo = TodoUpdate()
    assert todo.title is None
    assert todo.description is None
    assert todo.completed is None


def test_todo_response_from_attributes():
    """Test TodoResponse from_attributes config."""
    assert TodoResponse.model_config == {"from_attributes": True}


def test_todo_response_fields():
    """Test TodoResponse fields."""
    todo = TodoResponse(
        id=1,
        title="Test",
        description="Description",
        completed=False,
        created_at=datetime.now(),
        updated_at=None
    )
    assert todo.id == 1
    assert todo.title == "Test"
    assert todo.created_at is not None
```

### API Endpoint Tests

#### test_routes.py
```python
# api/tests/test_routes.py
from fastapi import status
from schemas import TodoCreate


def test_list_todos_empty(client):
    """Test listing todos from empty database."""
    response = client.get("/todos")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_create_todo(client):
    """Test creating a new todo."""
    response = client.post("/todos", json={
        "title": "API test",
        "description": "API test description"
    })
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == "API test"
    assert data["description"] == "API test description"
    assert data["id"] is not None
    assert data["completed"] is False
    assert "created_at" in data


def test_create_todo_minimal(client):
    """Test creating a todo with minimal data."""
    response = client.post("/todos", json={"title": "Minimal"})
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == "Minimal"
    assert data["description"] is None


def test_create_todo_missing_title(client):
    """Test creating a todo without title."""
    response = client.post("/todos", json={"description": "Test"})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_todo(client):
    """Test getting a specific todo."""
    # Create first
    create_resp = client.post("/todos", json={"title": "Get by ID test"})
    todo_id = create_resp.json()["id"]

    # Get
    response = client.get(f"/todos/{todo_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == todo_id
    assert response.json()["title"] == "Get by ID test"


def test_get_todo_not_found(client):
    """Test getting a non-existent todo."""
    response = client.get("/todos/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Todo not found"


def test_update_todo(client):
    """Test updating a todo."""
    create_resp = client.post("/todos", json={"title": "Update test"})
    todo_id = create_resp.json()["id"]

    response = client.put(f"/todos/{todo_id}", json={
        "title": "Updated via API",
        "completed": True
    })
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["title"] == "Updated via API"
    assert response.json()["completed"] is True


def test_update_todo_not_found(client):
    """Test updating a non-existent todo."""
    response = client.put("/todos/999", json={"title": "Test"})
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_todo_partial(client):
    """Test partial update of a todo."""
    create_resp = client.post("/todos", json={"title": "Partial update"})
    todo_id = create_resp.json()["id"]

    response = client.put(f"/todos/{todo_id}", json={
        "description": "Added description"
    })
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["title"] == "Partial update"  # Unchanged
    assert response.json()["description"] == "Added description"


def test_delete_todo(client):
    """Test deleting a todo."""
    create_resp = client.post("/todos", json={"title": "Delete test"})
    todo_id = create_resp.json()["id"]

    response = client.delete(f"/todos/{todo_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify deletion
    get_resp = client.get(f"/todos/{todo_id}")
    assert get_resp.status_code == status.HTTP_404_NOT_FOUND


def test_delete_todo_not_found(client):
    """Test deleting a non-existent todo."""
    response = client.delete("/todos/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND


# Test health check
def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "healthy"


# Test root endpoint
def test_root_endpoint(client):
    """Test root endpoint returns OpenAPI schema."""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert "openapi" in response.json()


# Test docs endpoints
def test_docs_endpoint(client):
    """Test Swagger UI endpoint."""
    response = client.get("/docs")
    assert response.status_code == status.HTTP_200_OK
    assert "swagger-ui" in response.text.lower()


def test_redoc_endpoint(client):
    """Test ReDoc endpoint."""
    response = client.get("/redoc")
    assert response.status_code == status.HTTP_200_OK
    assert "redoc" in response.text.lower()


# Test OpenAPI schema
def test_openapi_schema(client):
    """Test OpenAPI schema endpoint."""
    response = client.get("/openapi.json")
    assert response.status_code == status.HTTP_200_OK
    schema = response.json()
    assert schema["openapi"] == "3.1.0"
    assert schema["info"]["title"] == "To-Do API"
    assert "/todos" in schema["paths"]
```

## TypeScript Testing (vitest)

### Setup

#### package.json
```json
{
  "scripts": {
    "test": "vitest",
    "test:coverage": "vitest --coverage",
    "test:watch": "vitest watch"
  },
  "devDependencies": {
    "vitest": "^1.0.0",
    "@testing-library/svelte": "^4.0.0",
    "jsdom": "^24.0.0",
    "@vitest/coverage-v8": "^1.0.0"
  }
}
```

#### vite.config.ts
```typescript
// vite.config.ts
import { defineConfig } from 'vitest/config';
import { svelte } from '@sveltejs/vite-plugin-svelte';

export default defineConfig({
  plugins: [svelte()],
  test: {
    globals: true,
    environment: 'jsdom',
    include: ['src/**/*.{test,spec}.{js,ts}'],
    coverage: {
      reporter: ['text', 'json', 'html'],
      include: ['src/lib/**/*.ts', 'src/lib/**/*.svelte']
    }
  }
});
```

### API Client Tests

#### api.test.ts
```typescript
// src/lib/api.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { api } from './api';

// Mock fetch
global.fetch = vi.fn();

describe('API Client', () => {
  beforeEach(() => {
    fetch.mockReset();
  });

  it('should list todos', async () => {
    const mockTodos = [
      { id: 1, title: 'Task 1', completed: false },
      { id: 2, title: 'Task 2', completed: true }
    ];
    
    fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockTodos),
      status: 200,
      statusText: 'OK'
    });

    const todos = await api.listTodos();
    expect(todos).toEqual(mockTodos);
    expect(fetch).toHaveBeenCalledWith('/api/todos', expect.anything());
  });

  it('should handle API errors', async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      statusText: 'Server Error'
    });

    await expect(api.listTodos()).rejects.toThrow('500 Server Error');
  });

  it('should create a todo', async () => {
    const newTodo = { id: 1, title: 'New Task', completed: false };
    
    fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(newTodo),
      status: 201,
      statusText: 'Created'
    });

    const created = await api.createTodo({ title: 'New Task' });
    expect(created).toEqual(newTodo);
    expect(fetch).toHaveBeenCalledWith('/api/todos', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: 'New Task' })
    });
  });

  it('should handle 204 No Content', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      status: 204,
      statusText: 'No Content'
    });

    const result = await api.deleteTodo(1);
    expect(result).toBeUndefined();
  });
});
```

### Component Tests

#### TodoItem.test.ts
```typescript
// src/lib/components/TodoItem.test.ts
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/svelte';
import TodoItem from './TodoItem.svelte';

const mockTodo = {
  id: 1,
  title: 'Test task',
  description: 'Test description',
  completed: false,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: null
};

const mockCompletedTodo = {
  ...mockTodo,
  id: 2,
  title: 'Completed task',
  completed: true
};

describe('TodoItem', () => {
  it('renders task title', () => {
    render(TodoItem, {
      todo: mockTodo,
      onToggle: vi.fn(),
      onSave: vi.fn(),
      onDelete: vi.fn()
    });
    
    expect(screen.getByText('Test task')).toBeInTheDocument();
  });

  it('renders task description when present', () => {
    render(TodoItem, {
      todo: mockTodo,
      onToggle: vi.fn(),
      onSave: vi.fn(),
      onDelete: vi.fn()
    });
    
    expect(screen.getByText('Test description')).toBeInTheDocument();
  });

  it('does not render description when null', () => {
    const todoWithoutDesc = { ...mockTodo, description: null };
    render(TodoItem, {
      todo: todoWithoutDesc,
      onToggle: vi.fn(),
      onSave: vi.fn(),
      onDelete: vi.fn()
    });
    
    expect(screen.queryByText('Test description')).not.toBeInTheDocument();
  });

  it('calls onToggle when checkbox is clicked', async () => {
    const onToggle = vi.fn();
    render(TodoItem, {
      todo: mockTodo,
      onToggle,
      onSave: vi.fn(),
      onDelete: vi.fn()
    });
    
    const checkbox = screen.getByRole('checkbox');
    await fireEvent.click(checkbox);
    
    expect(onToggle).toHaveBeenCalledWith(1, true);
  });

  it('shows edit form when edit button is clicked', async () => {
    render(TodoItem, {
      todo: mockTodo,
      onToggle: vi.fn(),
      onSave: vi.fn(),
      onDelete: vi.fn()
    });
    
    const editButton = screen.getByLabelText('Edit Test task');
    await fireEvent.click(editButton);
    
    expect(screen.getByPlaceholderText('Title')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Test task')).toBeInTheDocument();
  });

  it('applies strikethrough to completed tasks', () => {
    render(TodoItem, {
      todo: mockCompletedTodo,
      onToggle: vi.fn(),
      onSave: vi.fn(),
      onDelete: vi.fn()
    });
    
    const title = screen.getByText('Completed task');
    expect(title).toHaveClass('line-through');
    expect(title).toHaveClass('text-slate-400');
  });

  it('calls onDelete when delete button is clicked', async () => {
    const onDelete = vi.fn();
    render(TodoItem, {
      todo: mockTodo,
      onToggle: vi.fn(),
      onSave: vi.fn(),
      onDelete
    });
    
    const deleteButton = screen.getByLabelText('Delete Test task');
    await fireEvent.click(deleteButton);
    
    expect(onDelete).toHaveBeenCalledWith(1);
  });

  it('displays save and cancel buttons in edit mode', async () => {
    render(TodoItem, {
      todo: mockTodo,
      onToggle: vi.fn(),
      onSave: vi.fn(),
      onDelete: vi.fn()
    });
    
    const editButton = screen.getByLabelText('Edit Test task');
    await fireEvent.click(editButton);
    
    expect(screen.getByText('Save')).toBeInTheDocument();
    expect(screen.getByText('Cancel')).toBeInTheDocument();
  });

  it('calls onSave when save button is clicked', async () => {
    const onSave = vi.fn();
    render(TodoItem, {
      todo: mockTodo,
      onToggle: vi.fn(),
      onSave,
      onDelete: vi.fn()
    });
    
    // Enter edit mode
    const editButton = screen.getByLabelText('Edit Test task');
    await fireEvent.click(editButton);
    
    // Click save
    const saveButton = screen.getByText('Save');
    await fireEvent.click(saveButton);
    
    expect(onSave).toHaveBeenCalledWith(1, expect.objectContaining({
      title: 'Test task'
    }));
  });
});
```

### Page Tests

#### +page.test.ts
```typescript
// src/routes/+page.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/svelte';
import Page from './+page.svelte';

// Mock the API module
vi.mock('$lib/api', () => ({
  api: {
    listTodos: vi.fn(),
    createTodo: vi.fn(),
    updateTodo: vi.fn(),
    deleteTodo: vi.fn()
  }
}));

import { api } from '$lib/api';

const mockTodos = [
  { id: 1, title: 'Task 1', description: null, completed: false, created_at: '2024-01-01', updated_at: null },
  { id: 2, title: 'Task 2', description: 'Description', completed: true, created_at: '2024-01-02', updated_at: null }
];

describe('Main Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the page title', () => {
    vi.mocked(api.listTodos).mockResolvedValue([]);
    
    render(Page);
    
    expect(screen.getByText('To-Do')).toBeInTheDocument();
    expect(screen.getByText('A simple task management application')).toBeInTheDocument();
  });

  it('loads and displays todos on mount', async () => {
    vi.mocked(api.listTodos).mockResolvedValue(mockTodos);
    
    render(Page);
    
    await waitFor(() => {
      expect(api.listTodos).toHaveBeenCalledTimes(1);
    });
    
    expect(screen.getByText('Task 1')).toBeInTheDocument();
    expect(screen.getByText('Task 2')).toBeInTheDocument();
  });

  it('displays loading state initially', async () => {
    vi.mocked(api.listTodos).mockImplementation(() => 
      new Promise(resolve => setTimeout(() => resolve(mockTodos), 100))
    );
    
    render(Page);
    
    expect(screen.getByText('Loading...')).toBeInTheDocument();
    
    await waitFor(() => {
      expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
    });
  });

  it('filters todos by status', async () => {
    vi.mocked(api.listTodos).mockResolvedValue(mockTodos);
    
    render(Page);
    
    await waitFor(() => {
      expect(screen.getByText('Task 1')).toBeInTheDocument();
    });
    
    // Switch to active filter
    fireEvent.click(screen.getByText('Active'));
    
    expect(screen.getByText('Task 1')).toBeInTheDocument();
    expect(screen.queryByText('Task 2')).not.toBeInTheDocument();
    
    // Switch to completed filter
    fireEvent.click(screen.getByText('Completed'));
    
    expect(screen.queryByText('Task 1')).not.toBeInTheDocument();
    expect(screen.getByText('Task 2')).toBeInTheDocument();
  });

  it('displays empty state when no todos', async () => {
    vi.mocked(api.listTodos).mockResolvedValue([]);
    
    render(Page);
    
    await waitFor(() => {
      expect(screen.getByText('No tasks found')).toBeInTheDocument();
    });
  });

  it('displays stats correctly', async () => {
    vi.mocked(api.listTodos).mockResolvedValue(mockTodos);
    
    render(Page);
    
    await waitFor(() => {
      expect(screen.getByText('2 total')).toBeInTheDocument();
      expect(screen.getByText('1 active')).toBeInTheDocument();
      expect(screen.getByText('1 completed')).toBeInTheDocument();
    });
  });

  it('shows error message on API failure', async () => {
    vi.mocked(api.listTodos).mockRejectedValue(new Error('Network error'));
    
    render(Page);
    
    await waitFor(() => {
      expect(screen.getByText('Network error')).toBeInTheDocument();
    });
  });

  it('can create a new todo', async () => {
    vi.mocked(api.listTodos).mockResolvedValue([]);
    vi.mocked(api.createTodo).mockResolvedValue({
      id: 1,
      title: 'New Task',
      description: null,
      completed: false,
      created_at: '2024-01-01',
      updated_at: null
    });
    
    render(Page);
    
    const input = screen.getByPlaceholderText('What needs to be done?');
    const button = screen.getByText('Add Task');
    
    fireEvent.input(input, { target: { value: 'New Task' } });
    fireEvent.click(button);
    
    await waitFor(() => {
      expect(api.createTodo).toHaveBeenCalledWith({
        title: 'New Task',
        description: null
      });
    });
    
    expect(screen.getByText('New Task')).toBeInTheDocument();
  });
});
```

## E2E Testing (Playwright)

### Setup

#### Install Playwright
```bash
npm init playwright@latest
```

#### playwright.config.js
```javascript
// playwright.config.js
module.exports = {
  testDir: './e2e',
  fullyParallel: true,
  use: {
    baseURL: process.env.CI ? 'http://localhost:5173' : 'http://localhost:5173',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
  },
};
```

### Test Files

#### todo.spec.ts
```typescript
// e2e/todo.spec.ts
import { test, expect } from '@playwright/test';

test('should display the to-do app', async ({ page }) => {
  await page.goto('/');
  
  await expect(page).toHaveTitle('To-Do');
  await expect(page.getByRole('heading', { name: 'To-Do' })).toBeVisible();
});

test('should add a new todo', async ({ page }) => {
  await page.goto('/');
  
  // Fill in the title
  await page.fill('input[placeholder="What needs to be done?"]', 'Playwright test');
  
  // Click add button
  await page.click('button[type="submit"]');
  
  // Verify the todo was added
  await expect(page.getByText('Playwright test')).toBeVisible();
  
  // Verify the input is cleared
  await expect(page.getByPlaceholder('What needs to be done?')).toHaveValue('');
});

test('should add a todo with description', async ({ page }) => {
  await page.goto('/');
  
  // Fill in title and description
  await page.fill('input[placeholder="What needs to be done?"]', 'Task with description');
  await page.fill('textarea[placeholder="Additional details..."]', 'This is a test description');
  
  // Click add button
  await page.click('button[type="submit"]');
  
  // Verify both are displayed
  await expect(page.getByText('Task with description')).toBeVisible();
  await expect(page.getByText('This is a test description')).toBeVisible();
});

test('should not add empty todo', async ({ page }) => {
  await page.goto('/');
  
  // Try to add without title
  await page.click('button[type="submit"]');
  
  // Verify no todo was added (still showing "No tasks found")
  await expect(page.getByText('No tasks found')).toBeVisible();
});

test('should toggle todo completion', async ({ page }) => {
  await page.goto('/');
  
  // Add a todo
  await page.fill('input[placeholder="What needs to be done?"]', 'Toggle test');
  await page.click('button[type="submit"]');
  
  // Find the checkbox
  const checkbox = page.getByRole('checkbox');
  
  // Click to toggle
  await checkbox.click();
  
  // Verify strikethrough is applied
  await expect(page.getByText('Toggle test')).toHaveClass(/line-through/);
  
  // Click again to un-toggle
  await checkbox.click();
  
  // Verify strikethrough is removed
  await expect(page.getByText('Toggle test')).not.toHaveClass(/line-through/);
});

test('should edit a todo', async ({ page }) => {
  await page.goto('/');
  
  // Add a todo
  await page.fill('input[placeholder="What needs to be done?"]', 'Edit test');
  await page.click('button[type="submit"]');
  
  // Click edit button
  await page.click('button[aria-label="Edit Edit test"]');
  
  // Clear and fill with new title
  await page.fill('input[placeholder="Title"]', 'Updated title');
  
  // Click save
  await page.click('button:text("Save")');
  
  // Verify update
  await expect(page.getByText('Updated title')).toBeVisible();
  await expect(page.getByText('Edit test')).not.toBeVisible();
});

test('should cancel edit', async ({ page }) => {
  await page.goto('/');
  
  // Add a todo
  await page.fill('input[placeholder="What needs to be done?"]', 'Cancel test');
  await page.click('button[type="submit"]');
  
  // Click edit button
  await page.click('button[aria-label="Edit Cancel test"]');
  
  // Clear title
  await page.fill('input[placeholder="Title"]', '');
  
  // Click cancel
  await page.click('button:text("Cancel")');
  
  // Verify original title is still there
  await expect(page.getByText('Cancel test')).toBeVisible();
});

test('should delete a todo', async ({ page }) => {
  await page.goto('/');
  
  // Add a todo
  await page.fill('input[placeholder="What needs to be done?"]', 'Delete test');
  await page.click('button[type="submit"]');
  
  // Verify it exists
  await expect(page.getByText('Delete test')).toBeVisible();
  
  // Click delete button
  await page.click('button[aria-label="Delete Delete test"]');
  
  // Verify it's gone
  await expect(page.getByText('Delete test')).not.toBeVisible();
  await expect(page.getByText('No tasks found')).toBeVisible();
});

test('should filter todos', async ({ page }) => {
  await page.goto('/');
  
  // Add active and completed todos
  await page.fill('input[placeholder="What needs to be done?"]', 'Active task');
  await page.click('button[type="submit"]');
  
  await page.fill('input[placeholder="What needs to be done?"]', 'Completed task');
  await page.click('button[type="submit"]');
  
  // Toggle the second task
  const checkboxes = page.getByRole('checkbox');
  await checkboxes.last().click();
  
  // Filter by active
  await page.click('button:text("Active")');
  await expect(page.getByText('Active task')).toBeVisible();
  await expect(page.getByText('Completed task')).not.toBeVisible();
  
  // Filter by completed
  await page.click('button:text("Completed")');
  await expect(page.getByText('Active task')).not.toBeVisible();
  await expect(page.getByText('Completed task')).toBeVisible();
  
  // Filter by all
  await page.click('button:text("All")');
  await expect(page.getByText('Active task')).toBeVisible();
  await expect(page.getByText('Completed task')).toBeVisible();
});

test('should display correct stats', async ({ page }) => {
  await page.goto('/');
  
  // Add todos
  await page.fill('input[placeholder="What needs to be done?"]', 'Task 1');
  await page.click('button[type="submit"]');
  
  await page.fill('input[placeholder="What needs to be done?"]', 'Task 2');
  await page.click('button[type="submit"]');
  
  // Toggle one
  const checkboxes = page.getByRole('checkbox');
  await checkboxes.first().click();
  
  // Verify stats
  await expect(page.getByText('2 total')).toBeVisible();
  await expect(page.getByText('1 active')).toBeVisible();
  await expect(page.getByText('1 completed')).toBeVisible();
});

test('should show error message on API failure', async ({ page }) => {
  // This test would need a mock API that returns errors
  // For now, just verify the page structure
  await page.goto('/');
  
  await expect(page.getByRole('heading', { name: 'To-Do' })).toBeVisible();
});

// Mobile tests
test.describe('Mobile', () => {
  test.use({ viewport: { width: 375, height: 667 } });
  
  test('should display correctly on mobile', async ({ page }) => {
    await page.goto('/');
    
    await expect(page).toHaveTitle('To-Do');
    await expect(page.getByRole('heading', { name: 'To-Do' })).toBeVisible();
  });
  
  test('should have responsive filters', async ({ page }) => {
    await page.goto('/');
    
    // Filters should be in a column on mobile
    const filters = page.getByRole('button', { name: /All|Active|Completed/ });
    await expect(filters).toHaveCount(3);
  });
});
```

## GitHub Actions Workflows

### test.yml
```yaml
# .github/workflows/test.yml
name: Tests

on:
  push:
    branches: [develop, main]
  pull_request:
    branches: [develop, main]

jobs:
  python-lint:
    name: Python Linting (Ruff)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install Ruff
        run: pip install ruff

      - name: Run Ruff
        run: |
          cd api
          ruff check .

  python-tests:
    name: Python Tests
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_pass
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v6

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          cd api
          pip install -r requirements.txt
          pip install pytest pytest-cov httpx pytest-asyncio

      - name: Run tests with coverage
        run: |
          cd api
          pytest --cov=./ --cov-report=xml --cov-report=term
        env:
          DATABASE_URL: postgresql://test_user:test_pass@localhost:5432/test_db

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: ./api/coverage.xml
          flags: api

  frontend-lint:
    name: Frontend Linting
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6

      - name: Set up Node
        uses: actions/setup-node@v4
        with:
          node-version: '22'

      - name: Install dependencies
        run: |
          cd web
          npm ci

      - name: Type checking
        run: |
          cd web
          npm run check

      - name: Build test
        run: |
          cd web
          npm run build

  frontend-tests:
    name: Frontend Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6

      - name: Set up Node
        uses: actions/setup-node@v4
        with:
          node-version: '22'

      - name: Install dependencies
        run: |
          cd web
          npm ci

      - name: Run tests
        run: |
          cd web
          npm test

  e2e-tests:
    name: E2E Tests
    runs-on: ubuntu-latest
    needs: [python-tests, frontend-lint, frontend-tests]
    steps:
      - uses: actions/checkout@v6

      - name: Start services with Docker Compose
        run: |
          docker compose up --build -d
          sleep 15

      - name: Set up Node
        uses: actions/setup-node@v4
        with:
          node-version: '22'

      - name: Install Playwright
        run: |
          cd web
          npm init playwright@latest
          npx playwright install --with-deps

      - name: Run E2E tests
        run: |
          cd web
          npx playwright test

      - name: Upload test results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: playwright-report
          path: web/playwright-report/
          retention-days: 30

  coverage:
    name: Coverage Report
    runs-on: ubuntu-latest
    needs: [python-tests, frontend-tests]
    steps:
      - uses: actions/checkout@v6

      - name: Download API coverage
        uses: actions/download-artifact@v4
        with:
          name: coverage-api
          path: api/

      - name: Download Frontend coverage
        uses: actions/download-artifact@v4
        with:
          name: coverage-web
          path: web/

      - name: Combine coverage
        run: |
          # Combine coverage reports if needed
          echo "Coverage reports collected"

      - name: Upload to Codecov
        uses: codecov/codecov-action@v4
        with:
          files: ./api/coverage.xml,./web/coverage/coverage-final.json
          flags: combined
```

## Test Coverage Goals
| Component | Target Coverage | Current |
|-----------|-----------------|---------|
| API Models | 100% | Track |
| API Schemas | 100% | Track |
| API CRUD | 100% | Track |
| API Routes | 95% | Track |
| Frontend Components | 80% | Track |
| Frontend Utility Functions | 90% | Track |
| E2E Flows | 100% | Track |

## Coverage Badges
Add these to your README.md:

```markdown
![API Coverage](https://img.shields.io/codecov/c/github/owner/repo/api?flag=api&label=API%20Coverage)
![Frontend Coverage](https://img.shields.io/codecov/c/github/owner/repo/web?flag=web&label=Frontend%20Coverage)
```

## When to Use This Skill
- Writing unit tests for API or frontend
- Writing integration tests for API endpoints
- Writing E2E tests for user journeys
- Setting up test fixtures and mocks
- Configuring test coverage
- Debugging failing tests
- Implementing CI/CD test pipelines

## Related Skills
- `todo-app` - For project-specific context
- `fastapi-sqlalchemy` - For FastAPI testing patterns
- `sveltekit-tailwind` - For SvelteKit testing patterns
- `docker` - For containerized testing
- `security` - For security testing
