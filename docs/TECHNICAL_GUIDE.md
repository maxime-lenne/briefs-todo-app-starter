# Technical Guide

Detailed guide for technical implementation aspects.

## Tech Stack

| Category | Technology | Version |
|----------|------------|---------|
| API Framework | FastAPI | >= 0.115.0 |
| ASGI Server | Uvicorn | >= 0.34.0 |
| ORM | SQLAlchemy | >= 2.0.0 |
| Validation | Pydantic | >= 2.0.0 |
| Database | SQLite (built-in) / PostgreSQL (optional) | - / 16 |
| Frontend | SvelteKit (Svelte 5 runes) | ^2.15 (svelte ^5.16) |
| Styling | Tailwind CSS | ^4.0 |
| Bundler | Vite | ^6.0 |
| Language (frontend) | TypeScript | ^5.7 |
| Python | CPython | >= 3.10 |
| Package Manager (JS) | Bun | >= 1.3 |
| Package Manager (Python) | uv | >= 0.5 |
| Git Hooks | Husky | ^9.1 |
| Commit Lint | commitlint | ^20.4 |
| Markdown Lint | markdownlint-cli | ^0.48 |

---

## Architecture

```text
┌────────────────────┐        ┌─────────────────────┐        ┌────────────┐
│  SvelteKit (Vite)  │  ───▶  │   FastAPI (uvicorn) │  ───▶  │  Database  │
│   localhost:5173   │        │    localhost:8000   │        │  (SQLite)  │
└────────────────────┘        └─────────────────────┘        └────────────┘
       (browser)              (proxied via /api in dev)        (todo.db)
```

The Vite dev server proxies `/api/*` requests to the FastAPI service, so the API needs no CORS
configuration during development. In production, serve the SvelteKit build behind the same origin
as the API (reverse proxy) or enable CORS on the FastAPI app.

---

## FastAPI Application

### Database Connection (`database.py`)

```python
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./todo.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Models (`models.py`)

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from database import Base


class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(String(500), nullable=True)
    completed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### Schemas (`schemas.py`)

```python
from datetime import datetime
from pydantic import BaseModel, Field


class TodoBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=500)
    completed: bool = False


class TodoCreate(TodoBase):
    pass


class TodoUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=500)
    completed: bool | None = None


class TodoResponse(TodoBase):
    id: int
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
```

### Endpoints (`main.py`)

```python
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

import crud
import schemas
from database import Base, engine, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI(title="To-Do API", version="0.1.0")


@app.get("/todos", response_model=list[schemas.TodoResponse])
def list_todos(db: Session = Depends(get_db)):
    return crud.get_todos(db)


@app.get("/todos/{todo_id}", response_model=schemas.TodoResponse)
def get_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = crud.get_todo(db, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@app.post("/todos", response_model=schemas.TodoResponse, status_code=201)
def create_todo(todo: schemas.TodoCreate, db: Session = Depends(get_db)):
    return crud.create_todo(db, todo)


@app.put("/todos/{todo_id}", response_model=schemas.TodoResponse)
def update_todo(todo_id: int, todo: schemas.TodoUpdate, db: Session = Depends(get_db)):
    updated = crud.update_todo(db, todo_id, todo)
    if not updated:
        raise HTTPException(status_code=404, detail="Todo not found")
    return updated


@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    if not crud.delete_todo(db, todo_id):
        raise HTTPException(status_code=404, detail="Todo not found")
```

---

## SvelteKit Frontend

### Vite Configuration (`vite.config.ts`)

The Vite dev server proxies `/api/*` to the FastAPI service, removing the need for CORS in
development.

```ts
import { sveltekit } from '@sveltejs/kit/vite';
import tailwindcss from '@tailwindcss/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [tailwindcss(), sveltekit()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
});
```

### Tailwind v4 Entry (`src/app.css`)

Tailwind v4 is loaded with a single CSS-first import. No `tailwind.config.js` is required for the
default token set.

```css
@import 'tailwindcss';
```

### Typed Fetch Client (`src/lib/api.ts`)

```ts
import type { Todo, TodoCreate, TodoUpdate } from './types';

const BASE = '/api';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export const api = {
  listTodos: () => request<Todo[]>('/todos'),
  createTodo: (payload: TodoCreate) =>
    request<Todo>('/todos', { method: 'POST', body: JSON.stringify(payload) }),
  updateTodo: (id: number, payload: TodoUpdate) =>
    request<Todo>(`/todos/${id}`, { method: 'PUT', body: JSON.stringify(payload) }),
  deleteTodo: (id: number) => request<void>(`/todos/${id}`, { method: 'DELETE' })
};
```

### Reactive State (Svelte 5 runes)

The main page uses runes for reactive state and derived values:

```svelte
<script lang="ts">
  import { api } from '$lib/api';

  let todos = $state<Todo[]>([]);
  let filter = $state<'all' | 'active' | 'completed'>('all');

  const visibleTodos = $derived.by(() => {
    if (filter === 'active') return todos.filter((t) => !t.completed);
    if (filter === 'completed') return todos.filter((t) => t.completed);
    return todos;
  });

  $effect(() => {
    api.listTodos().then((list) => (todos = list));
  });
</script>
```

---

## CI/CD

### Lint Workflow

The project runs linting on every push and PR to `develop` and `main`:

```yaml
# .github/workflows/lint.yml
name: Lint

on:
  push:
    branches: [develop, main]
  pull_request:
    branches: [develop, main]

jobs:
  markdownlint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: oven-sh/setup-bun@v2
      - run: bun install --frozen-lockfile
      - run: bun run lint:md

  yamllint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - run: uvx yamllint .
```

### Future Workflows

- **Frontend type-check** - `bun run check` on PR
- **Frontend build** - `bun run build` on PR
- **Python lint** - Ruff on PR
- **Integration tests** - End-to-end via Playwright

---

## Git Hooks

### Pre-commit Hook

Husky runs lint-staged automatically on commit:

```json
{
  "lint-staged": {
    "*.md": "markdownlint --fix",
    "*.{yml,yaml}": "yamllint"
  }
}
```

### Commit-msg Hook

Commitlint validates commit messages (Gitmoji or Conventional format).

### Setup

```bash
bun install  # Runs "husky" automatically via prepare script
```

---

## Development Workflow

### Feature Development

```bash
git checkout main
git pull origin main
git checkout -b feature/description

# API
cd api
uv sync                            # creates .venv and installs dependencies
uv run uvicorn main:app --reload

# Frontend (in another terminal)
cd web
bun run dev

# Lint and commit
bun run lint
bun run commit
git push origin feature/description
```

### Pre-commit Checklist

- [ ] `bun run lint` passes
- [ ] `cd web && bun run check` passes
- [ ] `cd web && bun run build` succeeds
- [ ] API endpoints respond correctly (`curl http://localhost:8000/todos`)
- [ ] Web UI loads and functions at <http://localhost:5173>
- [ ] Documentation updated if needed
- [ ] No sensitive data committed

---

*Last updated: 2026-04-29*
