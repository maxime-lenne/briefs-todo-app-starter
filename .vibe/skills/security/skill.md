# Security Skill

## Security Checklist

### Database Security
- [x] PostgreSQL restricted to internal network (`internal: true`)
- [x] Dedicated database user (not `postgres`)
- [x] Strong passwords in `.env` (not committed)
- [x] No direct web-to-database communication
- [ ] Regular database backups
- [ ] Database encryption at rest (if sensitive data)
- [ ] Database audit logging

### Container Security
- [x] Non-root users in all Dockerfiles
- [x] Specific image tags (no `latest`)
- [x] Resource limits (CPU, memory)
- [x] `.dockerignore` to exclude sensitive files
- [x] Clean build cache (`--no-cache-dir`)
- [ ] Image vulnerability scanning (Trivy)
- [ ] Image signing (Cosign)
- [ ] Container runtime security (Falco, Aqua)

### Application Security
- [x] Input validation (Pydantic schemas)
- [x] SQL injection prevention (SQLAlchemy ORM)
- [ ] Rate limiting (FastAPI `slowapi` or similar)
- [ ] CORS configuration for production
- [ ] CSRF protection (if using forms)
- [ ] Secure cookie settings
- [ ] Environment variable validation
- [ ] Security headers

### Secrets Management
- [x] `.env` in `.gitignore`
- [x] `.env.example` with placeholder values
- [x] No hardcoded secrets in code
- [ ] Secrets scanning (Gitleaks, TruffleHog)
- [ ] Use GitHub Secrets for CI/CD
- [ ] Use a secrets manager for production

### Network Security
- [x] Internal networks for database
- [x] No exposed database ports
- [ ] Network policies and firewalls
- [ ] TLS/SSL for all external communications
- [ ] Mutual TLS for service-to-service communication

## Security Scanning

### Trivy Configuration

#### .github/workflows/security-scan.yml
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
    name: Trivy Container Scan
    runs-on: ubuntu-latest
    strategy:
      matrix:
        image: [api, web]
      fail-fast: false

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

  trivy-fs-scan:
    name: Trivy Filesystem Scan
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v6

      - name: Run Trivy filesystem scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: trivy-fs-results.sarif
          severity: 'CRITICAL,HIGH'
          ignore-unfixed: true

      - name: Upload Trivy scan results
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: trivy-fs-results.sarif
```

### Trivy Configuration File
```yaml
# .trivy.yml
cache-dir: .trivy/cache
severity: CRITICAL,HIGH
ignore-unfixed: true
exit-code: 1
skip-dirs:
  - .venv
  - node_modules
  - .git
vulnerability-type: all
```

### Gitleaks (Secrets Scanning)

#### .github/workflows/secrets-scan.yml
```yaml
name: Secrets Scan

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  gitleaks:
    name: Gitleaks Secrets Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
        with:
          fetch-depth: 0

      - name: Run Gitleaks
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GITLEAKS_CONFIG: .gitleaks.toml
```

#### .gitleaks.toml
```toml
# .gitleaks.toml
title = "Gitleaks Custom Configuration"

[extend]
useDefault = true

[[rules]]
description = "GitHub Token"
regex = '''(?i)(github|ghp|gho|ghu|ghs|ghr)_[0-9a-zA-Z]{36,}'''
tags = ["github", "token"]

[[rules]]
description = "GitHub OAuth"
regex = '''(?i)github(.{0,1}com|app)?[/:]([0-9a-zA-Z]{40})'''
tags = ["github", "oauth"]

[[rules]]
description = "Generic API Key"
regex = '''(?i)(api|apikey|api_key|token|secret|password|passwd)['\"]*[=:]['\"]*[0-9a-zA-Z\-_]{16,}'''
tags = ["api", "key", "secret"]

[[rules]]
description = "Database URL"
regex = '''(?i)(postgres|mysql|mongodb|redis|amqp)://[^\\s]+'''
tags = ["database", "url"]

[[rules]]
description = "Docker Hub Token"
regex = '''(?i)docksh|ghcr_io'''
tags = ["docker", "token"]

