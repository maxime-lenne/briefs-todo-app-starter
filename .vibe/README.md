# Vibe Configuration for briefs-todo-app-starter

This directory contains **Mistral Vibe** configuration files for the **briefs-todo-app-starter** project. It includes skills, MCP server configurations, and hooks that enhance Vibe's capabilities when working with this specific project.

## 📁 Structure

```
.vibe/
├── README.md              # This file - Vibe configuration overview
├── skills/               # Project-specific and technology-specific skills
│   ├── todo-app/         # Main project skill
│   │   └── skill.md     # Project context, conventions, and patterns
│   ├── fastapi-sqlalchemy/
│   │   └── skill.md     # FastAPI + SQLAlchemy patterns and best practices
│   ├── sveltekit-tailwind/
│   │   └── skill.md     # SvelteKit + Tailwind CSS v4 patterns
│   ├── docker/
│   │   └── skill.md     # Docker and multi-container patterns
│   ├── testing/
│   │   └── skill.md     # Testing strategies and patterns
│   └── security/
│       └── skill.md     # Security best practices and patterns
└── mcp/                 # Model Context Protocol configurations
    ├── README.md         # MCP configuration guide
    ├── config.json       # Main MCP configuration
    └── servers/
        └── list.json     # List of available MCP servers
```

## 🎯 Skills

Skills are specialized modules that provide **context, instructions, and workflows** for specific domains or tasks. When Vibe loads a skill, it gains access to:

- Domain-specific knowledge and patterns
- Common tasks and their solutions
- Code examples and templates
- Best practices and conventions
- Troubleshooting guides

### Available Skills

| Skill | Domain | Purpose |
|-------|--------|---------|
| **todo-app** | Project-specific | Project context, conventions, file locations, common tasks |
| **fastapi-sqlalchemy** | Backend | FastAPI routes, SQLAlchemy models, CRUD patterns, testing |
| **sveltekit-tailwind** | Frontend | SvelteKit setup, Svelte 5 runes, Tailwind v4, component patterns |
| **docker** | Infrastructure | Dockerfiles, docker-compose, multi-container orchestration |
| **testing** | Quality | pytest, vitest, Playwright, test patterns, CI/CD testing |
| **security** | Security | Security scanning, middleware, authentication, OWASP top 10 |

### Skill Features

Each skill provides:
- **Best practices** for the domain
- **Code patterns** and examples
- **Testing strategies**
- **Common issues** and solutions
- **Debugging tips**
- **Related resources**

### Using Skills

Vibe automatically loads skills based on the project context. When you ask Vibe to:
- "Add a new API endpoint" → Loads `fastapi-sqlalchemy` skill
- "Create a Svelte component" → Loads `sveltekit-tailwind` skill
- "Debug Docker issues" → Loads `docker` skill
- "Write tests" → Loads `testing` skill
- "Add authentication" → Loads `security` skill

## 🤖 Model Context Protocol (MCP)

MCP extends Vibe's capabilities by connecting to **external tools, resources, and APIs**. MCP servers provide:

- **Filesystem access** - Read/write files directly
- **GitHub integration** - Manage issues, PRs, commits
- **Docker management** - Control containers and images
- **HTTP requests** - Make API calls
- **OpenAPI exploration** - Browse and test API endpoints
- **Process execution** - Run system commands

### Available MCP Servers

| Server | Type | Purpose | Recommended |
|--------|------|---------|-------------|
| **github** | Official | GitHub API integration | ✅ Yes |
| **filesystem** | Official | Local filesystem access | ✅ Yes |
| **process** | Official | Execute system commands | ✅ Yes |
| **git** | Official | Git operations | ✅ Yes |
| **docker** | Community | Docker container management | ✅ Yes |
| **http** | Official | HTTP requests | ✅ Yes |
| **openapi** | Community | OpenAPI/Swagger spec reader | ✅ Yes |
| **sql** | Community | SQL database queries | ⚠️ Optional |
| **fetch** | Official | Web content fetching | ⚠️ Optional |

### MCP Configuration

The MCP configuration is in `mcp/config.json` and includes:
- Server configurations with environment variables
- Skills auto-loading settings
- Hooks for automatic actions
- Logging and feature settings

See `mcp/README.md` for detailed setup instructions.

## ⚡ Quick Start

### 1. Install MCP Servers

