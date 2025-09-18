# Use official uv image for better caching and performance
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim AS base

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Create non-root user
RUN useradd --create-home --shell /bin/bash app

# Set working directory
WORKDIR /app

# Copy dependency files
COPY --chown=app:app pyproject.toml uv.lock* ./

# Development stage
FROM base AS dev

# Install development dependencies with cache mount
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --dev --frozen

# Copy source code
COPY --chown=app:app . .

# Switch to non-root user
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

# Default command for development (with reload)
CMD ["uv", "run", "--reload", "mcmqtt.main:main"]

# Production stage
FROM base AS prod

# Install production dependencies only with cache mount
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev --frozen --no-editable

# Copy source code
COPY --chown=app:app src/ ./src/
COPY --chown=app:app README.md ./

# Switch to non-root user
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

# Production command
CMD ["uv", "run", "mcmqtt.main:main"]