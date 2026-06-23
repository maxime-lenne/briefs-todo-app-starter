# Docker Multi-Container Skill

## Project Architecture
```text
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   PostgreSQL│────▶│    API     │◀────│     Web     │
│  (Internal) │     │  (FastAPI)  │     │ (SvelteKit) │
└─────────────┘     └─────────────┘     └─────────────┘
      │                   │                   │
      ▼                   ▼                   ▼
  pgdata volume    Container            Container
  (persistent)     (api image)         (web image)
```

## Docker Compose Configuration
```yaml
# docker-compose.yml
version: '3.8'

services:
  db:
    image: postgres:16-alpine
    container_name: todo-db
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-todo_user}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-todo_pass}
      POSTGRES_DB: ${POSTGRES_DB:-tododb}
    volumes:
      - pgdata:/var/lib/postgresql/data
    networks:
      - backend
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-todo_user} -d ${POSTGRES_DB:-tododb}"]
      interval: 5s
      timeout: 5s
      retries: 5

  api:
    build:
      context: .
      dockerfile: Dockerfile.api
    container_name: todo-api
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER:-todo_user}:${POSTGRES_PASSWORD:-todo_pass}@db:5432/${POSTGRES_DB:-tododb}
    ports:
      - "8000:8000"
    networks:
      - backend
      - frontend
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 256M

  web:
    build:
      context: .
      dockerfile: Dockerfile.web
    container_name: todo-web
    ports:
      - "5173:80"
    networks:
      - frontend
    depends_on:
      - api
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 256M

networks:
  backend:
    internal: true
  frontend:

volumes:
  pgdata:
```

## Dockerfile Patterns

### API Dockerfile
```dockerfile
# Dockerfile.api
FROM python:3.12-slim

# Create non-root user
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY api/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Copy application code
COPY api/ .

# Ensure scripts in .local are usable
ENV PATH=/root/.local/bin:${PATH}

# Switch to non-root user
USER appuser

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Web Dockerfile (Multi-stage)
```dockerfile
# Dockerfile.web
# Stage 1: Build
FROM node:22-alpine AS builder
WORKDIR /app

# Install dependencies
COPY web/package.json web/package-lock.json ./
RUN npm ci --no-audit --no-fund

# Copy application code
COPY web/ .

# Build the application
RUN npm run build

# Stage 2: Runtime (nginx)
FROM nginxinc/nginx-unprivileged:1.27-alpine

