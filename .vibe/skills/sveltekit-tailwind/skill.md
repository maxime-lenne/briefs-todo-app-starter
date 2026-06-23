# SvelteKit + Tailwind CSS v4 Skill

## Project Structure
```
web/
├── src/
│   ├── app.html          # HTML shell
│   ├── app.css           # Tailwind entry (@import 'tailwindcss')
│   ├── app.d.ts          # Type augmentation
│   ├── lib/
│   │   ├── api.ts        # Typed fetch client
│   │   ├── types.ts      # TypeScript types
│   │   └── components/
│   │       └── TodoItem.svelte
│   └── routes/
│       ├── +layout.svelte  # Root layout
│       └── +page.svelte    # Main page
├── svelte.config.js
├── vite.config.ts        # Includes /api proxy
├── package.json
└── tsconfig.json
```

## Tailwind v4 Setup

### CSS Entry Point
```css
/* src/app.css */
@import 'tailwindcss';

/* Optional: Custom tokens */
@theme {
  --color-brand-500: oklch(0.6 0.2 270);
  --font-display: 'Inter Variable', sans-serif;
}
```

### Vite Configuration
```typescript
// vite.config.ts
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

## Svelte 5 Runes Patterns

### Basic State Management
```svelte
<script lang="ts">
  import { api } from '$lib/api';
  import type { Todo } from '$lib/types';

  // Reactive state - triggers reactivity on assignment
  let todos = $state<Todo[]>([]);
  let loading = $state(false);
  let error = $state<string | null>(null);
  let filter = $state<'all' | 'active' | 'completed'>('all');

  // Derived state - automatically updates when dependencies change
  const visibleTodos = $derived.by(() => {
    if (filter === 'active') return todos.filter(t => !t.completed);
    if (filter === 'completed') return todos.filter(t => t.completed);
    return todos;
  });

  // Another derived example
  const stats = $derived({
    total: todos.length,
    active: todos.filter(t => !t.completed).length,
    completed: todos.filter(t => t.completed).length
  });

  // Side effects - run when dependencies change
  $effect(() => {
    loading = true;
    api.listTodos()
      .then((data) => todos = data)
      .catch((e) => error = e.message)
      .finally(() => loading = false);
  });

  // Effect that runs once on mount
  $effect(() => {
    console.log('Component mounted');
    return () => console.log('Component unmounted');
  });
</script>
```

### Props with $props
```svelte
<script lang="ts">
  import type { Todo, TodoUpdate } from '$lib/types';

  interface Props {
    todo: Todo;
    onToggle: (id: number, completed: boolean) => void | Promise<void>;
    onSave: (id: number, patch: TodoUpdate) => void | Promise<void>;
    onDelete: (id: number) => void | Promise<void>;
  }

  // Destructure props
  let { todo, onToggle, onSave, onDelete }: Props = $props();

  // Or access directly
  let props = $props();
  // props.todo, props.onToggle, etc.
</script>
```

## Typed Fetch Client

### Complete Implementation
```typescript
// src/lib/api.ts
import type { Todo, TodoCreate, TodoUpdate } from './types';

const BASE = '/api';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init
  });
  
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(
      `${res.status} ${res.statusText}${errorData.detail ? `: ${errorData.detail}` : ''}`
    );
  }
  
  // Handle 204 No Content
  if (res.status === 204) return undefined as T;
  
  return res.json() as Promise<T>;
}

