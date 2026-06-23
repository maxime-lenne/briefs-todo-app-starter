# To-Do App

<!-- markdownlint-disable -->
<p align="center">
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/fastapi/fastapi-original.svg" alt="FastAPI" width="80" height="80" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/svelte/svelte-original.svg" alt="Svelte" width="80" height="80" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/tailwindcss/tailwindcss-original.svg" alt="Tailwind CSS" width="80" height="80" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/sqlite/sqlite-original.svg" alt="SQLite" width="80" height="80" />
</p>

<p align="center">
  <strong>To-Do application with FastAPI, SvelteKit, and Tailwind CSS v4</strong>
</p>

<p align="center">
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT" />
  </a>
  <a href="https://gitmoji.dev">
    <img src="https://img.shields.io/badge/gitmoji-%20😜%20😍-FFDD67.svg" alt="Gitmoji" />
  </a>
</p>
<!-- markdownlint-restore -->

---

A simple To-Do application with a **FastAPI** REST API backed by **SQLAlchemy** and a **SvelteKit**
single-page frontend styled with **Tailwind CSS v4**.

## Architecture

```text
┌────────────────────┐        ┌─────────────────────┐        ┌────────────┐
│  SvelteKit (Vite)  │  ───▶  │   FastAPI (uvicorn) │  ───▶  │  Database  │
│   localhost:5173   │        │    localhost:8000   │        │  (SQLite)  │
└────────────────────┘        └─────────────────────┘        └────────────┘
       (browser)              (proxied via /api in dev)        (todo.db)
```

The Vite dev server proxies `/api/*` to the FastAPI service, so the API needs no CORS configuration
during development.

## Tech Stack

| Layer    | Technology                          |
|----------|-------------------------------------|
| API      | FastAPI + Uvicorn                   |
| ORM / DB | SQLAlchemy 2 + SQLite (Postgres OK) |
| Frontend | SvelteKit 2 (Svelte 5 runes)        |
| Styling  | Tailwind CSS v4                     |
| Bundler  | Vite                                |

## Prerequisites

- Python >= 3.10
- Node.js >= 20 (or compatible runtime)

## Quick Start

### 1. Run the API

```bash
cd api
uv sync
uv run uvicorn main:app --reload
```

The API listens on `http://localhost:8000`. By default it uses SQLite (`api/todo.db`); set
`DATABASE_URL` to point at Postgres if you prefer (see `api/.env.example`).

### 2. Run the web app

In a second terminal:

```bash
cd web
npm install
npm run dev
```

Open <http://localhost:5173>. The Vite proxy forwards `/api/*` to the API.

## API Endpoints

| Method   | Endpoint      | Description      |
|----------|---------------|------------------|
| `GET`    | `/todos`      | List all tasks   |
| `GET`    | `/todos/{id}` | Get a task by ID |
| `POST`   | `/todos`      | Create a task    |
| `PUT`    | `/todos/{id}` | Update a task    |
| `DELETE` | `/todos/{id}` | Delete a task    |

Interactive docs: <http://localhost:8000/docs> · <http://localhost:8000/redoc>

## Project Structure

```text
.
├── api/                  # FastAPI service
│   ├── main.py           # Entry point and routes
│   ├── database.py       # Engine and session
│   ├── models.py         # SQLAlchemy ORM models
│   ├── schemas.py        # Pydantic schemas
│   ├── crud.py           # CRUD helpers
│   ├── pyproject.toml     # Python deps (managed with uv)
│   ├── uv.lock
│   └── .env.example      # API runtime env (DATABASE_URL)
├── web/                  # SvelteKit + Tailwind v4 frontend
│   ├── src/
│   │   ├── lib/
│   │   │   ├── api.ts            # Typed fetch client
│   │   │   ├── types.ts
│   │   │   └── components/
│   │   │       └── TodoItem.svelte
│   │   └── routes/
│   │       ├── +layout.svelte
│   │       └── +page.svelte
│   ├── svelte.config.js
│   ├── vite.config.ts            # Includes /api → :8000 proxy
│   ├── package.json
│   └── .env.example              # Web public env (PUBLIC_API_BASE override)
└── README.md
```

## Development

```bash
bun install                   # Repo-level lint tooling
bun run lint                  # Lint markdown and yaml
bun run commit                # Interactive gitmoji commit

# Frontend
cd web && npm run check       # Svelte / TypeScript checks
cd web && npm run build       # Production build
```

## License

MIT — see [LICENSE](LICENSE).

## Author

**Maxime Lenne** — [maxime-lenne.fr](https://maxime-lenne.fr)
