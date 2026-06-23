# Project Structure

## Directory Organization

```text
todo-app/
├── api/                                # FastAPI application
│   ├── main.py                         # API entry point and routes
│   ├── database.py                     # Database connection and session
│   ├── models.py                       # SQLAlchemy ORM models
│   ├── schemas.py                      # Pydantic validation schemas
│   ├── crud.py                         # CRUD operations
│   └── requirements.txt                # Python dependencies (API)
├── web/                                # SvelteKit + Tailwind v4 frontend
│   ├── src/
│   │   ├── app.html                    # HTML shell
│   │   ├── app.css                     # Tailwind entry (`@import "tailwindcss"`)
│   │   ├── app.d.ts                    # SvelteKit type augmentation
│   │   ├── lib/
│   │   │   ├── api.ts                  # Typed fetch client
│   │   │   ├── types.ts                # Shared TypeScript types
│   │   │   └── components/
│   │   │       └── TodoItem.svelte     # Single task row component
│   │   └── routes/
│   │       ├── +layout.svelte          # Root layout (imports Tailwind)
│   │       └── +page.svelte            # Main task list page
│   ├── package.json                    # Frontend dependencies and scripts
│   ├── svelte.config.js                # SvelteKit configuration
│   ├── vite.config.ts                  # Vite config with `/api` proxy
│   ├── tsconfig.json                   # TypeScript configuration
│   ├── .gitignore
│   └── README.md
├── .claude/                            # Claude Code configuration
├── .github/                            # GitHub configuration
│   ├── workflows/                      # CI/CD workflows
│   │   ├── lint.yml                    # Markdown and YAML linting
│   │   ├── release.yml                 # Semantic release
│   │   ├── setup.yml                   # Repository setup
│   │   └── dependabot-lockfile.yml     # Dependabot lockfile updates
│   ├── ISSUE_TEMPLATE/                 # Issue templates
│   ├── pull_request_template.md
│   ├── CODEOWNERS
│   ├── dependabot.yml
│   └── settings.yml
├── docs/                               # Documentation
│   ├── AGENTS.md                       # AI assistant guide
│   ├── PROJECT_STRUCTURE.md            # This file
│   ├── CONVENTIONS.md                  # Code conventions
│   ├── TECHNICAL_GUIDE.md              # Technical guide
│   ├── DESIGN_SYSTEM.md                # Tailwind UI design
│   ├── COMPONENT_REFERENCE.md          # API and UI components
│   ├── FEATURES.md                     # Epics and user stories
│   ├── SCREEN_FLOW.md                  # Web app screen flows
│   └── TASKS.md                        # Task tracking
├── .env.example                        # Environment variables template
├── .gitignore                          # Git ignore rules
├── .gitmoji.json                       # Gitmoji configuration
├── .markdownlint.json                  # Markdownlint rules
├── .yamllint.yml                       # Yamllint configuration
├── .editorconfig                       # Editor settings
├── .releaserc.json                     # Semantic-release config
├── .husky/                             # Git hooks (Husky)
├── bun.lock                            # Bun lock file
├── commitlint.config.js                # Commit message validation
├── package.json                        # Bun config (linting, commits)
├── pyproject.toml                      # Python project metadata
├── renovate.json                       # Renovate configuration
├── brief.md                            # Project specification (historical)
├── CLAUDE.md                           # AI assistant entry point
├── CONTRIBUTING.md                     # Contribution guidelines
├── CHANGELOG.md                        # Version history
├── LICENSE                             # MIT License
└── README.md                           # Main documentation
```

---

## Application Code

### API (`api/`)

| File | Purpose |
|------|---------|
| `main.py` | FastAPI app initialization, route definitions, startup logic |
| `database.py` | SQLAlchemy engine, session factory, `get_db` dependency |
| `models.py` | SQLAlchemy ORM models (`Todo` table) |
| `schemas.py` | Pydantic models for request/response validation |
| `crud.py` | Database CRUD operations (create, read, update, delete) |
| `requirements.txt` | Python package dependencies for the API |

### Web (`web/`)

| File | Purpose |
|------|---------|
| `src/routes/+layout.svelte` | Root layout, imports `app.css` |
| `src/routes/+page.svelte` | Main task list page (state, filters, list rendering) |
| `src/lib/components/TodoItem.svelte` | Single task row with toggle / edit / delete |
| `src/lib/api.ts` | Typed fetch client targeting the `/api` proxy |
| `src/lib/types.ts` | Shared TypeScript types (`Todo`, `Filter`, etc.) |
| `src/app.html` | HTML shell |
| `src/app.css` | Tailwind v4 entry point |
| `vite.config.ts` | Vite plugins (Tailwind, SvelteKit) and `/api` dev proxy |
| `svelte.config.js` | Adapter and preprocess configuration |
| `package.json` | Frontend dependencies and scripts |

---

## Configuration Files

### Project Configuration

| File | Purpose |
|------|---------|
| `package.json` | Bun dependencies (linting, commits), scripts |
| `pyproject.toml` | Python project metadata and tooling |
| `bun.lock` | Locked dependency versions |
| `.gitmoji.json` | Gitmoji-cli configuration |
| `.env.example` | Documents required environment variables |

### Code Quality

| File | Purpose |
|------|---------|
| `.markdownlint.json` | Markdown linting rules |
| `.yamllint.yml` | YAML linting rules |
| `.editorconfig` | Editor settings |

### CI/CD

| File | Purpose |
|------|---------|
| `.github/workflows/lint.yml` | Lint on push/PR |
| `.github/workflows/release.yml` | Automated releases |
| `renovate.json` | Automatic dependency updates |
| `.github/dependabot.yml` | Security updates |

### Git Hooks

| Directory | Purpose |
|-----------|---------|
| `.husky/` | Git hooks managed by Husky |

---

## Documentation (`docs/`)

| File | Purpose |
|------|---------|
| `AGENTS.md` | Main guide for AI assistants |
| `PROJECT_STRUCTURE.md` | This file - directory layout |
| `CONVENTIONS.md` | Code style and git conventions |
| `TECHNICAL_GUIDE.md` | Technical implementation guide |
| `DESIGN_SYSTEM.md` | Tailwind UI tokens and patterns |
| `COMPONENT_REFERENCE.md` | API endpoints and Svelte components |
| `FEATURES.md` | Epics and user stories |
| `SCREEN_FLOW.md` | Web app navigation flows |
| `TASKS.md` | Project task tracking |

---

*Last updated: 2026-04-29*