// Typed API client
export const api = {
  // GET /todos
  listTodos: () => request<Todo[]>('/todos'),
  
  // GET /todos/{id}
  getTodo: (id: number) => request<Todo>(`/todos/${id}`),
  
  // POST /todos
  createTodo: (payload: TodoCreate) =>
    request<Todo>('/todos', { 
      method: 'POST', 
      body: JSON.stringify(payload) 
    }),
  
  // PUT /todos/{id}
  updateTodo: (id: number, payload: TodoUpdate) =>
    request<Todo>(`/todos/${id}`, { 
      method: 'PUT', 
      body: JSON.stringify(payload) 
    }),
  
  // DELETE /todos/{id}
  deleteTodo: (id: number) => 
    request<void>(`/todos/${id}`, { method: 'DELETE' })
};
```

### Usage Example
```svelte
<script lang="ts">
  import { api } from '$lib/api';
  import type { TodoCreate } from '$lib/types';

  let todos = $state<Todo[]>([]);
  let newTitle = $state('');

  $effect(() => {
    api.listTodos().then(data => todos = data);
  });

  async function addTodo() {
    if (!newTitle.trim()) return;
    
    const newTodo: TodoCreate = {
      title: newTitle.trim(),
      description: '',
      completed: false
    };
    
    const created = await api.createTodo(newTodo);
    todos = [created, ...todos];
    newTitle = '';
  }
</script>

<input bind:value={newTitle} placeholder="What needs to be done?" />
<button onclick={addTodo}>Add</button>
```

## TypeScript Types

### Core Types
```typescript
// src/lib/types.ts

export interface Todo {
  id: number;
  title: string;
  description: string | null;
  completed: boolean;
  created_at: string;
  updated_at: string | null;
}

export interface TodoCreate {
  title: string;
  description?: string | null;
  completed?: boolean;
}

export interface TodoUpdate {
  title?: string;
  description?: string | null;
  completed?: boolean;
}

export type Filter = 'all' | 'active' | 'completed';

// For API responses
export interface ApiError {
  detail: string;
}
```

## Component Patterns

### TodoItem Component (Complete Example)
```svelte
<!-- src/lib/components/TodoItem.svelte -->
<script lang="ts">
  import type { Todo, TodoUpdate } from '$lib/types';

  interface Props {
    todo: Todo;
    onToggle: (id: number, completed: boolean) => void | Promise<void>;
    onSave: (id: number, patch: TodoUpdate) => void | Promise<void>;
    onDelete: (id: number) => void | Promise<void>;
  }

  let { todo, onToggle, onSave, onDelete }: Props = $props();
  
  // Edit state
  let editing = $state(false);
  let titleDraft = $state('');
  let descriptionDraft = $state('');
  let saving = $state(false);

  function startEdit() {
    titleDraft = todo.title;
    descriptionDraft = todo.description ?? '';
    editing = true;
  }

  async function saveEdit() {
    if (!titleDraft.trim()) return;
    
    saving = true;
    try {
      await onSave(todo.id, {
        title: titleDraft.trim(),
        description: descriptionDraft.trim() || null
      });
      editing = false;
    } finally {
      saving = false;
    }
  }

  function cancelEdit() {
    editing = false;
  }
</script>