[[rules]]
description = "AWS Access Key"
regex = '''(?i)aws(.{0,20})?(?i)['\"][0-9a-zA-Z/+]{20,40}['\"]'''
tags = ["aws", "key"]

[[rules]]
description = "Private Key"
regex = '''(?i)-----BEGIN\\s*(?:RSA\\s*)?PRIVATE\\s*KEY-----'''
tags = ["key", "private"]

[allowlist]
description = "Ignore test files"
paths = [
  '''test_.*''',
  '''.*_test\\.py''',
  '''/tests/''',
  '''\\.min\\.js$''',
  '''\\.min\\.css$'''
]

[allowlist]
description = "Ignore example files"
paths = [
  '''\\.env\\.example''',
  '''\\.env\\.template''',
  '''\\.env\\.local'''
]
```

### Snyk Configuration

#### .github/workflows/snyk-scan.yml
```yaml
name: Snyk Security Scan

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  snyk-test:
    name: Snyk Test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6

      - name: Set up Node
        uses: actions/setup-node@v4
        with:
          node-version: '22'

      - name: Install frontend dependencies
        run: |
          cd web
          npm ci

      - name: Run Snyk to check for vulnerabilities
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          command: test
          args: --severity-threshold=high

  snyk-monitor:
    name: Snyk Monitor
    runs-on: ubuntu-latest
    needs: snyk-test
    steps:
      - uses: actions/checkout@v6

      - name: Run Snyk to monitor for vulnerabilities
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          command: monitor
```

## FastAPI Security Middleware

### main.py with Security Middleware
```python
# api/main.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import logging

app = FastAPI(
    title="To-Do API",
    version="0.1.0",
    description="A simple To-Do API with CRUD operations",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Rate Limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# CORS Middleware (configure for production)
if app.debug:
    # Development: allow all origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:8000", "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    # Production: restrict to specific origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "https://your-production-domain.com",
            "https://www.your-production-domain.com"
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Accept", "Origin"],
        max_age=86400,  # 24 hours
    )

# Trusted Host Middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        "localhost",
        "127.0.0.1",
        "your-production-domain.com",
        "www.your-production-domain.com"
    ]
)

# HTTPS Redirect Middleware (enable in production)
# app.add_middleware(HTTPSRedirectMiddleware)

# Compression Middleware
app.add_middleware(
    GZipMiddleware,
    minimum_size=1000,
    compresslevel=6
)


# Rate limited endpoints
@app.get("/todos")
@limiter.limit("100/minute")
async def list_todos(request: Request, db: Session = Depends(get_db)):
    return crud.get_todos(db)


@app.post("/todos")
@limiter.limit("60/minute")
async def create_todo(
    request: Request,
    todo: schemas.TodoCreate,
    db: Session = Depends(get_db)
):
    return crud.create_todo(db, todo)


# Rate limit exception handler
@app.exception_handler(RateLimitExceeded)
async def rate_limit_exception_handler(request: Request, exc: RateLimitExceeded):
    logger.warning(f"Rate limit exceeded for {request.client.host}: {request.url}")
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Too many requests. Please try again later.",
            "retry_after": str(exc.detail.headers.get("Retry-After", "60"))
        },
    )


# Global exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP Error: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred"},
    )
```

### Security Headers Middleware
```python
# api/middleware/security_headers.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data: https:; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "midi=(), "
            "notifications=(), "
            "push=(), "
            "sync-xhr=(), "
            "microphone=(), "
            "camera=(), "
            "magnetometer=(), "
            "gyroscope=(), "
            "fullscreen=(self), "
            "payment=()"
        )
        response.headers["Cache-Control"] = "no-store, max-age=0"
        
        return response
```

## Authentication and Authorization

### JWT Authentication Example
```python
# api/auth.py
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session
import crud
import schemas
from database import get_db

# Secret key and algorithm
SECRET_KEY = "your-secret-key-here-use-env-variables-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class UserInDB(BaseModel):
    username: str
    hashed_password: str


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = crud.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: schemas.User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


# Add authentication to routes
@app.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = crud.get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me")
async def read_users_me(
    current_user: schemas.User = Depends(get_current_active_user)
):
    return current_user
