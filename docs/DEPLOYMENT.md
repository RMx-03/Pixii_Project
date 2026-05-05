# Deployment Guide

## Backend on Railway
1. Create a new Railway project.
2. Set root directory to `apps/api`.
3. Provision PostgreSQL plugin.
4. Set environment variables:
   - `DATABASE_URL`
   - `APP_ENV=production`
   - `OPENAI_API_KEY`
   - `ANTHROPIC_API_KEY`
   - `GEMINI_API_KEY`
   - Optional: `SERPAPI_KEY`
5. Deploy and copy public URL.

## Frontend on Vercel
1. Import repository in Vercel.
2. Set root directory to `apps/web`.
3. Set environment variable:
   - `NEXT_PUBLIC_API_BASE_URL=https://<railway-domain>`
4. Deploy and validate report flow.

## Smoke Checklist
- `/health` returns `{"status":"ok"}`.
- New run returns `run_id`.
- Report page renders scorecard and provider cards.
- Markdown and PDF exports download.

