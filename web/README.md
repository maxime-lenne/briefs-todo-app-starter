# web

SvelteKit + Tailwind CSS v4 frontend for the To-Do API.

## Develop

```bash
bun install
bun run dev
```

The dev server runs on <http://localhost:5173>. Vite proxies `/api/*` to
`http://localhost:8000` (configured in `vite.config.ts`), so the FastAPI service
must be running on that port.

## Build

```bash
bun run build
bun run preview
```

## Type-check

```bash
bun run check
```

## Stack

- SvelteKit 2 (Svelte 5 runes)
- Tailwind CSS v4 via the `@tailwindcss/vite` plugin
- TypeScript
- `adapter-auto` for deployment (swap to `adapter-static` for a pure SPA build)