```bash
# Install official MCP servers
npm install -g @modelcontextprotocol/server-github
npm install -g @modelcontextprotocol/server-filesystem
npm install -g @modelcontextprotocol/server-process
npm install -g @modelcontextprotocol/server-git
npm install -g @modelcontextprotocol/server-http

# Install community MCP servers
npm install -g @modelcontextprotocol/mcp-server-docker
npm install -g mcp-openapi
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# GitHub Token (required for github MCP)
GITHUB_TOKEN=your_github_personal_access_token

# Docker (optional)
DOCKER_HOST=unix:///var/run/docker.sock
```

### 3. Test Configuration

```bash
# Test skills are loaded
# Ask Vibe: "What are the project conventions?"

# Test MCP servers
mcp list
mcp list_issues github --repo briefs-todo-app-starter
mcp list_containers docker
```

## 📋 Workflow Examples

### Example 1: Adding a New API Endpoint

**You**: "Add an endpoint to get todos by completion status"

**Vibe's Process**:
1. Loads `todo-app` skill for project context
2. Loads `fastapi-sqlalchemy` skill for backend patterns
3. Identifies the pattern: add to `crud.py`, `schemas.py`, `routes.py`
4. Generates code following project conventions
5. Updates documentation in `COMPONENT_REFERENCE.md`

### Example 2: Creating a New Component

**You**: "Create a new TodoList component"

**Vibe's Process**:
1. Loads `todo-app` skill for project structure
2. Loads `sveltekit-tailwind` skill for component patterns
3. Creates file in `web/src/lib/components/TodoList.svelte`
4. Uses Svelte 5 runes and Tailwind classes
5. Follows project naming conventions (PascalCase)

### Example 3: Debugging Docker Issues

**You**: "The API container won't start"

**Vibe's Process**:
1. Loads `docker` skill for troubleshooting
2. Loads `todo-app` skill for project-specific context
3. Uses `docker` MCP to check container status: `mcp list_containers docker`
4. Checks logs: `mcp get_container_logs docker --container todo-api`
5. Provides solutions based on error patterns

### Example 4: Writing Tests

**You**: "Write tests for the CRUD operations"

**Vibe's Process**:
1. Loads `testing` skill for test patterns
2. Loads `fastapi-sqlalchemy` skill for backend context
3. Generates pytest fixtures and test cases
4. Follows project testing conventions
5. Integrates with CI/CD workflows

## 🔧 Customization

### Adding a New Skill

1. Create a new directory in `.vibe/skills/`
2. Add a `skill.md` file with the skill content
3. Reference the skill in `mcp/config.json` under `skills.autoLoad`

**Example skill.md structure**:
```markdown
# My New Skill

## Description
Brief description of what this skill covers.

## Best Practices
- Practice 1
- Practice 2
- Practice 3

## Common Tasks
### Task 1
Steps to complete task 1

### Task 2
Steps to complete task 2

## Code Patterns
```python
# Example code
```

## Troubleshooting
| Issue | Solution |
|-------|----------|
| Issue 1 | Solution 1 |
| Issue 2 | Solution 2 |

## Related Skills
- skill-1
- skill-2
```

### Modifying MCP Configuration

Edit `mcp/config.json` to:
- Enable/disable MCP servers
- Modify environment variables
- Add custom hooks
- Change skill auto-loading behavior

### Adding New MCP Servers

