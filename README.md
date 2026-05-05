# AEO Report Card

Production-style AEO diagnostic app for the Pixii.ai assessment.

## Stack
- Frontend: Next.js (App Router, TypeScript)
- Backend: FastAPI + SQLAlchemy
- Data: PostgreSQL on Railway (SQLite fallback for local/tests)
- LLM Providers: OpenAI, Anthropic, Gemini
- Competitor Discovery: SerpAPI primary, free DuckDuckGo fallback

## Monorepo Structure
```text
apps/
  api/        FastAPI backend
  web/        Next.js frontend
packages/
  shared/     Shared schemas, types, prompts
```

## Core Flows
- `POST /api/v1/diagnostics/run`
- `POST /api/v1/diagnostics/rerun`
- `GET /api/v1/diagnostics/runs/{run_id}`
- `GET /api/v1/diagnostics/reports/{run_id}/export?format=md|pdf`

## Local Setup
1. Copy environment files:
```bash
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env.local
```
2. Install frontend workspace dependencies:
```bash
npm install
```
3. Install backend dependencies:
```bash
pip install -e "apps/api[dev]"
```
4. Run frontend:
```bash
npm run dev:web
```
5. Run backend:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --app-dir apps/api
```

## Docker
```bash
docker compose up --build
```

## Quality Gates
- Frontend:
```bash
npm run check:web
```
- Backend:
```bash
npm run check:api
```

## Deployment
### Frontend (Vercel)
- Root directory: `apps/web`
- Env: `NEXT_PUBLIC_API_BASE_URL=https://<railway-api-domain>`

### Backend (Railway)
- Root directory: `apps/api`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Add PostgreSQL plugin and set `DATABASE_URL`
- Set provider keys:
  - `OPENAI_API_KEY`
  - `ANTHROPIC_API_KEY`
  - `GEMINI_API_KEY`
  - Optional: `SERPAPI_KEY`

## Demo Script
1. Paste target Amazon URL and shopper query.
2. Run report and show score + recommendation status.
3. Show provider evidence cards.
4. Show action plan.
5. Trigger rerun to show score delta.
6. Export Markdown/PDF.

