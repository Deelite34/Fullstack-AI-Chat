# Full Stack AI Chat
<img width="1336" height="1269" alt="obraz" src="https://github.com/user-attachments/assets/542aa51c-5754-4890-a080-221e3809d41a" />

Full-stack AI chat application.
Playground for learning and improving my front-end skills.

## Stack

- Frontend: javascript with react, typescript, vite
- Backend: Python, fastapi, Ollama for running local ai model

## Features and plans

- AI Chat, where you can talk with AI (ollama3.2) model, and model keeps track of current conversation in memory.
- Chat utilizes http streaming for fluent response display
- Full typing with typescript and type hints for both backend and frontend
- Files cleanly divided into specific categories in frontend and backend
- Uses repository, service layer for code structure
- Frontend responsiveness through scaling html elements size as screen width decreases (clamp)- visible site elements keep reasonable size with lower screen sizes (until some minimal size)

Features to work on or consider, but while also resisting feature creep, where I try to make everything perfect while delaying implementing more important or useful things such as:

- Unit/integration tests for streaming
- General frontend tests (jest library?)
- Implementing and learning how to handle frontend side of logging in and sessions
- Add option to persists data in PostgreSQL database instead of memory

## Running

Run command:
docker compose up --build --watch
