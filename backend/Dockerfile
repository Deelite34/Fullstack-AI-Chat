FROM python:3.13-slim

ENV PYTHONBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

COPY --from=ghcr.io/astral-sh/uv:0.7.12 /uv /uvx /bin/

RUN pip install --no-cache-dir --upgrade pip \
    && apt-get update \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock /app/
WORKDIR /app/
RUN uv sync --locked

COPY . .

EXPOSE 8000
EXPOSE 5678
ENTRYPOINT ["/app/docker-entrypoint.sh"]
