<script lang="ts">
  import type { Todo, TodoUpdate } from '$lib/types';

  interface Props {
    todo: Todo;
    onToggle: (id: number, completed: boolean) => void | Promise<void>;
    onSave: (id: number, patch: TodoUpdate) => void | Promise<void>;
    onDelete: (id: number) => void | Promise<void>;
  }

  let { todo, onToggle, onSave, onDelete }: Props = $props();

  let editing = $state(false);
  let titleDraft = $state('');
  let descriptionDraft = $state('');

  function startEdit() {
    titleDraft = todo.title;
    descriptionDraft = todo.description ?? '';
    editing = true;
  }

  function cancelEdit() {
    editing = false;
  }

  async function save() {
    const trimmedTitle = titleDraft.trim();
    if (!trimmedTitle) return;
    await onSave(todo.id, {
      title: trimmedTitle,
      description: descriptionDraft.trim() || null,
    });
    editing = false;
  }
</script>

<li
  class="group flex items-start gap-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm transition hover:shadow-md"
>
  <input
    type="checkbox"
    checked={todo.completed}
    onchange={(e) => onToggle(todo.id, e.currentTarget.checked)}
    class="mt-1 h-5 w-5 shrink-0 cursor-pointer rounded border-slate-300 text-indigo-600 focus:ring-2 focus:ring-indigo-500"
    aria-label={`Mark ${todo.title} as ${todo.completed ? 'active' : 'completed'}`}
  />

  <div class="min-w-0 flex-1">
    {#if editing}
      <form
        onsubmit={(e) => {
          e.preventDefault();
          save();
        }}
        class="space-y-2"
      >
        <input
          type="text"
          bind:value={titleDraft}
          class="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500 focus:outline-none"
          placeholder="Title"
          required
        />
        <textarea
          bind:value={descriptionDraft}
          rows="2"
          class="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500 focus:outline-none"
          placeholder="Description (optional)"
        ></textarea>
        <div class="flex gap-2">
          <button
            type="submit"
            class="rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-indigo-700"
          >
            Save
          </button>
          <button
            type="button"
            onclick={cancelEdit}
            class="rounded-md border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50"
          >
            Cancel
          </button>
        </div>
      </form>
    {:else}
      <p
        class="font-medium text-slate-900 break-words"
        class:line-through={todo.completed}
        class:text-slate-400={todo.completed}
      >
        {todo.title}
      </p>
      {#if todo.description}
        <p class="mt-1 text-sm text-slate-600 break-words" class:text-slate-400={todo.completed}>
          {todo.description}
        </p>
      {/if}
    {/if}
  </div>

  {#if !editing}
    <div class="flex gap-1 opacity-0 transition group-hover:opacity-100">
      <button
        type="button"
        onclick={startEdit}
        class="rounded-md p-2 text-slate-500 hover:bg-slate-100 hover:text-slate-700"
        aria-label="Edit task"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-4 w-4"
          viewBox="0 0 20 20"
          fill="currentColor"
        >
          <path d="M17.414 2.586a2 2 0 00-2.828 0L7 10.172V13h2.828l7.586-7.586a2 2 0 000-2.828z" />
          <path
            fill-rule="evenodd"
            d="M2 6a2 2 0 012-2h4a1 1 0 010 2H4v10h10v-4a1 1 0 112 0v4a2 2 0 01-2 2H4a2 2 0 01-2-2V6z"
            clip-rule="evenodd"
          />
        </svg>
      </button>
      <button
        type="button"
        onclick={() => onDelete(todo.id)}
        class="rounded-md p-2 text-slate-500 hover:bg-red-50 hover:text-red-600"
        aria-label="Delete task"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-4 w-4"
          viewBox="0 0 20 20"
          fill="currentColor"
        >
          <path
            fill-rule="evenodd"
            d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z"
            clip-rule="evenodd"
          />
        </svg>
      </button>
    </div>
  {/if}
</li>
