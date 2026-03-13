FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN mkdir -p app && touch app/__init__.py && pip install --no-cache-dir -e ".[dev]"

COPY . .

EXPOSE 8000
