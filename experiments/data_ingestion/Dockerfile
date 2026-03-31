# ─── Stage 1: dependency resolution ──────────────────────────────────────────
FROM python:3.11-slim AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /build

# Copy only the dependency manifest first (cache-friendly)
COPY pyproject.toml ./

# Export a plain requirements.txt from pyproject.toml, then install into
# a dedicated prefix so we can copy just the site-packages in Stage 2.
RUN uv export --no-hashes --format requirements-txt -o requirements.txt && \
    uv pip install --system --no-cache -r requirements.txt

# ─── Stage 2: runtime image ───────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

WORKDIR /app

# Copy application source (the src/ package lives inside app/)
COPY app/ ./src/

# Runtime directories for checkpoint / logs / rejected (persisted via volume)
RUN mkdir -p auto_loader/checkpoint auto_loader/logs auto_loader/rejected

# Forward all Python output to stdout/stderr immediately
ENV PYTHONUNBUFFERED=1

# Health-check: confirm the app module is importable
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "import src.config" || exit 1

CMD ["python", "-m", "src.main"]
