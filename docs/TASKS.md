# Tasks

Project task tracking based on the project brief.

## Part 1: Multi-Container Application

### PostgreSQL Setup

- [x] Pull and configure the official PostgreSQL Docker image
- [x] Create the `tododb` database with dedicated user
- [x] Configure a Docker volume (`pgdata`) for data persistence
- [x] Test database connectivity from a client

### FastAPI API Dockerization

- [x] Adapt `database.py` to connect to PostgreSQL (via `DATABASE_URL` override)
- [x] Create SQLAlchemy models for the Todo entity
- [x] Create Pydantic schemas for request/response validation
- [x] Implement CRUD operations (create, read, update, delete)
- [x] Create `Dockerfile.api` with Python slim base image
- [x] Configure Uvicorn as the ASGI server
- [x] Test API endpoints via Swagger UI
- [ ] Push API image to Docker Hub

### Web (SvelteKit) Dockerization

- [x] Configure SvelteKit with `@sveltejs/adapter-static` and `fallback: 'index.html'`
- [x] Disable SSR in `+layout.ts` (full SPA mode)
- [x] Implement Svelte UI with task list display
- [x] Implement add, edit, delete, and toggle task actions
- [x] Create `Dockerfile.web` (multi-stage: node builder + nginx runtime)
- [x] Add `web/nginx.conf` reverse-proxying `/api/*` to the api service
- [x] Test web-to-API communication through the nginx proxy
- [ ] Push web image to Docker Hub

### Docker Compose Orchestration

- [x] Create `docker-compose.yml` with all three services (db, api, web)
- [x] Configure internal Docker networks (backend, frontend)
- [x] Set up environment variable substitution from `.env`
- [x] Configure service startup dependencies (`depends_on` + healthcheck)
- [x] Create `.env.example` with documented variables
- [x] Test full orchestration with `docker compose up --build`

---

## Part 2: Security and Optimization

### Container Security

- [x] Create non-root users in all Dockerfiles (api: `appuser`; web: `nginx-unprivileged` image)
- [x] Restrict PostgreSQL to internal backend network only (`internal: true`)
- [x] Ensure no direct web-to-database communication (web is only on `frontend`)
- [x] Verify `.env` file is in `.gitignore`
- [x] Use specific image tags (no `latest`) — `postgres:16-alpine`, `node:22-alpine`,
      `nginxinc/nginx-unprivileged:1.27-alpine`, `python:3.12-slim`

### Resource Management

- [x] Define CPU and memory limits for PostgreSQL in Compose
- [x] Define CPU and memory limits for API in Compose
- [x] Define CPU and memory limits for the web in Compose
- [x] Optimize Docker images (slim base, `uv sync --frozen --no-dev`, `bun install --frozen-lockfile`,
      multi-stage build)

### Orchestration Security

- [x] Configure `restart: unless-stopped` for all services
- [x] Verify network isolation (test external connection rejection)
- [ ] Run Trivy vulnerability scan on all images

---

## Part 3: Cloud Deployment (Optional)

- [ ] Create Railway account and project
- [ ] Deploy PostgreSQL via Railway plugin
- [ ] Deploy FastAPI service with `DATABASE_URL` from Railway
- [ ] Deploy web service pointing at the public API URL (or co-host behind nginx)
- [ ] Test CRUD operations on deployed application
- [ ] Document deployment steps in README.md
- [ ] Take screenshots of deployed application

---

## Completed (Template Setup)

- [x] Workflow release with changelog and GitHub release
- [x] Clean all docs
- [x] Issue and PR templates
- [x] Dependabot configuration
- [x] Renovate configuration
- [x] Commitlint (gitmoji)
- [x] Changelog (gitmoji + conventional)
- [x] Semantic-release (gitmoji)
- [x] EditorConfig
- [x] CONTRIBUTING.md
- [x] Adapt all documentation files for the SvelteKit stack

---

*Last updated: 2026-04-29*
