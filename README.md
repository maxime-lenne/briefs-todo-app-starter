# Docker To-Do App

<!-- markdownlint-disable -->
<p align="center">
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/docker/docker-original.svg" alt="Docker" width="80" height="80" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/fastapi/fastapi-original.svg" alt="FastAPI" width="80" height="80" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/svelte/svelte-original.svg" alt="Svelte" width="80" height="80" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/tailwindcss/tailwindcss-original.svg" alt="Tailwind CSS" width="80" height="80" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/postgresql/postgresql-original.svg" alt="PostgreSQL" width="80" height="80" />
</p>

<p align="center">
  <strong>Dockerized To-Do application with FastAPI, SvelteKit, Tailwind v4, and PostgreSQL</strong>
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

A multi-container To-Do application orchestrated with Docker Compose, featuring a **FastAPI**
REST API, a **SvelteKit + Tailwind v4** frontend served by **nginx**, and a **PostgreSQL**
database.

## Architecture

```text
┌──────────────────────────────────────────────────────────────────┐
│                       Docker Compose                             │
│                                                                  │
│  ┌──────────────┐      ┌──────────────┐      ┌────────────────┐  │
│  │  web (nginx) │ ───▶ │  api (uvic.) │ ───▶ │   db (Postgres)│  │
│  │   :8080      │      │   :8000      │      │     :5432      │  │
│  └──────────────┘      └──────────────┘      └────────────────┘  │
│       ▲                                                ▲         │
│       │                                                │         │
│   (browser)                                     [pgdata volume]  │
└──────────────────────────────────────────────────────────────────┘
        frontend network             backend network
```

The web container serves the prebuilt SvelteKit static bundle and proxies `/api/*` to the
FastAPI service through the internal Docker network — no CORS configuration is needed.

## Tech Stack

| Service  | Technology                       | Description                                |
|----------|----------------------------------|--------------------------------------------|
| api      | FastAPI + Uvicorn                | REST API with CRUD operations              |
| web      | SvelteKit + Tailwind v4 / nginx  | Static SPA + reverse proxy to the API      |
| db       | PostgreSQL 16                    | Persistent data storage                    |
| ORM      | SQLAlchemy 2                     | Database abstraction layer                 |
| Bundler  | Vite                             | Build the SvelteKit app to static assets   |
| Compose  | Docker Compose                   | Multi-container orchestration              |

## Prerequisites

- [Docker](https://docs.docker.com/get-started/) >= 24.0
- [Docker Compose](https://docs.docker.com/compose/) >= 2.20
- [Bun](https://bun.sh/) >= 1.3 (lint tooling and frontend development)
- [uv](https://docs.astral.sh/uv/) >= 0.5 (Python API development)

## Quick Start

### 1. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` with your Postgres credentials (used by Compose). Per-project examples live at
`api/.env.example` (API runtime config) and `web/.env.example` (web public env).

```env
POSTGRES_USER=todouser
POSTGRES_PASSWORD=todopassword
POSTGRES_DB=tododb
DATABASE_URL=postgresql://todouser:todopassword@db:5432/tododb
```

### 2. Build and run

```bash
docker compose up --build       # Foreground
docker compose up --build -d    # Detached
```

### 3. Access the application

| Service               | URL                                       |
|-----------------------|-------------------------------------------|
| Web UI                | <http://localhost:8080>                   |
| FastAPI Swagger UI    | <http://localhost:8000/docs>              |
| FastAPI ReDoc         | <http://localhost:8000/redoc>             |

## API Endpoints

| Method   | Endpoint        | Description       |
|----------|-----------------|-------------------|
| `GET`    | `/todos`        | List all tasks    |
| `GET`    | `/todos/{id}`   | Get a task by ID  |
| `POST`   | `/todos`        | Create a task     |
| `PUT`    | `/todos/{id}`   | Update a task     |
| `DELETE` | `/todos/{id}`   | Delete a task     |

## Project Structure

```text
.
├── api/                        # FastAPI service
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   ├── pyproject.toml
│   ├── uv.lock
│   ├── Dockerfile              # API image (Python slim + uvicorn)
│   ├── .dockerignore
│   └── .env.example            # API runtime env (DATABASE_URL)
├── web/                        # SvelteKit + Tailwind v4 frontend
│   ├── src/
│   ├── nginx.conf              # Reverse proxy + SPA fallback
│   ├── svelte.config.js
│   ├── vite.config.ts
│   ├── package.json
│   ├── Dockerfile              # Web image (multi-stage node + nginx)
│   ├── .dockerignore
│   └── .env.example            # Web public env (PUBLIC_API_BASE override)
├── docker-compose.yml          # Service orchestration
├── .env.example                # Compose-level env (Postgres credentials)
├── docs/                       # Documentation
└── README.md                   # This file
```

## Local Development (without Docker)

The API can run against SQLite without Docker — useful for quick iteration:

```bash
# API
cd api
uv sync                            # creates .venv and installs dependencies
uv run uvicorn main:app --reload   # http://localhost:8000

# Frontend (in another terminal)
cd web
bun install
bun run dev                        # http://localhost:5173 (proxies /api → :8000)
```

## Development Commands

```bash
# Docker
docker compose up --build       # Build and start all services
docker compose up -d            # Detached mode
docker compose down             # Stop all services
docker compose down -v          # Stop and remove volumes
docker compose logs -f          # Follow logs

# Linting (requires bun install)
bun run lint                    # Lint markdown and yaml
bun run lint:md:fix             # Auto-fix markdown

# Frontend
cd web && bun run check         # Type-check
cd web && bun run build         # Build static bundle (used by web/Dockerfile)

# Git
bun run commit                  # Interactive gitmoji commit
```

## Documentation

| File | Description |
|------|-------------|
| [`docs/AGENTS.md`](docs/AGENTS.md) | AI assistant guide and conventions |
| [`docs/CONVENTIONS.md`](docs/CONVENTIONS.md) | Code style and git conventions |
| [`docs/TECHNICAL_GUIDE.md`](docs/TECHNICAL_GUIDE.md) | Technical implementation and deployment |
| [`docs/PROJECT_STRUCTURE.md`](docs/PROJECT_STRUCTURE.md) | Directory and file organization |
| [`docs/FEATURES.md`](docs/FEATURES.md) | Epics and user stories |
| [`docs/COMPONENT_REFERENCE.md`](docs/COMPONENT_REFERENCE.md) | API endpoints and Svelte components |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Contribution guidelines |
| [`CHANGELOG.md`](CHANGELOG.md) | Version history |

## License

MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Maxime Lenne** - [maxime-lenne.fr](https://maxime-lenne.fr)
