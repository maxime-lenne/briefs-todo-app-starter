# MCP Configuration for briefs-todo-app-starter

This directory contains configuration for **Model Context Protocol (MCP)** servers that extend Mistral Vibe's capabilities when working with this project.

## Overview

MCP (Model Context Protocol) is a standard for connecting AI assistants to external tools, resources, and APIs. These servers provide additional capabilities beyond the default Vibe functionality.

## Recommended MCP Servers

| Server | Purpose | Recommended | Status |
|--------|---------|-------------|--------|
| **github** | GitHub API integration | ✅ Yes | Official |
| **filesystem** | Local filesystem access | ✅ Yes | Official |
| **process** | Execute system commands | ✅ Yes | Official |
| **git** | Git operations | ✅ Yes | Official |
| **docker** | Docker container management | ✅ Yes | Community |
| **http** | HTTP requests | ✅ Yes | Official |
| **openapi** | OpenAPI/Swagger spec reader | ✅ Yes | Community |
| **sql** | SQL database queries | ⚠️ Optional | Community |
| **fetch** | Web content fetching | ⚠️ Optional | Official |
| **redis** | Redis database access | ⚠️ Optional | Community |

## Setup Instructions

### 1. Install MCP CLI
```bash
npm install -g @modelcontextprotocol/cli
```

### 2. Install Required Servers

#### Official MCP Servers
```bash
# GitHub, Filesystem, Process, HTTP, Fetch
npm install -g @modelcontextprotocol/server-github
npm install -g @modelcontextprotocol/server-filesystem
npm install -g @modelcontextprotocol/server-process
npm install -g @modelcontextprotocol/server-http
npm install -g @modelcontextprotocol/server-git
```

#### Community MCP Servers
```bash
# Docker
npm install -g @modelcontextprotocol/mcp-server-docker

# OpenAPI
npm install -g mcp-openapi

# SQL (optional)
npm install -g @modelcontextprotocol/mcp-server-sql

# Redis (optional)
npm install -g @modelcontextprotocol/mcp-server-redis
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# GitHub Token (required for github MCP)
GITHUB_TOKEN=your_github_personal_access_token

# Optional: Docker host (default: unix:///var/run/docker.sock)
DOCKER_HOST=unix:///var/run/docker.sock

# Optional: API base URL for http and openapi MCPs
API_BASE_URL=http://localhost:8000
```

**Important**: Never commit `.env` files with tokens or secrets!

### 4. Test MCP Servers

```bash
# List available MCP servers
mcp list

# Test filesystem MCP
mcp read filesystem --path .

# Test GitHub MCP
mcp list_issues github --repo briefs-todo-app-starter

# Test Docker MCP (requires Docker to be running)
mcp list_containers docker
```

## Project-Specific MCP Usage

### With FastAPI OpenAPI

1. Start the API locally:
```bash
cd api && uvicorn main:app --reload
```

2. Use openapi MCP to explore endpoints:
```bash
# List all endpoints
mcp list_endpoints openapi --url http://localhost:8000/openapi.json

# Get endpoint details
mcp get_endpoint_details openapi --url http://localhost:8000/openapi.json --endpoint /todos

# List all schemas
mcp list_schemas openapi --url http://localhost:8000/openapi.json
```

### With Docker

The docker MCP allows you to manage containers without leaving Vibe:

```bash
# List all containers
mcp list_containers docker

# List images
mcp list_images docker

# Start a container
mcp start_container docker --container todo-api

# Stop a container
mcp stop_container docker --container todo-api

# Get container logs
mcp get_container_logs docker --container todo-api

# Execute a command in a container
mcp exec_command docker --container todo-api --command "bash -c 'ls -la'"
```

### With GitHub

The github MCP integrates with GitHub's API:

```bash
# List issues
mcp list_issues github --repo briefs-todo-app-starter

# List pull requests
mcp list_pull_requests github --repo briefs-todo-app-starter

# Get repository information
mcp get_repository github --repo briefs-todo-app-starter

# Create an issue
mcp create_issue github --repo briefs-todo-app-starter --title "New Feature" --body "Description"

# Get commits
mcp get_commits github --repo briefs-todo-app-starter --count 10
```

### With Filesystem

The filesystem MCP provides file access:

```bash
# Read a file
mcp read filesystem --path api/main.py

# List directory contents
mcp list_directory filesystem --path api/

# Search for files
mcp search_files filesystem --path . --pattern "*.py"

# Write a file (if READ_ONLY is false)
mcp write_file filesystem --path test.txt --content "Hello"
```

### With Process

The process MCP allows command execution:

```bash
# Run a command
mcp run_command process --command "docker compose ps"

# Start a process in background
mcp start_process process --command "sleep 60"

# List running processes
mcp list_processes process
```

