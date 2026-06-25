# Full Stack AI Chat
<img width="1336" height="1269" alt="obraz" src="https://github.com/user-attachments/assets/542aa51c-5754-4890-a080-221e3809d41a" />

Full-stack AI chat application.
Playground for learning and improving my front-end skills.

## Stack

- Frontend: javascript with react, typescript, vite
- Backend: Python, fastapi, Ollama for running local ai model

## Features and plans

- AI Chat, currently with no conversation memory. One response = one answer, but bot doesn't remember any messages in current conversation yet.
- Full typing with typescript and type hints for both backend and frontend
- Files cleanly divided into specific categories in frontend and backend
- Frontend responsiveness through scaling html elements size as screen width decreases - visible site elements keep reasonable size with lower screen sizes (until some minimal size)

Features to work on, but while also resisting feature creep, where I try to make everything perfect while delaying implementing more important or useful things such as:

- Conversation memory for model
- Unit/integration tests for streaming
- General frontend tests (jest library?)
- Implementing and learning how to handle frontend side of logging in and sessions
- Understand better basic react hooks other than useState()

## Running

Run command:
docker compose up --build --watch
