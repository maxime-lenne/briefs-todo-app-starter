# AGENTS.md

Main guide for AI assistants working on this repository.

**Full documentation**: [`docs/AGENTS.md`](docs/AGENTS.md)

## Quick commands

```bash
# Docker
docker compose up --build       # Build and start all services
docker compose up --build -d    # Build and start in background
docker compose down             # Stop all services
docker compose down -v          # Stop and remove volumes
docker compose logs -f          # Follow all logs

# Linting (requires bun install)
bun install           # Install linting dependencies
bun run lint          # Lint markdown and yaml
bun run lint:md       # Lint markdown only
bun run lint:md:fix   # Auto-fix markdown
bun run lint:commit   # Validate last commit message
bun run commit        # Interactive gitmoji commit
```

## Essential rules

1. **Always consult** `docs/AGENTS.md` before any modification
2. **Update** documentation when making changes
3. **Follow** conventions established in each `docs/` file
4. **Never** commit secrets or `.env` files
5. **Test** changes with `docker compose up --build` before committing
