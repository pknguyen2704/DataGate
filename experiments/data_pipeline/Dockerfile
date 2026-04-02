FROM python:3.11-slim

# Install uv 
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy dependency definition
COPY pyproject.toml .

# Install dependencies into system python
RUN uv pip install --system --no-cache .

# Copy application
COPY app/ .
RUN mkdir -p auto_loader/checkpoint

ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]
