FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install dependencies
# Copying pyproject.toml and uv.lock first for caching
COPY pyproject.toml uv.lock /app/
RUN uv sync --frozen --no-cache

# Copy the rest of the app
COPY ./app /app/app

ENV PYTHONPATH=/app
ENV PATH="/app/.venv/bin:$PATH"

# Run the app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
