<script lang="ts">
  import { api } from '$lib/api';
  import TodoItem from '$lib/components/TodoItem.svelte';
  import type { Filter, Todo, TodoUpdate } from '$lib/types';

  let todos = $state<Todo[]>([]);
  let loading = $state(true);
  let error = $state<string | null>(null);
  let filter = $state<Filter>('all');

  let newTitle = $state('');
  let newDescription = $state('');
  let creating = $state(false);

  const total = $derived(todos.length);
  const completedCount = $derived(todos.filter((t) => t.completed).length);
  const activeCount = $derived(total - completedCount);

  const visibleTodos = $derived.by(() => {
    if (filter === 'active') return todos.filter((t) => !t.completed);
    if (filter === 'completed') return todos.filter((t) => t.completed);
    return todos;
  });

  async function loadTodos() {
    loading = true;
    error = null;
    try {
      todos = await api.listTodos();
    } catch (e) {
      error = e instanceof Error ? e.message : 'Failed to load tasks.';
    } finally {
      loading = false;
    }
  }

  async function createTodo(e: Event) {
    e.preventDefault();
    const title = newTitle.trim();
    if (!title || creating) return;
    creating = true;
    try {
      const created = await api.createTodo({
        title,
        description: newDescription.trim() || null,
      });
      todos = [created, ...todos];
      newTitle = '';
      newDescription = '';
    } catch (e) {
      error = e instanceof Error ? e.message : 'Failed to create task.';
    } finally {
      creating = false;
    }
  }

  async function toggleTodo(id: number, completed: boolean) {
    const previous = todos;
    todos = todos.map((t) => (t.id === id ? { ...t, completed } : t));
    try {
      await api.updateTodo(id, { completed });
    } catch (e) {
      todos = previous;
      error = e instanceof Error ? e.message : 'Failed to update task.';
    }
  }

  async function saveTodo(id: number, patch: TodoUpdate) {
    try {
      const updated = await api.updateTodo(id, patch);
      todos = todos.map((t) => (t.id === id ? updated : t));
    } catch (e) {
      error = e instanceof Error ? e.message : 'Failed to update task.';
    }
  }

  async function deleteTodo(id: number) {
    const previous = todos;
    todos = todos.filter((t) => t.id !== id);
    try {
      await api.deleteTodo(id);
    } catch (e) {
      todos = previous;
      error = e instanceof Error ? e.message : 'Failed to delete task.';
    }
  }

  $effect(() => {
    loadTodos();
  });
</script>

<svelte:head>
  <title>To-Do</title>
</svelte:head>

<main class="mx-auto max-w-2xl px-4 py-10 sm:py-16">
  <header class="mb-8">
    <h1 class="text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">To-Do</h1>
    <p class="mt-2 text-sm text-slate-600">A small task manager backed by a FastAPI service.</p>
  </header>

  <section class="mb-6 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
    <form onsubmit={createTodo} class="space-y-3">
      <input
        type="text"
        bind:value={newTitle}
        placeholder="What needs to be done?"
        required
        maxlength="200"
        class="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sm placeholder:text-slate-400 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500 focus:outline-none"
      />
      <textarea
        bind:value={newDescription}
        rows="2"
        maxlength="500"
        placeholder="Description (optional)"
        class="w-full rounded-lg border border-slate-300 px-4 py-2 text-sm placeholder:text-slate-400 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500 focus:outline-none"
      ></textarea>
      <div class="flex justify-end">
        <button
          type="submit"
          disabled={creating || !newTitle.trim()}
          class="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:bg-slate-300"
        >
          {creating ? 'Adding…' : 'Add task'}
        </button>
      </div>
    </form>
  </section>

  <section class="mb-4 flex flex-wrap items-center justify-between gap-3">
    <div class="flex gap-1 rounded-lg bg-slate-200/60 p-1 text-sm">
      {#each ['all', 'active', 'completed'] as const as f}
        <button
          type="button"
          onclick={() => (filter = f)}
          class="rounded-md px-3 py-1.5 font-medium capitalize transition"
          class:bg-white={filter === f}
          class:text-indigo-700={filter === f}
          class:shadow-sm={filter === f}
          class:text-slate-600={filter !== f}
        >
          {f}
        </button>
      {/each}
    </div>
    <div class="flex gap-4 text-xs text-slate-500">
      <span><strong class="text-slate-900">{total}</strong> total</span>
      <span><strong class="text-slate-900">{activeCount}</strong> active</span>
      <span><strong class="text-slate-900">{completedCount}</strong> done</span>
    </div>
  </section>

  {#if error}
    <div
      role="alert"
      class="mb-4 flex items-start justify-between gap-3 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800"
    >
      <span>{error}</span>
      <button
        type="button"
        onclick={() => (error = null)}
        class="text-red-600 hover:text-red-800"
        aria-label="Dismiss error"
      >
        ✕
      </button>
    </div>
  {/if}

  {#if loading}
    <p class="text-center text-sm text-slate-500">Loading tasks…</p>
  {:else if visibleTodos.length === 0}
    <div class="rounded-2xl border border-dashed border-slate-300 bg-white p-10 text-center">
      <p class="text-sm text-slate-500">
        {#if total === 0}
          No tasks yet. Add one above to get started.
        {:else}
          No {filter} tasks.
        {/if}
      </p>
    </div>
  {:else}
    <ul class="space-y-2">
      {#each visibleTodos as todo (todo.id)}
        <TodoItem {todo} onToggle={toggleTodo} onSave={saveTodo} onDelete={deleteTodo} />
      {/each}
    </ul>
  {/if}
</main>
