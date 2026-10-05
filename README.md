# LowTicket Ads Studio

Local-first campaign planning and safety controls for low-ticket Meta Ads and Google Ads.

The project is being built with a draft-first workflow: campaigns are created paused, every live mutation requires a preview and explicit approval, and credentials are never stored in SQLite.

## Status

Early MVP. The current scaffold includes a FastAPI health endpoint and a Vite/React shell. Provider integrations are intentionally isolated behind adapters and will remain optional during local development.

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
