# LowTicket Ads Studio

Local-first campaign planning and safety controls for low-ticket Meta Ads and Google Ads.

The project uses a draft-first workflow: campaigns are created paused, every live mutation requires a preview and explicit approval, and credentials are never stored in SQLite.

## Status

Current MVP includes:

- offer economics and break-even CPA/ROAS calculations;
- Meta/Google CSV metric import with SQLite persistence;
- deterministic campaign copy and creative briefs without an AI key;
- optional OpenAI-compatible AI adapter for Ollama or BYOK endpoints;
- platform copy-limit validation;
- evidence-based pause/scale recommendations;
- preview, approval-token, budget-ceiling, paused-campaign, and audit safeguards;
- local browser workflow for offer → draft → preview → approval.

Live Meta/Google credentials are intentionally behind provider ports. The included provider is a safe fake for local development; connect official APIs only after adding and testing a real adapter.

## Development

Backend:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload
```

Frontend:

```powershell
cd frontend
npm install
npm run dev
```

Run the verification suite:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
cd frontend
npm test -- --run
npm run build
cd ..
powershell -ExecutionPolicy Bypass -File scripts/smoke.ps1
```

Optional Docker:

```powershell
docker compose up --build
```

The application defaults to deterministic local generation. To use Ollama or another OpenAI-compatible endpoint, copy `.env.example` to `.env`, set `AI_PROVIDER=openai_compatible`, configure `AI_BASE_URL`, `AI_API_KEY`, and `AI_MODEL`, and start Uvicorn with `--env-file .env`.