<li class="border border-slate-200 rounded-lg p-4 space-y-3">
  {#if editing}
    <!-- Edit Form -->
    <div class="space-y-2">
      <input
        bind:value={titleDraft}
        class="w-full rounded-lg border border-slate-300 px-4 py-2 text-sm
                   focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500 focus:outline-none"
        placeholder="Title"
        required
      />
      <textarea
        bind:value={descriptionDraft}
        class="w-full rounded-lg border border-slate-300 px-4 py-2 text-sm
                   placeholder:text-slate-400 focus:border-indigo-500 focus:ring-2
                   focus:ring-indigo-500 focus:outline-none resize-none"
        placeholder="Description (optional)"
        rows="2"
      />
      <div class="flex gap-2">
        <button
          onclick={saveEdit}
          disabled={saving || !titleDraft.trim()}
          class="rounded-lg bg-indigo-600 px-3 py-1.5 text-sm font-medium text-white
                     disabled:cursor-not-allowed disabled:bg-slate-300
                     hover:bg-indigo-700 transition"
        >
          {saving ? 'Saving...' : 'Save'}
        </button>
        <button
          onclick={cancelEdit}
          disabled={saving}
          class="rounded-md border border-slate-300 px-3 py-1.5 text-sm font-medium
                     text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed"
        >
          Cancel
        </button>
      </div>
    </div>
  {:else}
    <!-- Read Mode -->
    <div class="flex items-start gap-3">
      <input
        type="checkbox"
        checked={todo.completed}
        onchange={() => onToggle(todo.id, !todo.completed)}
        class="mt-1 h-5 w-5 cursor-pointer rounded border-slate-300 text-indigo-600
                   focus:ring-2 focus:ring-indigo-500"
        aria-label={`Toggle completion for ${todo.title}`}
      />
      
      <div class="flex-1 min-w-0">
        <h3 class={`font-medium ${todo.completed ? 'line-through text-slate-400' : 'text-slate-900'}`}>
          {todo.title}
        </h3>
        {#if todo.description}
          <p class="text-sm text-slate-600">{todo.description}</p>
        {/if}
      </div>
      
      <div class="flex gap-1">
        <button
          onclick={startEdit}
          class="text-slate-500 hover:text-indigo-600 transition"
          aria-label={`Edit ${todo.title}`}
        >
          ✏️
        </button>
        <button
          onclick={() => onDelete(todo.id)}
          class="text-slate-500 hover:text-red-600 transition"
          aria-label={`Delete ${todo.title}`}
        >
          🗑️
        </button>
      </div>
    </div>
  {/if}
</li>
```

### Main Page Component
```svelte
<!-- src/routes/+page.svelte -->
<script lang="ts">
  import { api } from '$lib/api';
  import TodoItem from '$lib/components/TodoItem.svelte';
  import type { Filter, Todo, TodoCreate } from '$lib/types';

  let todos = $state<Todo[]>([]);
  let filter = $state<Filter>('all');
  let newTitle = $state('');
  let newDescription = $state('');
  let loading = $state(false);
  let error = $state<string | null>(null);

  // Derived: filtered todos
  const visibleTodos = $derived.by(() => {
    if (filter === 'active') return todos.filter(t => !t.completed);
    if (filter === 'completed') return todos.filter(t => t.completed);
    return todos;
  });

  // Derived: statistics
  const stats = $derived({
    total: todos.length,
    active: todos.filter(t => !t.completed).length,
    completed: todos.filter(t => t.completed).length
  });

  // Load todos on mount
  $effect(() => {
    loadTodos();
  });

  async function loadTodos() {
    loading = true;
    error = null;
    try {
      todos = await api.listTodos();
    } catch (e) {
      error = e instanceof Error ? e.message : 'Failed to load todos';
    } finally {
      loading = false;
    }
  }

  async function createTodo(e: Event) {
    e.preventDefault();
    const title = newTitle.trim();
    if (!title) return;

    const newTodo: TodoCreate = {
      title,
      description: newDescription.trim() || null
    };

    try {
      const created = await api.createTodo(newTodo);
      todos = [created, ...todos];
      newTitle = '';
      newDescription = '';
    } catch (e) {
      error = e instanceof Error ? e.message : 'Failed to create todo';
    }
  }

  async function toggleTodo(id: number, completed: boolean) {
    // Optimistic update
    todos = todos.map(t => t.id === id ? { ...t, completed } : t);
    
    try {
      await api.updateTodo(id, { completed });
    } catch (e) {
      // Rollback on error
      await loadTodos();
      error = e instanceof Error ? e.message : 'Failed to update todo';
    }
  }

  async function updateTodo(id: number, patch: TodoCreate) {
    try {
      await api.updateTodo(id, patch);
    } catch (e) {
      error = e instanceof Error ? e.message : 'Failed to update todo';
      throw e;
    }
  }

  async function deleteTodo(id: number) {
    // Optimistic update
    todos = todos.filter(t => t.id !== id);
    
    try {
      await api.deleteTodo(id);
    } catch (e) {
      // Rollback on error
      await loadTodos();
      error = e instanceof Error ? e.message : 'Failed to delete todo';
    }
  }

  function setFilter(newFilter: Filter) {
    filter = newFilter;
  }
</script>

<svelte:head>
  <title>To-Do App</title>
</svelte:head>

<div class="mx-auto max-w-2xl px-4 py-10 sm:py-16">
  <header class="mb-8 text-center">
    <h1 class="text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
      To-Do
    </h1>
    <p class="mt-2 text-sm text-slate-600">
      A simple task management application
    </p>
  </header>

  <!-- Error Banner -->
  {#if error}
    <div class="mb-6 rounded-lg border border-red-200 bg-red-50 p-4 text-red-800" role="alert">
      <p>{error}</p>
      <button onclick={() => error = null} class="mt-2 text-sm underline">
        Dismiss
      </button>
    </div>
  {/if}

  <!-- Add Todo Form -->
  <section class="mb-6 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
    <h2 class="mb-4 text-lg font-medium text-slate-900">Add Task</h2>
    <form onsubmit={createTodo} class="space-y-3">
      <div>
        <label for="title" class="block text-sm font-medium text-slate-700">
          Title *
        </label>
        <input
          id="title"
          type="text"
          bind:value={newTitle}
          required
          minlength="1"
          maxlength="200"
          class="mt-1 block w-full rounded-lg border border-slate-300 px-4 py-2 text-sm
                 placeholder:text-slate-400 focus:border-indigo-500 focus:ring-2
                 focus:ring-indigo-500 focus:outline-none"
          placeholder="What needs to be done?"
        />
      </div>
      <div>
        <label for="description" class="block text-sm font-medium text-slate-700">
          Description
        </label>
        <textarea
          id="description"
          bind:value={newDescription}
          maxlength="500"
          rows="2"
          class="mt-1 block w-full rounded-lg border border-slate-300 px-4 py-2 text-sm
                 placeholder:text-slate-400 focus:border-indigo-500 focus:ring-2
                 focus:ring-indigo-500 focus:outline-none resize-none"
          placeholder="Additional details..."
        />
      </div>
      <button
        type="submit"
        disabled={loading || !newTitle.trim()}
        class="w-full rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white
                   disabled:cursor-not-allowed disabled:bg-slate-300
                   hover:bg-indigo-700 transition"
      >
        {loading ? 'Adding...' : 'Add Task'}
      </button>
    </form>
  </section>

  <!-- Filters and Stats -->
  <div class="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
    <div class="flex gap-1 rounded-lg bg-slate-200/60 p-1 text-sm">
      <button
        onclick={() => setFilter('all')}
        class="rounded-md px-3 py-1.5 font-medium transition
               {filter === 'all' ? 'bg-white text-indigo-700 shadow-sm' : 'text-slate-600 hover:bg-slate-300/50'}"
        aria-pressed={filter === 'all'}
      >
        All
      </button>
      <button
        onclick={() => setFilter('active')}
        class="rounded-md px-3 py-1.5 font-medium transition
               {filter === 'active' ? 'bg-white text-indigo-700 shadow-sm' : 'text-slate-600 hover:bg-slate-300/50'}"
        aria-pressed={filter === 'active'}
      >
        Active
      </button>
      <button
        onclick={() => setFilter('completed')}
        class="rounded-md px-3 py-1.5 font-medium transition
               {filter === 'completed' ? 'bg-white text-indigo-700 shadow-sm' : 'text-slate-600 hover:bg-slate-300/50'}"
        aria-pressed={filter === 'completed'}
      >
        Completed
      </button>
    </div>

    <div class="text-right text-xs text-slate-500">
      <span class="font-bold text-slate-900">{stats.total}</span> total •
      <span class="font-bold text-slate-900">{stats.active}</span> active •
      <span class="font-bold text-slate-900">{stats.completed}</span> completed
    </div>
  </div>

  <!-- Todo List -->
  {#if loading && todos.length === 0}
    <div class="text-center text-slate-500">Loading...</div>
  {:else if visibleTodos.length === 0}
    <div class="rounded-2xl border-2 border-dashed border-slate-300 p-8 text-center">
      <p class="text-slate-500">No tasks found</p>
      {#if filter !== 'all'}
        <p class="mt-2 text-sm text-slate-400">
          Try adjusting your filter
        </p>
      {/if}
    </div>
  {:else}
    <ul class="space-y-2">
      {#each visibleTodos as todo (todo.id)}
        <TodoItem
          {todo}
          onToggle={toggleTodo}
          onSave={updateTodo}
          onDelete={deleteTodo}
        />
      {/each}
    </ul>
  {/if}
</div>
```

## Tailwind v4 Design Patterns

### Color Palette
| Role | Tailwind Class | Usage |
|------|----------------|-------|
| Primary (action) | `bg-indigo-600` / `hover:bg-indigo-700` | Buttons, focus rings |
| Page background | `bg-slate-50` | Main background |
| Surface | `bg-white` | Cards, list rows |
| Border | `border-slate-200` / `border-slate-300` | Cards, inputs |
| Primary text | `text-slate-900` | Titles, body |
| Muted text | `text-slate-600` | Descriptions, helper text |
| Disabled text | `text-slate-400` | Completed task labels |
| Success accent | `text-indigo-700` (active filter) | Active filter pill |
| Danger | `text-red-600` / `bg-red-50` | Delete hover state, errors |

### Component Styles

#### Card / Surface
```html
<section class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
  Content
</section>
```

#### Primary Button
```html
<button class="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white
                shadow-sm transition hover:bg-indigo-700
                disabled:cursor-not-allowed disabled:bg-slate-300">
  Button Text
</button>
```

#### Secondary Button
```html
<button class="rounded-md border border-slate-300 px-3 py-1.5 text-sm font-medium
                text-slate-700 hover:bg-slate-50">
  Button Text
</button>
```

#### Text Input
```html
<input class="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sm
               placeholder:text-slate-400 focus:border-indigo-500 focus:ring-2
               focus:ring-indigo-500 focus:outline-none" />
```

#### Textarea
```html
<textarea class="w-full rounded-lg border border-slate-300 px-4 py-2 text-sm
                  placeholder:text-slate-400 focus:border-indigo-500 focus:ring-2
                  focus:ring-indigo-500 focus:outline-none resize-none" rows="3"></textarea>
```

#### Checkbox
```html
<input type="checkbox" class="h-5 w-5 cursor-pointer rounded border-slate-300
                         text-indigo-600 focus:ring-2 focus:ring-indigo-500" />
```

#### Filter Tabs
```html
<div class="flex gap-1 rounded-lg bg-slate-200/60 p-1 text-sm">
  <button class="rounded-md bg-white px-3 py-1.5 font-medium text-indigo-700 shadow-sm">
    All
  </button>
  <button class="rounded-md px-3 py-1.5 font-medium text-slate-600 hover:bg-slate-300/50">
    Active
  </button>
</div>
```

### Typography
| Element | Tailwind Class |
|---------|----------------|
| Page title | `text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl` |
| Section title | `text-lg font-medium text-slate-900` |
| Section subtitle | `text-sm text-slate-600` |
| Task title | `font-medium text-slate-900` |
| Task description | `text-sm text-slate-600` |
| Stats | `text-xs text-slate-500` (numbers `text-slate-900 font-bold`) |

### Spacing
- **Container**: `mx-auto max-w-2xl px-4 py-10 sm:py-16`
- **Card padding**: `p-5`
- **Vertical spacing**: `mb-4`, `mb-6`, `mb-8`
- **List item spacing**: `space-y-2`
- **Form field spacing**: `space-y-3`

### Layout Patterns

#### Page Layout
```svelte
<!-- src/routes/+layout.svelte -->
<script lang="ts">
  import '../app.css';
</script>

{@render children()}
```

#### Centered Container
```svelte
<div class="mx-auto max-w-2xl px-4 py-10 sm:py-16">
  <!-- Content -->
</div>
```

#### Form Layout
```svelte
<form class="space-y-4">
  <div class="space-y-1">
    <label class="block text-sm font-medium text-slate-700">Label</label>
    <input class="..." />
  </div>
  <button type="submit" class="...">Submit</button>
</form>
```

## Accessibility Best Practices

### Semantic HTML
- Use `<button>` for buttons, not `<div>`
- Use `<form>` for forms
- Use `<nav>` for navigation
- Use `<main>` for main content
- Use `<section>` for content sections

### ARIA Attributes
```svelte
<button aria-label="Delete task" aria-pressed={false}>
  🗑️
</button>

<div role="alert" class="...">
  Error message
</div>

<input 
  type="checkbox" 
  id="task-1"
  aria-labelledby="task-1-label"
/>
<label id="task-1-label">Task title</label>
```

### Keyboard Navigation
- All interactive elements should be focusable
- Use `:focus-visible` for focus styles
- Ensure tab order is logical
- Add keyboard shortcuts where appropriate

### Color Contrast
- Text: Minimum 4.5:1 contrast ratio
- UI Components: Minimum 3:1 contrast ratio
- Use `text-slate-900` on `bg-white` (7.32:1)
- Use `text-white` on `bg-indigo-600` (5.82:1)

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Tailwind classes not applying | Check `vite.config.ts` has `@tailwindcss/vite` |
| Type errors in Svelte | Run `npm run check` (svelte-check + tsc) |
| Proxy not working | Verify `/api` proxy in `vite.config.ts` |
| Reactive updates not triggering | Use `$state` and `$derived` correctly |
| Build fails | Run `npm run build` locally to debug |
| HMR not working | Check Vite server is running, clear cache |
| Styles not updating | Check Tailwind is scanning Svelte files |
| TypeScript errors | Check `tsconfig.json` and type definitions |

## Testing Frontend Code

### vitest Configuration
```typescript
// vite.config.ts
import { defineConfig } from 'vitest/config';

export default defineConfig({
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

### Component Test Example
```typescript
// src/lib/components/TodoItem.test.ts
import { describe, it, expect } from 'vitest';
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
    
    const editButton = screen.getByLabelText('Edit');
    await fireEvent.click(editButton);
    
    expect(screen.getByPlaceholderText('Title')).toBeInTheDocument();
  });
});
```

## Package.json Dependencies
```json
{
  "name": "todo-web",
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite dev",
    "build": "vite build",
    "preview": "vite preview",
    "check": "svelte-check && tsc --noEmit",
    "check:watch": "svelte-check --watch",
    "test": "vitest",
    "test:coverage": "vitest --coverage"
  },
  "dependencies": {
    "@sveltejs/adapter-static": "^3.0.0",
    "svelte": "^5.16.0"
  },
  "devDependencies": {
    "@sveltejs/kit": "^2.15.0",
    "@sveltejs/vite-plugin-svelte": "^4.0.0",
    "@tailwindcss/vite": "^4.0.0",
    "@testing-library/svelte": "^4.0.0",
    "@types/node": "^20.0.0",
    "jsdom": "^24.0.0",
    "svelte-check": "^4.0.0",
    "tailwindcss": "^4.0.0",
    "typescript": "^5.7.0",
    "vite": "^6.0.0",
    "vitest": "^1.0.0"
  }
}
```

## When to Use This Skill
- Creating new SvelteKit pages or components
- Styling components with Tailwind CSS v4
- Managing state with Svelte 5 runes
- Creating typed API clients
- Implementing responsive layouts
- Writing tests for frontend code
- Debugging frontend issues

## Related Skills
- `todo-app` - For project-specific context
- `fastapi-sqlalchemy` - For backend integration
- `docker` - For containerizing the frontend
- `testing` - For comprehensive testing strategies
- `security` - For frontend security best practices
