# Copilot instructions for AI Chat ollama

## Purpose

Use these instructions when working in this repository. Keep changes consistent with the existing architecture, toolchain, and repository layout.

## Project toolchain

- This is a web application, using python, fastapi in backend and node, tailwind, vite, react in frontend.
- Backend uses Python via `uv`, and applications is run only through docker compose containers. This means, use `uv run <command>` to run any python command, unless the user explicitly asks for a different approach.
For example:
  - `docker compose exec -it backend uv run python ...`
  - `docker compose exec -it backend uv run pytest ...`
  - `docker compose exec -it backend uv run ruff check ...`
- When running commands, remember that root backend path outside of docker maps to `/app/` path inside docker container.

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