## Configuration Files

### `list.json`
Contains the list of all available MCP servers with their capabilities, types, and configuration options.

### `config.json`
Main configuration file for MCP servers in this project. It includes:
- Server configurations with environment variables
- Skills configuration
- Hooks configuration
- Logging settings
- Feature flags

### Customizing Configuration

To customize MCP configuration for your needs:

1. Edit `config.json` to:
   - Enable/disable specific servers
   - Modify environment variables
   - Add custom hooks
   - Change skill auto-loading behavior

2. Edit `servers/list.json` to:
   - Add new MCP servers
   - Modify server capabilities
   - Update server URLs

## Security Considerations

### Filesystem MCP
- ⚠️ **Be careful with allowed directories** - Only allow access to necessary directories
- 🔒 **Consider READ_ONLY mode** - Set `READ_ONLY: true` if write access is not needed
- 🚫 **Never allow sensitive directories** - Keep `.venv`, `node_modules`, `.git` in denied list

### GitHub MCP
- 🔑 **Use Personal Access Tokens (PAT)** - Create with minimal required permissions
- 🎭 **Use fine-grained tokens** - Limit to specific repositories if possible
- 🔄 **Rotate tokens regularly** - Change tokens periodically

### Docker MCP
- 🐳 **Requires Docker socket access** - Ensure the socket is properly secured
- 🧱 **Limit container operations** - Be cautious with privileged operations
- 🌐 **Network isolation** - Consider network security when managing containers

### General Security
- ❌ **Never commit `.env` files** with tokens or secrets
- 🔑 **Use GitHub Secrets** for CI/CD tokens
- 🛡️ **Review server capabilities** - Only enable what you need
- 🔍 **Audit regularly** - Review MCP configurations periodically

## Useful Commands

### Manage MCP Servers
```bash
# List all MCP servers
mcp list

# Show server info
mcp info [server-name]

# Start a server
mcp start [server-name]

# Stop a server
mcp stop [server-name]
```

### Interact with MCP Servers
```bash
# List available resources
mcp list [server-name]

# Get resource details
mcp get [server-name] [resource-type] [options]

# Call server tool
mcp [tool-name] [server-name] [options]
```

## Integration with Vibe Skills

The MCP configuration is integrated with the project's skills:

- **todo-app skill**: Uses filesystem and process MCP for project operations
- **fastapi-sqlalchemy skill**: Uses http and openapi MCP for API testing
- **docker skill**: Uses docker MCP for container management
- **testing skill**: Uses all relevant MCPs for testing
- **security skill**: Uses various MCPs for security scanning

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| MCP server not found | Install the server: `npm install -g @modelcontextprotocol/server-[name]` |
| Authentication failed | Check environment variables (GITHUB_TOKEN, etc.) |
| Permission denied (filesystem) | Check ALLOWED_DIRECTORIES and DENIED_DIRECTORIES |
| Docker commands not working | Ensure Docker is running and socket is accessible |
| Connection refused | Check if the service is running (API, database, etc.) |
| Timeout errors | Increase TIMEOUT in config.json |

### Debug Mode

Enable debug logging to see detailed MCP communication:

```json
{
  "logging": {
    "level": "debug",
    "format": "json",
    "output": "stdout"
  }
}
```

### Testing MCP Connectivity

```bash
# Test GitHub token
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user

# Test Docker socket
ls -la /var/run/docker.sock

# Test API endpoint
curl http://localhost:8000/health
```

## Updates and Maintenance

### Updating MCP Servers

```bash
# Update all MCP servers
npm update -g @modelcontextprotocol/*

# Update specific server
npm update -g @modelcontextprotocol/server-github
```

### Adding New MCP Servers

1. Find the server in the [MCP Server Registry](https://github.com/modelcontextprotocol/servers)
2. Install it: `npm install -g [server-package]`
3. Add it to `servers/list.json`
4. Add configuration to `config.json`
5. Test the server

### Removing MCP Servers

1. Remove from `servers/list.json`
2. Remove configuration from `config.json`
3. Uninstall (optional): `npm uninstall -g [server-package]`

## References

- [Model Context Protocol Specification](https://github.com/modelcontextprotocol/spec)
- [MCP Server Registry](https://github.com/modelcontextprotocol/servers)
- [Vibe MCP Documentation](https://docs.vibe.codes/mcp)

## Support

For issues with MCP configuration:
1. Check the [MCP documentation](https://github.com/modelcontextprotocol/spec)
2. Review server-specific documentation
3. Check Vibe's MCP documentation
4. Open an issue in the project repository

## License

This MCP configuration is part of the briefs-todo-app-starter project and is licensed under the MIT License.
