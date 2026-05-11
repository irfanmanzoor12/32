# ── Stage 1: install dependencies ──────────────────────────────────────────
FROM python:3.12-slim AS deps

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.5 /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./
# --no-install-project: deps cached separately from source for faster rebuilds
RUN uv sync --frozen --no-dev --no-install-project

# ── Stage 2: production runtime ─────────────────────────────────────────────
FROM python:3.12-slim AS runtime

RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

COPY --from=deps --chown=appuser:appuser /app/.venv .venv
COPY --chown=appuser:appuser src/ src/

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH=src \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MCP_HOST=0.0.0.0 \
    MCP_PORT=8000

USER appuser
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["python", "-m", "tasks_mcp"]
