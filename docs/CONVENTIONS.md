# Conventions

Advanced coding conventions and guidelines.

## Code Style

### General Principles

- Write readable, self-documenting code
- Follow the DRY principle (Don't Repeat Yourself)
- Keep functions small and focused
- Use meaningful names for variables and functions

### Python Conventions (PEP 8)

| Element | Convention | Example |
|---------|------------|---------|
| Modules | snake_case | `database.py` |
| Classes | PascalCase | `TodoResponse` |
| Functions | snake_case | `get_todo_by_id` |
| Constants | UPPER_SNAKE_CASE | `MAX_TITLE_LENGTH` |
| Variables | snake_case | `todo_item` |
| Private | leading underscore | `_validate_input` |

### File Naming

| Context | Convention | Example |
|---------|------------|---------|
| Python modules | snake_case | `crud.py`, `database.py` |
| Config files | kebab-case | `docker-compose.yml` |
| Dockerfiles | PascalCase + dot | `Dockerfile.api` |
| Documentation | UPPER_SNAKE_CASE | `TECHNICAL_GUIDE.md` |

### Python File Organization

```python
# 1. Standard library imports
import os
from datetime import datetime

# 2. Third-party imports
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

# 3. Local imports
from database import get_db
from models import Todo
from schemas import TodoCreate

# 4. Constants
MAX_TITLE_LENGTH = 200

# 5. Functions / Classes
def create_todo(db: Session, todo: TodoCreate) -> Todo:
    """Create a new todo item."""
    ...
```

---

## Type Hints

All Python code must use type hints:

```python
# Function signatures
def get_todo(db: Session, todo_id: int) -> Todo | None:
    ...

# Variable annotations (when not obvious)
todos: list[Todo] = []

# Pydantic models
class TodoCreate(BaseModel):
    title: str
    description: str | None = None
    completed: bool = False
```

---

## Docker Conventions

### Dockerfile Best Practices

- Use specific base image tags (e.g., `python:3.12-slim`, not `python:latest`)
- Group `RUN` commands to minimize layers
- Copy dependency files before application code (layer caching)
- Create and use non-root users
- Use `.dockerignore` to exclude unnecessary files
- Use `uv sync --frozen --no-dev` in production Dockerfiles (uv manages the cache automatically)

### Docker Compose

- Use environment variable substitution from `.env`
- Define explicit networks for service isolation
- Set resource limits (`deploy.resources.limits`)
- Configure restart policies (`restart: unless-stopped`)
- Use named volumes for persistent data

---

## Testing Conventions

### Test File Naming

- Unit tests: `test_*.py`
- Integration tests: `test_*_integration.py`

### Test Structure

```python
class TestTodoCrud:
    """Tests for todo CRUD operations."""

    def test_create_todo_with_valid_data(self, db_session):
        # Arrange
        todo_data = TodoCreate(title="Test task")

        # Act
        result = create_todo(db_session, todo_data)

        # Assert
        assert result.title == "Test task"
        assert result.completed is False

    def test_create_todo_without_title_fails(self, db_session):
        # Arrange / Act / Assert
        with pytest.raises(ValidationError):
            TodoCreate(title="")
```

---

## Git Conventions

### Branch Strategy

This project uses a **rebase-only** merge strategy (`develop` -> `main`).

```text
main     --A--B-------------------------------> (production)
                \
develop          C--D--E-----------------------> (integration)
                          \
feature/xxx                F--G----------------> (feature branches)
```

**Golden rules:**

1. **Never commit directly to `main`** - only via PR from `develop`
2. **Never commit directly to `develop`** - always via feature/fix branch
3. **Never `git merge main` into `develop`** - use `git rebase origin/main`
4. **Always rebase your branch on `develop`** before opening a PR

### Branch Naming

```text
feature/short-description
fix/issue-number-description
refactor/component-name
docs/update-readme
hotfix/issue-description
```

### Commit Messages (Gitmoji or Conventional)

```bash
# Use the interactive gitmoji tool
bun run commit
```

#### Gitmoji Format

`<emoji> <description>`

Examples:

- `✨ Add task filtering endpoint`
- `🐛 Fix database connection on startup`
- `🐳 Add health check to API Dockerfile`
- `📝 Document Docker Compose networking`
- `🔒️ Restrict PostgreSQL to internal network`

Common gitmojis:

| Emoji | When to use |
|-------|-------------|
| ✨ | New feature |
| 🐛 | Bug fix |
| 📝 | Documentation |
| 🐳 | Docker-related |
| 🔒️ | Security fix |
| ♻️ | Refactor |
| 🔧 | Configuration |
| ✅ | Add tests |
| 🔥 | Remove code/files |
| ⬆️ | Upgrade dependency |

Full reference: [gitmoji.dev](https://gitmoji.dev)

#### Conventional Commits Format

`<type>(scope): <description>`

Examples:

- `feat(api): Add task filtering endpoint`
- `fix(db): Fix connection retry on startup`
- `docs: Update Docker Compose networking`

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`

---

## Documentation

### Code Comments

```python
# Single line comment for brief explanations

# Multi-line comment for complex logic
# explaining the why, not the what

def public_function(param: str) -> None:
    """Docstring for public functions.

    Args:
        param: Description of the parameter.

    Returns:
        Description of the return value.
    """
    ...
```

### Markdown Style

- Follow markdownlint rules
- No trailing whitespace
- Single blank line between sections
- Use fenced code blocks with language identifier

---

*Last updated: 2026-04-25*