```

### Role-Based Access Control
```python
# api/auth.py (continued)
from typing import List, Union
from fastapi import Security
from fastapi.security import SecurityScopes


class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles
    
    def __call__(self, user: schemas.User = Depends(get_current_active_user)):
        if not any(role in user.roles for role in self.allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted"
            )
        return user


# Usage in routes
@app.get("/admin/users")
async def list_all_users(
    user: schemas.User = Security(RoleChecker(["admin"]))
):
    return crud.get_all_users()


@app.post("/todos")
async def create_todo(
    todo: schemas.TodoCreate,
    db: Session = Depends(get_db),
    user: schemas.User = Depends(get_current_active_user)
):
    return crud.create_todo_for_user(db, todo, user.id)
```

## Input Validation and Sanitization

### Enhanced Pydantic Schemas
```python
# api/schemas.py
from pydantic import BaseModel, Field, field_validator, field_serializer
from typing import Optional, List
import re
from datetime import datetime


class SanitizedString(str):
    """String that has been sanitized for XSS and injection."""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError('string required')
        # Remove potentially dangerous characters
        v = v.replace('<', '').replace('>', '')
        v = v.replace('"', "'").replace("'", "'")
        v = re.sub(r'javascript:', '', v, flags=re.IGNORECASE)
        v = re.sub(r'on\w+\s*=', '', v, flags=re.IGNORECASE)
        return cls(v)
    
    def __repr__(self):
        return f"SanitizedString({super().__repr__()})"


class TodoBase(BaseModel):
    title: SanitizedString = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Task title (sanitized)"
    )
    description: Optional[SanitizedString] = Field(
        None,
        max_length=500,
        description="Task description (sanitized)"
    )
    completed: bool = Field(False, description="Task completion status")
    
    @field_validator('title', 'description')
    @classmethod
    def validate_no_sql_injection(cls, v: str) -> str:
        """Validate that the string doesn't contain SQL injection patterns."""
        if not v:
            return v
        sql_patterns = [
            r'(?i)select\s+',
            r'(?i)insert\s+',
            r'(?i)update\s+',
            r'(?i)delete\s+',
            r'(?i)drop\s+',
            r'(?i)alter\s+',
            r'(?i)union\s+',
            r';\s*--',
            r'\b(?:or|and)\s+1\s*=\s*1\b',
        ]
        for pattern in sql_patterns:
            if re.search(pattern, v):
                raise ValueError('Potentially dangerous input detected')
        return v


class TodoCreate(TodoBase):
    pass


class TodoUpdate(BaseModel):
    title: Optional[SanitizedString] = Field(
        None,
        min_length=1,
        max_length=200
    )
    description: Optional[SanitizedString] = Field(
        None,
        max_length=500
    )
    completed: Optional[bool] = None
    
    @field_serializer('title', 'description')
    def serialize_sanitized(self, value: Optional[str]) -> Optional[str]:
        """Serialize sanitized strings."""
        return value
```

## Environment Variable Management

### pydantic-settings for Configuration
```python
# api/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Database
    DATABASE_URL: str = "sqlite:///./todo.db"
    
    # API
    API_TITLE: str = "To-Do API"
    API_VERSION: str = "0.1.0"
    API_DEBUG: bool = False
    
    # Security
    SECRET_KEY: str = "change-me-in-production-use-env-variables"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DEFAULT: str = "100/minute"
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:8000"
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: str = "GET,POST,PUT,DELETE,OPTIONS"
    CORS_ALLOW_HEADERS: str = "Authorization,Content-Type,Accept,Origin"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    @property
    def cors_allow_methods_list(self) -> list[str]:
        """Parse allowed methods from comma-separated string."""
        return [method.strip() for method in self.CORS_ALLOW_METHODS.split(",")]
    
    @property
    def cors_allow_headers_list(self) -> list[str]:
        """Parse allowed headers from comma-separated string."""
        return [header.strip() for header in self.CORS_ALLOW_HEADERS.split(",")]


@lru_cache()
def get_settings():
    return Settings()


# Usage in main.py
from config import get_settings, Settings

settings = get_settings()

