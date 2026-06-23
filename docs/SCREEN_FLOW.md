# Screen Flow

SvelteKit web application screen flow and navigation.

## Overview

The app is a single-page experience: one route (`/`) holds the task list, the create form,
filter tabs, and inline edit forms.

```text
┌──────────────────────────────────────────────┐
│  To-Do (single page)                         │
│                                              │
│  ┌──────────────────────────────────────┐    │
│  │  Add task form (title + description) │    │
│  └──────────────────────────────────────┘    │
│  ┌──────────────────────┬─────────────────┐  │
│  │ Filter tabs          │ Stats           │  │
│  │ [All|Active|Done]    │ total / active  │  │
│  └──────────────────────┴─────────────────┘  │
│  ┌──────────────────────────────────────┐    │
│  │ TodoItem rows (toggle / edit / del)  │    │
│  └──────────────────────────────────────┘    │
└──────────────────────────────────────────────┘
```

---

## Sections

### Add Task Form

- **Purpose**: Create a new task
- **Components**:
  - Title input (required, max 200 chars)
  - Description textarea (optional, max 500 chars)
  - Add button (disabled while submitting or empty title)
- **Behavior**: Optimistic prepend to the list on success; form clears

### Filter Tabs

- **Purpose**: Filter the list by status
- **Options**: All / Active / Completed
- **Behavior**: Re-renders the visible list via a `$derived` selector — no network call

### Stats

- **Purpose**: Show total / active / completed counts
- **Behavior**: Derived from `todos` (`$derived`), updates instantly on any mutation

### Task Row (`TodoItem`)

- **Purpose**: Display and mutate a single task
- **Components**:
  - Checkbox (toggle completed)
  - Title (strikethrough when completed)
  - Description (optional, secondary text)
  - Edit button (reveals inline edit form)
  - Delete button
- **Inline edit form**: Title input, description textarea, Save / Cancel buttons

---

## User Flows

### Flow 1: Add a Task

1. User types a title (and optionally a description) in the Add form
2. User submits the form
3. Frontend calls `POST /api/todos`
4. On success, the new task is prepended to the list and the form clears
5. On error, an inline alert is displayed and the form keeps its values

### Flow 2: Toggle a Task

1. User clicks the checkbox on a task row
2. UI updates optimistically (strikethrough applied/removed instantly)
3. Frontend calls `PUT /api/todos/{id}` with `{ completed }`
4. On error, the optimistic change is rolled back and an alert is shown

### Flow 3: Edit a Task

1. User clicks the edit button on a task
2. The row swaps to an inline form pre-filled with the current values
3. User edits and clicks Save
4. Frontend calls `PUT /api/todos/{id}` with the patch
5. On success, the row returns to read mode with updated values
6. Cancel discards changes without an API call

### Flow 4: Delete a Task

1. User clicks the delete button on a task
2. UI removes the row immediately (optimistic)
3. Frontend calls `DELETE /api/todos/{id}`
4. On error, the row is restored and an alert is shown

### Flow 5: Filter Tasks

1. User clicks one of the filter tabs (All / Active / Completed)
2. The visible list updates instantly via the `$derived` selector
3. Stats remain unchanged (always derived from the full list)

---

## API Communication Flow

```text
User action → SvelteKit UI → fetch /api/* → Vite proxy → FastAPI → SQLAlchemy → Database
                                  ↓
Database → SQLAlchemy → FastAPI → fetch response → SvelteKit state update → re-render
```

| User Action | HTTP Method | Endpoint | UI Update |
|-------------|-------------|----------|-----------|
| View tasks | GET | `/todos` | Render task list |
| Add task | POST | `/todos` | Prepend to list |
| Edit task | PUT | `/todos/{id}` | Update row |
| Delete task | DELETE | `/todos/{id}` | Remove row |
| Toggle status | PUT | `/todos/{id}` | Toggle checkbox |

---

*Last updated: 2026-04-29*
