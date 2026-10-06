# Campus Customs (HW4)

Campus Customs is a Yale-inspired apparel shop with a React/Vite/TypeScript frontend, a FastAPI backend, database-backed product and inventory answers, authentication, persistent signed-in chat history, dynamic product cards, and a PydanticAI shopping concierge.

## Before running

The data pack is intentionally not included in GitHub. Place it at this exact local path:

```text
hw4/data 4/campus_customs.db
hw4/data 4/products/<catalogue image files>
```

Copy `.env.example` to `.env` and replace the placeholder with your own `PORTKEY_API_KEY`. Never commit `.env`, the database, or product images.

## Install

From the `hw4/` folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd frontend
npm install
```

## Run the backend

In one terminal, from `hw4/backend/`:

```bash
uvicorn main:app --reload --port 8001
```

The API is available at `http://127.0.0.1:8001`. The backend uses the local database and images under `data 4/`.

## Run the frontend

In a second terminal, from `hw4/frontend/`:

```bash
npm run dev -- --host 127.0.0.1 --port 5176
```

Open `http://127.0.0.1:5176/`. The frontend is configured to call the backend on port 8001.

## Agent files

The agent consists of exactly these four files under `backend/`: `prompts/prompt.md`, `agent.py`, `tools.py`, and `models.py`. `main.py` exposes the FastAPI routes and loads the agent. The agent uses `gpt-5.6-luna` through Portkey and reads `PORTKEY_API_KEY` from `.env`.

## Submission documentation

- `AI_prompts.md` records the prompts used for the homework.
- `output/harness.md` explains the system, models, tools, safety rules, limits, and run commands.
- `output/design.md` explains the visual design work.
- `output/usability.md` explains the four usability improvements.
- `output/app_check.html` is a browser-check page with linked screenshots.
- `output/audit_trail.json` is append-only JSONL audit data from agent activity.