app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    debug=settings.API_DEBUG
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.cors_allow_methods_list,
    allow_headers=settings.cors_allow_headers_list,
)
```

### .env.example
```bash
# .env.example

# Database Configuration
DATABASE_URL=postgresql://todo_user:todo_pass@db:5432/tododb
# For development (SQLite):
# DATABASE_URL=sqlite:///./todo.db

# API Configuration
API_TITLE="To-Do API"
API_VERSION="0.1.0"
API_DEBUG=false

# Security Configuration
SECRET_KEY=your-secret-key-here-generate-with-openssl-rand-hex-32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_DEFAULT="100/minute"

# CORS Configuration
CORS_ORIGINS=http://localhost:5173,http://localhost:8000
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=GET,POST,PUT,DELETE,OPTIONS
CORS_ALLOW_HEADERS=Authorization,Content-Type,Accept,Origin

# PostgreSQL Credentials (used by docker-compose)
POSTGRES_USER=todo_user
POSTGRES_PASSWORD=todo_pass
POSTGRES_DB=tododb

# Logging
LOG_LEVEL=INFO
LOG_FORMAT="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

## Docker Security Best Practices

### Dockerfile Security Checklist
```dockerfile
# ✅ GOOD: Use specific, minimal base images
FROM python:3.12-slim  # NOT python:latest or python:3.12

# ✅ GOOD: Create a dedicated non-root user
RUN groupadd -r appgroup && useradd -r -g appgroup appuser
WORKDIR /app

# ✅ GOOD: Install only necessary dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# ✅ GOOD: Use --no-cache-dir to reduce image size
RUN pip install --no-cache-dir --user -r requirements.txt

# ✅ GOOD: Copy only what's needed
COPY api/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt
COPY api/ .

# ✅ GOOD: Switch to non-root user
USER appuser

# ✅ GOOD: Set environment variables securely
ENV PYTHONPATH=/app
ENV PATH=/root/.local/bin:${PATH}

# ✅ GOOD: Use exec form for CMD
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### ❌ BAD Practices to Avoid
```dockerfile
# ❌ BAD: Using latest tag
FROM python:latest

# ❌ BAD: Running as root
USER root

# ❌ BAD: Committing secrets in Dockerfile
ENV DB_PASSWORD=supersecret123
RUN echo "DB_PASSWORD=$DB_PASSWORD" >> .env

# ❌ BAD: Installing unnecessary packages
RUN apt-get install -y vim wget curl git

# ❌ BAD: Not cleaning up
RUN pip install -r requirements.txt

# ❌ BAD: Using shell form for CMD (can be exploited)
CMD uvicorn main:app --host 0.0.0.0 --port 8000

# ❌ BAD: Not setting a working directory
# Missing WORKDIR

