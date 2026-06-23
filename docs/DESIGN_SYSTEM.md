# Design System

UI/UX design system for the SvelteKit + Tailwind CSS v4 To-Do application.

## Design Principles

- **Simplicity** - Clean, minimal interface focused on task management
- **Clarity** - Clear visual hierarchy and task status indicators
- **Responsiveness** - Mobile-first layout, max-width container on desktop
- **Accessibility** - Semantic HTML, ARIA labels, sufficient contrast, keyboard support

---

## Tailwind v4 Setup

Tailwind v4 is loaded directly from CSS with no JS config file. The whole entrypoint is:

```css
/* src/app.css */
@import 'tailwindcss';
```

The `@tailwindcss/vite` plugin in `vite.config.ts` handles scanning Svelte files for class usage.
Custom tokens, when needed, can be declared with the v4 `@theme` block:

```css
@theme {
  --color-brand-500: oklch(0.6 0.2 270);
  --font-display: 'Inter Variable', sans-serif;
}
```

---

## Color Palette

The default palette is Tailwind's slate / indigo / red scales — applied through utility classes,
not custom tokens. The values below describe their intended role.

| Role | Tailwind class | Usage |
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

---

## Layout

### Page Structure

```text
┌──────────────────────────────────────────────┐
│  Header                                      │
│   Title: "To-Do"                             │
│   Subtitle: brief description                │
├──────────────────────────────────────────────┤
│  Add task card                               │
│   [Title input]                              │
│   [Description textarea]                     │
│   [Add button]                               │
├──────────────────────────────────────────────┤
│  Filter tabs    │   Stats (total/active/done)│
├──────────────────────────────────────────────┤
│  ┌─ TodoItem ────────────────────────────┐   │
│  │ [☐] Title                  ✏️  🗑️   │   │
│  │     Description                       │   │
│  └───────────────────────────────────────┘   │
│  ┌─ TodoItem ────────────────────────────┐   │
│  │ [☑] ~~Done task~~          ✏️  🗑️   │   │
│  └───────────────────────────────────────┘   │
└──────────────────────────────────────────────┘
```

### Container

```svelte
<main class="mx-auto max-w-2xl px-4 py-10 sm:py-16">…</main>
```

- Max width: `max-w-2xl` (≈ 672px)
- Horizontal padding: `px-4`
- Vertical padding: `py-10` mobile, `py-16` from `sm:` breakpoint

### Spacing

- Card padding: `p-4` to `p-5`
- Vertical spacing between sections: `mb-6` to `mb-8`
- Vertical spacing between list items: `space-y-2`

---

## Components

### Card / Surface

```html
<section class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">…</section>
```

### Primary Button

```html
<button
  class="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm
         transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:bg-slate-300"
>
  Add task
</button>
```

### Secondary Button

```html
<button
  class="rounded-md border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-700
         hover:bg-slate-50"
>
  Cancel
</button>
```

### Text Input / Textarea

```html
<input
  class="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sm placeholder:text-slate-400
         focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500 focus:outline-none"
/>
```

### Checkbox (task toggle)

```html
<input
  type="checkbox"
  class="h-5 w-5 cursor-pointer rounded border-slate-300 text-indigo-600
         focus:ring-2 focus:ring-indigo-500"
/>
```

### Filter tab group

```html
<div class="flex gap-1 rounded-lg bg-slate-200/60 p-1 text-sm">
  <button class="rounded-md bg-white px-3 py-1.5 font-medium text-indigo-700 shadow-sm">All</button>
  <button class="rounded-md px-3 py-1.5 font-medium text-slate-600">Active</button>
  <button class="rounded-md px-3 py-1.5 font-medium text-slate-600">Completed</button>
</div>
```

### Status Indicators

| Status | Visual |
|--------|--------|
| Active | Normal text, unchecked checkbox |
| Completed | `line-through` + `text-slate-400` on title and description |

---

## Typography

| Element | Tailwind class |
|---------|----------------|
| Page title | `text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl` |
| Section subtitle | `text-sm text-slate-600` |
| Task title | `font-medium text-slate-900` |
| Task description | `text-sm text-slate-600` |
| Stats | `text-xs text-slate-500` (numbers `text-slate-900 font-bold`) |

Default font stack is the Tailwind system stack (`ui-sans-serif`, `system-ui`, …). Override with a
`@theme` block if a custom typeface is required.

---

## Feedback and Notifications

| Event | UI feedback |
|-------|-------------|
| Task created | Optimistic prepend to list, form clears |
| Task updated | Optimistic patch (toggle), rollback on error |
| Task deleted | Optimistic removal, rollback on error |
| API error | Inline alert: `border-red-200 bg-red-50 text-red-800` with dismiss button |
| Empty state | Dashed-border card: `border-dashed border-slate-300` with helper copy |

---

## Accessibility

- All interactive controls have descriptive `aria-label` or visible label text
- Focus styles via Tailwind's `focus:ring-*` utilities
- Color is never the sole status indicator (checkbox + strikethrough used together)
- Buttons use semantic `<button type="button|submit">`
- `role="alert"` on the error banner for screen readers

---

*Last updated: 2026-04-29*
