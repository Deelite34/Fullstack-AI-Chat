#!/bin/sh

# uv run alembic upgrade head
# if [ $? -ne 0]; then
#     echo "Database migration failed."
#     exit 1
# fi


# debugpy allows debugger use inside docker container in vs code
exec uv run debugpy --listen 0.0.0.0:5678 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload  # development run

# exec tail -F whatever  # forcing container to keep running for debugging
# exec uv run uvicorn main:app --host 0.0.0.0 --port 8000  # prod run 