# ❌ BAD: Copying everything
COPY . .
```

## Security Headers for Nginx

### web/nginx.conf with Security Headers
```nginx
# web/nginx.conf
server {
    listen 80;
    server_name localhost;

    # Enable gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
    gzip_min_length 1000;
    gzip_comp_level 6;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https:; style-src 'self' 'unsafe-inline' https:; img-src 'self' data: https:; font-src 'self' https:; connect-src 'self' https:; frame-ancestors 'none'; base-uri 'self'; form-action 'self';" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Permissions-Policy "geolocation=(), microphone=(), camera=(), payment=(), usb=()" always;
    add_header Cache-Control "no-store, max-age=0" always;

    # Hide server version
    server_tokens off;

    # Prevent MIME type sniffing
    types {}
    default_type application/octet-stream;

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
        
        # Security headers for proxy
        proxy_hide_header X-Powered-By;
        proxy_hide_header Server;
        
        # Timeout settings
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Deny access to hidden files
    location ~ /\. {
        deny all;
        return 404;
    }

    # Deny access to specific file types
    location ~* \.(env|config|ini|log|bak|sql|md)$ {
        deny all;
        return 404;
    }
}
```

## OWASP Top 10 Mitigations

| Risk | Mitigation | Implementation | Status |
|------|------------|----------------|--------|
| A01:2021 - Broken Access Control | Proper authentication/authorization | JWT + Role-based access | ⚠️ Partial |
| A02:2021 - Cryptographic Failures | Use HTTPS, strong algorithms | TLS configuration, bcrypt | ⚠️ Partial |
| A03:2021 - Injection | Use ORM, parameterized queries | SQLAlchemy ORM | ✅ Complete |
| A04:2021 - Insecure Design | Threat modeling, secure defaults | Architecture review | ⚠️ Partial |
| A05:2021 - Security Misconfiguration | Secure defaults, scanning | Trivy, Snyk, Docker security | ✅ Complete |
| A06:2021 - Vulnerable Components | Dependency scanning | Dependabot, Renovate, Trivy | ✅ Complete |
| A07:2021 - Auth Failures | Strong authentication | JWT with bcrypt | ⚠️ Partial |
| A08:2021 - Software Integrity | Code signing, dependency verification | Cosign (optional) | ❌ Not Implemented |
| A09:2021 - Logging Failures | Comprehensive logging | Structured logging | ⚠️ Partial |
| A10:2021 - SSRF | Input validation, allowlists | URL validation in API | ⚠️ Partial |

## Incident Response Plan

### 1. Detection
- **Monitoring**: GitHub Actions, Sentry, or custom monitoring
- **Alerts**: Configure alerts for security-related events
- **Logging**: Centralized logging with structured format

### 2. Containment
- **Isolation**: Isolate affected systems and containers
- **Access Control**: Revoke compromised credentials
- **Network**: Block malicious IPs at firewall level

### 3. Eradication
- **Patch**: Apply security patches
- **Rotate**: Rotate all secrets and credentials
- **Clean**: Remove malware or malicious code
- **Verify**: Ensure all systems are clean

### 4. Recovery
- **Restore**: Restore services from clean backups
- **Test**: Verify all functionality works
- **Monitor**: Increase monitoring during recovery

### 5. Lessons Learned
- **Post-mortem**: Conduct thorough analysis
- **Document**: Update security policies and procedures
- **Prevent**: Implement preventive measures

### Security Contact Information
```markdown
## Security

If you discover a security vulnerability in this project, please follow our [Security Policy](SECURITY.md):

- **Report vulnerabilities**: security@your-domain.com
- **Response time**: 24-48 hours for critical issues, 5-7 days for non-critical
- **Disclosure policy**: Coordinated disclosure
- **Bug bounty**: Not currently available

Please do not create GitHub issues for security vulnerabilities.
```

## SECURITY.md Template
```markdown
# Security Policy

## Supported Versions

We provide security updates for the following versions:

| Version | Supported |
|---------|----------|
| >= 1.0.0 | ✅ Yes |
| < 1.0.0 | ❌ No |

## Reporting a Vulnerability

To report a security vulnerability, please:

1. **Do not** create a GitHub issue, pull request, or post in discussions
2. **Do not** disclose the vulnerability publicly
3. **Do** email security@your-domain.com with:
   - A clear description of the vulnerability
   - Steps to reproduce
   - Impact assessment
   - Suggested fix (if available)

We will:
- Acknowledge your report within 24 hours
- Provide a timeline for fixes
- Keep you updated on progress
- Credit you (if you wish) in the release notes

## Security Updates

Security updates are released as new versions with the appropriate severity:
- **Critical**: Immediate patch release
- **High**: Patch release within 1 week
- **Medium**: Patch release within 1 month
- **Low**: Next scheduled release

## Security Advisories

All security advisories are published in our [GitHub Security Advisories](https://github.com/owner/repo/security/advisories) page.

## Security Best Practices

- Keep dependencies updated
- Use HTTPS in production
- Rotate secrets regularly
- Enable rate limiting
- Monitor for suspicious activity
- Follow the principle of least privilege
```

## When to Use This Skill
- Implementing security best practices
- Configuring security middleware
- Setting up security scanning
- Managing secrets and credentials
- Handling security incidents
- Reviewing code for security vulnerabilities
- Configuring secure deployments

## Related Skills
- `todo-app` - For project-specific context
- `fastapi-sqlalchemy` - For FastAPI security
- `sveltekit-tailwind` - For frontend security
- `docker` - For container security
- `testing` - For security testing
