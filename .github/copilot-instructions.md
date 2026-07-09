# Copilot instructions for AI Chat ollama

## Purpose
Use these instructions when working in this repository. Keep changes consistent with the existing architecture, toolchain, and repository layout.

## Project toolchain
- This project uses Python via `uv` inside docker container in the backend workspace.
- When need to run Python commands, prefer running them inside docker container:
  - `docker compose exec -it backend uv run python ...`
  - `docker compose exec -it backend uv run pytest ...`
  - `docker compose exec -it backend  uv run ruff check ...`
- Do not assume that bare `python` is available in the system environment. Use `uv run` unless the user explicitly asks for a different approach.
- The frontend uses Node.js and `pnpm`, no need to use commands inside docker container:
  - `pnpm install`
  - `pnpm run dev`
  - `pnpm run build`
  - `pnpm run lint`
- Use Docker Compose for local services when the task involves the full stack.

## Repository layout
- Backend API code lives in `backend/`.
- Frontend code lives in `frontend/`.
- Docker configuration is in `docker-compose.yml`.
- Environment example values are in `example.env`.
