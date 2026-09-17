# Digital Twin API

Always-on FastAPI service wrapping Landon Nguyen’s agent + Chroma RAG.
Gradio (`app.py` on the `Digital-Twin` branch) is for local demos only — not used here.

## Endpoints

| Method | Path | Notes |
|--------|------|--------|
| `GET` | `/health` | Liveness |
| `POST` | `/session` | Allocate a visitor `session_id` |
| `POST` | `/chat/stream` | SSE: `session`, `token`, `done`, `error` |
| `POST` | `/chat/reset` | Clear that visitor’s SQLite session |

Body for stream/reset:

```json
{ "message": "Tell me about your capstone", "session_id": "<uuid>" }
```

Each visitor gets an isolated `SQLiteSession` (no shared `"12345"` id).

## Environment variables

| Name | Required | Purpose |
|------|----------|---------|
| `OPENAI_API_KEY` | yes | Agent + embeddings |
| `PORTFOLIO_ORIGINS` | yes (prod) | CORS allowlist, comma-separated |
| `PUSHOVER_USER` / `PUSHOVER_TOKEN` | no | Lead / unknown-question alerts |
| `TWIN_API_SECRET` | no | Optional shared secret header |
| `TWIN_MODEL` | no | Default `gpt-5.4-mini` |
| `TWIN_RATE_LIMIT_PER_MIN` | no | Default `20` |
| `PORT` | no | Default `8000` |

Never put OpenAI or Pushover keys in the Next.js frontend.

## Local run

```bash
cd twin-api
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # set OPENAI_API_KEY
uvicorn api:app --reload --port 8000
```

## Deploy (Railway / Render / Fly)

1. Point the service root at `twin-api/` (or deploy this folder as the repo root of a service).
2. Set env vars above; bake `twin_db/` and `Nguyen_Landon_CV.pdf` into the image (already in tree).
3. Health check: `GET /health`.
4. Set `PORTFOLIO_ORIGINS` to your Vercel URL(s) + `http://localhost:3000` for local widget testing.
5. Re-ingest offline via `python ingest.py` when `twin_reference_base/` changes; redeploy with updated `twin_db/`.

### Docker

```bash
docker build -t landon-twin-api .
docker run -p 8000:8000 --env-file .env landon-twin-api
```

## Portfolio wiring

On Vercel, set only:

```
NEXT_PUBLIC_TWIN_API_URL=https://your-twin-host.example.com
```

The floating chat widget streams from `/chat/stream`.