1. Find the server in the [MCP Server Registry](https://github.com/modelcontextprotocol/servers)
2. Install it: `npm install -g [server-package]`
3. Add it to `mcp/servers/list.json`
4. Add configuration to `mcp/config.json`

## 🎯 Best Practices

### For Skills
- ✅ **Be specific** - Focus on a single domain or technology
- ✅ **Include examples** - Show real code from the project
- ✅ **Follow conventions** - Respect project's `CONVENTIONS.md`
- ✅ **Document patterns** - Show common solutions
- ✅ **Update regularly** - Keep skills up-to-date with project changes
- ❌ **Don't duplicate** - Don't repeat what's already in docs

### For MCP
- ✅ **Start with essentials** - Enable servers you need most
- ✅ **Secure configurations** - Use environment variables for secrets
- ✅ **Restrict access** - Limit filesystem MCP to necessary directories
- ✅ **Test locally** - Verify MCP servers work before committing
- ❌ **Don't expose secrets** - Never commit `.env` files with tokens

### For Hooks
- ✅ **Automate common tasks** - Use hooks for repetitive operations
- ✅ **Keep them fast** - Hooks should execute quickly
- ✅ **Handle errors gracefully** - Don't break workflows
- ❌ **Don't over-automate** - Some decisions require human judgment

## 🚀 Advanced Usage

### Chaining Skills

Vibe can combine multiple skills for complex tasks:

**Example**: "Add a new feature with API endpoint and frontend component"
- Uses `todo-app` for project context
- Uses `fastapi-sqlalchemy` for backend
- Uses `sveltekit-tailwind` for frontend
- Uses `testing` for test generation
- Uses `docker` for deployment considerations

### MCP Server Combinations

Powerful workflows emerge from combining MCP servers:

**Example**: "Test the API and create a GitHub issue if tests fail"
1. Use `process` MCP to run tests: `mcp run_command process --command "cd api && pytest"`
2. Use `filesystem` MCP to read test results
3. Use `github` MCP to create an issue if tests failed

**Example**: "Deploy to production"
1. Use `docker` MCP to build images
2. Use `process` MCP to run `docker compose up`
3. Use `http` MCP to verify deployment
4. Use `github` MCP to create a deployment record

### Custom Hooks

Add custom hooks in `mcp/config.json`:

```json
{
  "hooks": {
    "onCommand": [
      {
        "patterns": ["deploy"],
        "skill": "docker",
        "action": "run_deployment_checklist"
      }
    ],
    "onFileChange": [
      {
        "patterns": ["api/**/*.py"],
        "skill": "testing",
        "action": "suggest_tests"
      }
    ]
  }
}
```

## 📊 Monitoring and Maintenance

### Skill Updates
- Review and update skills when:
  - Project structure changes
  - New technologies are added
  - Conventions are updated
  - New patterns emerge

### MCP Server Updates
```bash
# Update all MCP servers
npm update -g @modelcontextprotocol/*

# Check for new servers
npm search @modelcontextprotocol/server
```

### Configuration Review
- Regularly review `mcp/config.json`:
  - Remove unused servers
  - Update environment variables
  - Clean up old hooks
  - Optimize skill loading

## 🔍 Troubleshooting

### Skills Not Loading
- **Check**: Skill file exists in `.vibe/skills/[name]/skill.md`
- **Check**: Skill is in `skills.autoLoad` in `mcp/config.json`
- **Check**: No syntax errors in skill.md
- **Fix**: Run `mcp list` to see loaded servers

### MCP Server Not Working
- **Check**: Server is installed (`npm list -g @modelcontextprotocol/server-*`)
- **Check**: Environment variables are set
- **Check**: Server has proper permissions
- **Fix**: Test server manually with `mcp [tool] [server] [options]`

### Hooks Not Triggering
- **Check**: Hook pattern matches the command
- **Check**: Hook is in the correct event type (onStart, onCommand, onFileChange)
- **Check**: Skill is loaded
- **Fix**: Add debug logging to `mcp/config.json`

### Permission Issues
- **Filesystem MCP**: Check `ALLOWED_DIRECTORIES` and `DENIED_DIRECTORIES`
- **Docker MCP**: Check Docker socket permissions
- **GitHub MCP**: Check token permissions
- **Fix**: Adjust configurations and permissions

## 📚 Resources

### Vibe Documentation
- [Vibe Official Documentation](https://docs.vibe.codes)
- [Skills Documentation](https://docs.vibe.codes/skills)
- [MCP Documentation](https://docs.vibe.codes/mcp)
- [Hooks Documentation](https://docs.vibe.codes/hooks)

### MCP Resources
- [Model Context Protocol Specification](https://github.com/modelcontextprotocol/spec)
- [MCP Server Registry](https://github.com/modelcontextprotocol/servers)
- [Building MCP Servers](https://github.com/modelcontextprotocol/spec/blob/main/docs/building-servers.md)

### Project Resources
- [Project Documentation](docs/AGENTS.md) - Main AI guide
- [Technical Guide](docs/TECHNICAL_GUIDE.md) - Implementation details
- [Conventions](docs/CONVENTIONS.md) - Coding standards

## 🤝 Contributing

Contributions to Vibe configuration are welcome!

### Adding New Skills
1. Fork the repository
2. Create a new skill in `.vibe/skills/`
3. Add tests if applicable
4. Update documentation
5. Submit a pull request

### Improving Existing Skills
1. Identify improvements needed
2. Update the skill.md file
3. Test the changes
4. Submit a pull request

### Adding MCP Integrations
1. Research available MCP servers
2. Test integration locally
3. Add configuration to `mcp/servers/list.json` and `mcp/config.json`
4. Document the integration
5. Submit a pull request

## 📄 License

This Vibe configuration is part of the **briefs-todo-app-starter** project and is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

---

**Maintained by**: Project Contributors  
**Last Updated**: 2026-06-23  
**Vibe Version**: Compatible with Mistral Vibe  
**MCP Version**: Compatible with MCP Specification
