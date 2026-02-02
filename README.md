# NewsroomKit

NewsroomKit is a full-stack app that helps student journalists write ethical, well-sourced articles with transparent claim checking.

## Features (MVP)
- Projects with drafts, sources, and interviews.
- Claim extraction + claim list with heuristic classification.
- Cross-reference engine (keyword overlap + TF-IDF similarity).
- Evidence report with Markdown + JSON exports and copy buttons.
- AI writing tools that only rephrase existing text (no new facts).
- Ethical guardrails checklist and allegation warnings.
- Web search agent mode (real API key or demo mode).
- PWA-ready manifest + service worker for install.

## Tech Stack
- **Frontend**: Next.js + TypeScript
- **Backend**: FastAPI
- **Database**: SQLite (local), Postgres compatible

## Local development

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Environment variables
Create a `.env` in `backend` if needed:
```
DATABASE_URL=sqlite:///./newsroomkit.db
SEARCH_PROVIDER=serpapi # or bing
SEARCH_API_KEY=your-key
STALE_YEARS=5
```

For the frontend, set the backend URL:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Database migrations
```bash
cd backend
alembic upgrade head
```

## Tests
```bash
cd backend
pytest
```

## Deployment

### Frontend (Vercel)
- Set `NEXT_PUBLIC_API_URL` to your API URL.
- Deploy the `frontend` folder.

### Backend (Render/Railway/Fly)
- Set `DATABASE_URL` to your Postgres connection string.
- Run `uvicorn app.main:app --host 0.0.0.0 --port 8000`.

## PWA install
- The app includes `/manifest.json` and a service worker.
- Visit the site in Chrome/Edge/Safari and select **Install**.

## Ethical notes
- Search results are never fabricated. If no API key is provided, the API returns clearly labeled demo results.
- AI writing tools only rephrase existing text and never add new facts.

## Roadmap stubs (non-MVP)
- Credibility signals (domain indicators, press release detection).
- Writing coach & reading level estimator.
- Interview question generator and quote tagging.
- Workflow board and deadline reminders.
- Fact Lock + Cite-or-Flag enforcement.
