# Temple & Heritage Information Assistant

A React + TypeScript discovery experience backed by a FastAPI retrieval augmented generation service. Temple catalogue entries and chat citations are grounded in the curated source documents in `backend/data/raw/temple_sources.json`.

## Run on Windows

Open two PowerShell terminals from the repository root.

**Backend terminal**

```powershell
Set-Location .\backend
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

If the virtual environment is not present, create it with `py -3.10 -m venv .venv`, activate it, and install `requirements.txt`. The embedding model is loaded when a chat query needs it; its first use requires the model files to be available locally or a network connection to download them.

**Frontend terminal**

```powershell
Set-Location .\frontend
npm install
npm run dev -- --host 127.0.0.1
```

Vite serves the frontend at `http://127.0.0.1:5173` and proxies `/api` requests to the backend at `http://127.0.0.1:8001`. The backend API is available directly at `http://127.0.0.1:8001`; its interactive API docs are at `/docs`.

Copy `backend/.env.example` to `backend/.env` to configure an OpenAI-compatible provider such as OpenRouter. Keep API keys only in the backend environment. Without a configured key and model, chat remains available in retrieval-only mode.

## API routes

- `GET /api/health`
- `POST /api/chat` — `{ "question": "...", "language": "en", "temple_id": null, "history": [] }` (`history` is optional and limited to four completed turns)
- `GET /api/temples/states` — the national state and union-territory selector list (36 options)
- `GET /api/temples/facets?state=&district=` — catalogue-backed districts and temple choices for the selected location
- `GET /api/temples/?query=&search=&state=&district=&area=&limit=50&offset=0` — case-insensitive substring search over primary and alternate names; `search` and `query` are aliases
- `GET /api/temples/{temple_id}`

The catalogue is `backend/data/catalogue.json`. It currently contains 217 distinct records across 17 states and 76 state/district pairs. The curated document set contains 268 source-attributed knowledge documents and the persistent Chroma collection has 296 chunks. The added ASI inventory records support temple names and listed locations; they do not imply that historical, deity, architectural, or festival details have been verified. At present, 203 catalogue entries are marked `source_listed_needs_review`, 8 UNESCO-supported entries are marked `source_reviewed_needs_review`, and the original 6 remain `curated_unverified`; none are marked verified. State/UT selector options do not imply that the catalogue contains temples in every region. A missing catalogue returns HTTP 503 rather than an empty success response.

## Checks

From `backend`: `python -m pytest -v`

From `frontend`: `npx tsc --noEmit` and `npm run build`

## Collect and index trusted source pages

From `backend/` with `.venv` active, use `python -m app.ingestion collect --source tn-arch`, `python -m app.ingestion validate`, `python -m app.ingestion index --dry-run`, `python -m app.ingestion index`, and `python -m app.ingestion report`. `python -m app.ingestion run` runs collection, validation, and then indexing; add `--dry-run` to preview without writing collection or Chroma data.

Collection is limited to explicit HTTPS URLs in `data/source_registry.json`, honors each host's `robots.txt`, and skips sources until their terms/access review status is set to `approved`. Newly discovered unmatched entries remain in `data/catalogue_candidates.json` for human review. See `backend/README.md` for Windows Task Scheduler setup and source limitations.

The manually reviewed ASI inventory seed can be reapplied idempotently from `backend/` with `python scripts/import_asi_inventory_seed.py`. It uses the official ASI inventory URL as provenance but does not fetch or crawl the source. The ASI registry entry remains disabled and collection remains gated pending operator terms/access review. Run `python -m app.ingestion validate`, then `python -m app.ingestion index --dry-run` before indexing.

## Public deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for the Vercel + Render environment variables, persistent ChromaDB setup, and verified migration procedure. Current local data is 217 catalogue records, 268 curated knowledge documents, and 296 chunks in `backend/data/chroma`.


