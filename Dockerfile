# ---- Stage 1: Builder ----
FROM python:3.13-slim AS builder

# Install uv for fast dependency resolution
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy dependency files first for layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies into a virtual environment
RUN uv sync --frozen --no-dev --no-install-project

# Copy the rest of the application
COPY . .

# Install the project itself
RUN uv sync --frozen --no-dev


# ---- Stage 2: Runtime ----
FROM python:3.13-slim AS runtime

WORKDIR /app

# Copy the virtual environment and app from builder
COPY --from=builder /app /app

# Add the virtual env to PATH
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Expose ports for FastAPI (8000) and MCP server (6969)
EXPOSE 8000
EXPOSE 6969

# Default: run the FastAPI web server
# Override with: docker run ... python app/mcp_main.py  (for MCP server)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "app"]
