# Contributing

Thank you for your interest in contributing to the Docker To-Do App!

## Getting Started

1. Fork the repository
2. Clone your fork:

   ```bash
   git clone https://github.com/maxime-lenne/briefs-todo-app-starter.git
   cd briefs-todo-app-starter
   ```

3. Install linting dependencies:

   ```bash
   bun install
   ```

4. Copy environment variables:

   ```bash
   cp .env.example .env
   ```

5. Start the application:

   ```bash
   docker compose up --build
   ```

## Development Workflow

### Creating a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

### Making Changes

1. Make your changes following the project conventions
2. Test with Docker:

   ```bash
   docker compose up --build
   ```

3. Run linting:

   ```bash
   bun run lint
   ```

4. Commit your changes using gitmoji:

   ```bash
   bun run commit
   ```

### Project-Specific Guidelines

- **Python code** follows PEP 8 (enforced by Ruff)
- **API changes** must include updated Pydantic schemas
- **Database changes** must be reflected in SQLAlchemy models
- **New endpoints** must be tested via Swagger UI (`/docs`)
- **Docker changes** must be tested with `docker compose up --build`
- **Environment variables** must be documented in `.env.example`

### Commit Convention

This project uses **Gitmoji** for commit messages. Use the interactive tool:

```bash
bun run commit
```

Or write commits manually with the format: `<emoji> <description>`

Examples:

- `✨ Add task filtering endpoint`
- `🐛 Fix database connection retry logic`
- `🐳 Optimize API Dockerfile layer caching`
- `📝 Update API endpoint documentation`

Conventional commits are also accepted: `<type>(scope): <description>`

### Submitting a Pull Request

1. Push your branch to your fork:

   ```bash
   git push origin feature/your-feature-name
   ```

2. Open a Pull Request against the `develop` branch
3. Fill out the PR template
4. Ensure Docker builds succeed
5. Wait for review

## Code Style

- **Python**: PEP 8, type hints, docstrings for public functions
- **Dockerfiles**: Multi-stage builds, non-root users, minimal layers
- **YAML/Markdown**: Follow linting rules (`.markdownlint.json`, `.yamllint.yml`)

## Reporting Issues

- Use the issue templates when available
- Provide Docker and OS version for environment-specific bugs
- Include `docker compose logs` output when relevant

## Questions?

Feel free to open an issue for any questions or concerns.