# Copy built files
COPY --from=builder /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY web/nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Run nginx
CMD ["nginx", "-g", "daemon off;"]
```

### Nginx Configuration
```nginx
# web/nginx.conf
server {
    listen 80;
    server_name localhost;

    # Enable gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;

    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://api:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeout settings
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
```

## Common Commands

| Command | Description |
|---------|-------------|
| `docker compose up --build -d` | Build and start all services in background |
| `docker compose up --build` | Build and start all services with logs |
| `docker compose down -v` | Stop and remove containers and volumes |
| `docker compose logs -f api` | Follow API service logs |
| `docker compose logs -f` | Follow all service logs |
| `docker compose exec api bash` | Enter API container shell |
| `docker compose exec web sh` | Enter Web container shell |
| `docker compose ps` | List running services |
| `docker compose restarts` | Restart all services |
| `docker compose pull` | Pull latest images |
| `docker compose build --no-cache` | Rebuild images without cache |

## Development Workflow

### Start Services
```bash
# Build and start all services
docker compose up --build -d

# View logs
docker compose logs -f

# Stop services (but keep containers)
docker compose stop

# Stop and remove containers
docker compose down

# Stop, remove containers and volumes
docker compose down -v
```

### Debugging
```bash
# Check container status
docker compose ps

# View resource usage
docker stats

# Enter a container
docker compose exec api bash

# View container logs
docker compose logs api

# Check network connectivity
docker compose exec api ping db
docker compose exec api curl -v http://db:5432
```

## Security Best Practices

### Do's ✅
- Use specific image tags (no `latest`)
- Create non-root users in Dockerfiles
- Set resource limits (CPU, memory)
- Use internal networks for database
- Configure health checks
- Use `.dockerignore` to exclude unnecessary files
- Clean pip cache: `pip install --no-cache-dir`
- Use `npm ci --no-audit --no-fund` for frontend
- Set `restart: unless-stopped`
- Use environment variables for secrets
- Enable health checks for all services
- Configure proper timeout settings

### Don'ts ❌
- Don't run containers as root
- Don't expose database ports externally
- Don't use `latest` tag for production
- Don't commit `.env` files
- Don't store secrets in images
- Don't allow web-to-database communication
- Don't use `sudo` in Dockerfiles
- Don't include unnecessary files in images

## Network Isolation
```yaml
networks:
  backend:
    # Only accessible by other services in the same compose file
    internal: true
  frontend:
    # Accessible from host and external
```

## Environment Variables
```bash
# .env.example
POSTGRES_USER=todo_user
POSTGRES_PASSWORD=todo_pass
POSTGRES_DB=tododb
DATABASE_URL=postgresql://todo_user:todo_pass@db:5432/tododb

# API configuration
API_PORT=8000
API_WORKERS=4

# Web configuration
WEB_PORT=5173
PUBLIC_API_BASE=/api
```

### .dockerignore
```
# .dockerignore
**/.venv
**/venv
**/node_modules
**/.git
**/.gitignore
**/.env
**/.env.*
**/__pycache__
**/*.pyc
**/*.pyo
**/*.pyd
*.sqlite
*.db
docker-compose.override.yml
Dockerfile*
docker-compose*
README.md
```

## Docker Compose Commands Reference

### Service Management
```bash
# Start specific service
docker compose up -d api

# Stop specific service
docker compose stop api

# Restart specific service
docker compose restart api

# Build specific service
docker compose build api

# Pull specific service image
docker compose pull api
```

### Container Management
```bash
# List all containers (including stopped)
docker ps -a

# List containers for this compose project
docker compose ps -a

# View container details
docker inspect todo-api

# Remove specific container
docker rm todo-api

# Remove all stopped containers
docker container prune
```

### Image Management
```bash
# List images
docker images

# Remove specific image
docker rmi briefs-todo-app-starter-api

# Remove all unused images
docker image prune -a

# View image details
docker inspect briefs-todo-app-starter-api
```

### Volume Management
```bash
# List volumes
docker volume ls

# View volume details
docker volume inspect briefs-todo-app-starter_pgdata

# Remove specific volume
docker volume rm briefs-todo-app-starter_pgdata

# Remove all unused volumes
docker volume prune
```

### Network Management
```bash
# List networks
docker network ls

# View network details
docker network inspect briefs-todo-app-starter_backend

# Remove specific network
docker network rm briefs-todo-app-starter_backend
```

## Debugging Common Issues

| Issue | Solution |
|-------|----------|
| Database connection fails | Check `DATABASE_URL` format and credentials |
| API not reachable from web | Verify nginx proxy config in `web/nginx.conf` |
| Volume not persisting | Check volume mount in compose file |
| Port already in use | Change host port or stop existing service |
| Build fails | Check Dockerfile paths and commands |
| Container won't start | Check logs: `docker compose logs service_name` |
| Health check fails | Increase timeout or adjust health check command |
| Out of memory | Increase memory limits or reduce container count |
| Permission denied | Check user permissions in Dockerfile |
| Image not found | Run `docker compose pull` or check image name |

## Dockerfile Security Checklist

### ✅ GOOD Practices
```dockerfile
# Use specific tags
FROM python:3.12-slim  # NOT python:latest

# Create non-root user
RUN useradd -m appuser
USER appuser

# Clean cache
RUN pip install --no-cache-dir -r requirements.txt

# Use multi-stage builds
FROM builder AS stage1
# Build step
FROM alpine AS final
COPY --from=stage1 /app /app
```

### ❌ BAD Practices
```dockerfile
# Running as root
USER root  # Avoid this!

# Using latest tag
FROM node:latest  # Avoid this!

# Committing secrets in image
ENV DB_PASSWORD=supersecret123  # NEVER do this!

# Installing unnecessary packages
RUN apt-get install -y vim wget curl  # Only install what's needed

# Not cleaning cache
RUN pip install -r requirements.txt  # Cache bloats image
```

## Production Configuration

### docker-compose.prod.yml
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  db:
    extends:
      file: docker-compose.yml
      service: db
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M

  api:
    extends:
      file: docker-compose.yml
      service: api
    environment:
      DATABASE_URL: ${DATABASE_URL}
      ENVIRONMENT: production
    deploy:
      resources:
        limits:
          cpus: '0.75'
          memory: 384M
      replicas: 2

  web:
    extends:
      file: docker-compose.yml
      service: web
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 256M
      replicas: 2
```

## Health Check Patterns

### PostgreSQL Health Check
```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 10s
```

### FastAPI Health Check
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

### Custom Health Check Script
```python
# api/health.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db

router = APIRouter()

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    # Test database connection
    try:
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"
    
    return {
        "status": "healthy" if db_status == "healthy" else "unhealthy",
        "database": db_status
    }
```

## Resource Limits

### CPU Limits
```yaml
deploy:
  resources:
    limits:
      cpus: '0.5'  # 0.5 CPU cores
    reservations:
      cpus: '0.25'  # Minimum guaranteed
```

### Memory Limits
```yaml
deploy:
  resources:
    limits:
      memory: 256M  # Hard limit
    reservations:
      memory: 128M  # Minimum guaranteed
```

### GPU Limits (if applicable)
```yaml
deploy:
  resources:
    limits:
      gpus: '1'  # Number of GPUs
```

## Trivy Security Scan Configuration

### .github/workflows/security-scan.yml
```yaml
name: Security Scan

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]
  schedule:
    - cron: '0 0 * * 0'  # Weekly scan

jobs:
  trivy-container-scan:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        image: [api, web]
    steps:
      - uses: actions/checkout@v6
      
      - name: Build Docker image
        run: docker build -t todo-${{ matrix.image }} -f Dockerfile.${{ matrix.image }} .
      
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: todo-${{ matrix.image }}
          format: 'sarif'
          output: trivy-${{ matrix.image }}-results.sarif
          severity: 'CRITICAL,HIGH'
          ignore-unfixed: true
          exit-code: 1
      
      - name: Upload Trivy scan results
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: trivy-${{ matrix.image }}-results.sarif
```

## When to Use This Skill
- Setting up or modifying Docker configuration
- Debugging container issues
- Optimizing Docker images
- Implementing security best practices
- Configuring multi-container applications
- Managing service dependencies
- Troubleshooting network connectivity
- Deploying applications with Docker

## Related Skills
- `todo-app` - For project-specific context
- `fastapi-sqlalchemy` - For API application
- `sveltekit-tailwind` - For frontend application
- `testing` - For testing Docker containers
- `security` - For Docker security best practices
