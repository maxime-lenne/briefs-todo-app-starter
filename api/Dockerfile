FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Create non-root user with /app owned by them
RUN useradd --create-home appuser && mkdir -p /app && chown appuser:appuser /app

WORKDIR /app

USER appuser

# Install dependencies (cached layer)
COPY --chown=appuser:appuser pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copy application code
COPY --chown=appuser:appuser . .

EXPOSE 8000

ENV PATH="/app/.venv/bin:$PATH"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
