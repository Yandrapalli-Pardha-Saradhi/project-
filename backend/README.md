# Temple & Heritage Information Assistant — Backend

Local RAG (Retrieval-Augmented Generation) backend for Indian temple and heritage
information. It ingests curated documents, retrieves relevant passages, optionally
generates an answer using a configurable LLM provider, and returns citations linked
to real source URLs.

The React + TypeScript frontend lives in the sibling `frontend/` directory. See the repository root README for Windows startup instructions.

## Technology

- Python 3.10.11 (pinned for local and Render deployment compatibility)
- FastAPI
- ChromaDB with persistent local storage (`data/chroma`)
- Sentence Transformers (`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`)
- OpenAI-compatible chat completions client (supports OpenRouter via `LLM_BASE_URL`)
- Pydantic Settings
- pytest

## Repository layout (backend/)

```
app/
  main.py            # FastAPI app, CORS, GET /api/health
  config.py          # Pydantic Settings (env + .env)
  schemas/chat.py    # Chat request/response schemas
  services/
    embedding_service.py   # Sentence-Transformers embeddings
    retrieval_service.py   # ChromaDB vector search
    llm_service.py         # OpenAI-compatible chat client
    rag_service.py         # RAG orchestration + citation mapping
    collection_service.py  # Allowlisted, robots-aware public HTML collection
    ingestion_service.py   # Validation, chunking, incremental Chroma updates
  routes/chat.py     # POST /api/chat
  routes/temples.py  # Temple discovery API
  ingestion.py       # collect/validate/index/run/report CLI
data/catalogue.json # Source-backed temple catalogue
data/
  source_registry.json    # Explicit source URLs and collection policies
  raw/temple_sources.json   # Curated dataset (Brihadeeswarar, Shore, Konark)
  collected/               # Incremental collector output and state
  chroma/             # Persistent ChromaDB storage (created on ingestion)
scripts/
  ingest_documents.py # Backward-compatible ingestion CLI
tests/
  test_rag.py         # pytest suite
requirements.txt
.env.example          # Configuration template (copy to .env)
.gitignore
```

## Configuration

Copy `.env.example` to `.env` and adjust:

```bash
cp .env.example .env
```

Key settings:

- `LLM_BASE_URL` — base URL of an OpenAI-compatible chat API (default OpenRouter).
- `LLM_API_KEY` — API key. **Never committed to source control** (`.env` is
  ignored by git). Never logged or returned by the API.
- `LLM_MODEL` — model name.
- If `LLM_API_KEY`/`LLM_MODEL` are unset, the backend runs in **retrieval-only
  mode**: it still returns relevant evidence with citations, but no generated
  answer is produced and `generation_disabled` is `true`.
- `CORS_ORIGINS` — comma-separated allowed origins. Unrestricted CORS (`*`)
  is only tolerated in debug mode; production must list explicit origins.
- `RELEVANCE_THRESHOLD` — cosine-distance threshold (default 0.7). Results with
  distance above it are treated as insufficient evidence.

## Collection and indexing

Run from `backend/` with the project virtual environment active:

```bash
python -m app.ingestion collect --source tn-arch
python -m app.ingestion validate
python -m app.ingestion index --dry-run
python -m app.ingestion index
python -m app.ingestion run --dry-run
python -m app.ingestion report
```

`run` collects, validates, then indexes only when validation passes. Collection writes to `data/collected/temple_sources.json`; curated `data/raw/temple_sources.json` remains separate. The collector uses only explicit HTTPS allowlisted URLs, checks each host's `robots.txt`, applies a per-domain delay and retries, caps response size, and accepts HTML only. It does not execute JavaScript or follow arbitrary links. ETag, Last-Modified and content hashes support incremental collection. Sources whose `terms_review_status` is not `approved` are skipped. Review source terms and access policy before changing that field; HR&CE is disabled pending review of its interactive search interface.

Unmatched temple listings are written to `data/catalogue_candidates.json` with `needs_review`; they are not published as verified catalogue records. Exact matches can add separately marked `collected_sources` links to existing catalogue entries. Failed URLs retain prior page data and do not block successful sources. Collection, validation, and index reports are separate; `report` writes an aggregate `data/ingestion_report.json`. Stale Chroma chunks are deleted only after inputs validate and all required embeddings and upserts succeed. Chunk hashes include the configured embedding model; provenance-only changes use metadata updates without re-embedding. A dry-run index does not load the model or mutate Chroma. Legacy chunks with matching stored text are classified for a one-time metadata backfill, also without re-embedding.

The original `python scripts/ingest_documents.py` command remains as a backward-compatible index command.

### Optional Windows Task Scheduler setup

After reviewing source policies and marking the relevant source entries approved, create a scheduled task with:

- Program: `D:\GEN-AI\temple-heritage-assistant\backend\.venv\Scripts\python.exe`
- Arguments: `-m app.ingestion run`
- Start in: `D:\GEN-AI\temple-heritage-assistant\backend`

Set **If the task is already running** to **Do not start a new instance**. Review Task Scheduler history and `data/ingestion_report.json` after runs. Collection is never triggered by chat requests.

First run downloads the sentence-transformers model (~230 MB), so network access
is needed once.

## 2. Start the server

From the `backend/` directory:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

Then:

- `GET http://127.0.0.1:8001/api/health`
- `POST http://127.0.0.1:8001/api/chat` with JSON body `{"question": "...", "language": "en", "temple_id": null}`

Supported languages: `en` (English), `te` (Telugu), `ta` (Tamil), `hi` (Hindi).

## 3. API

### GET /api/health

Returns service status, generation enabled flag, collection name, and indexed
chunk count. No secrets are exposed.

### POST /api/chat

Request:

```json
{
  "question": "Who built the Brihadisvara Temple?",
  "language": "en",
  "temple_id": "brihadeeswarar",
  "history": [
    {"role": "user", "content": "What is the temple?"},
    {"role": "assistant", "content": "It is a Chola temple.", "context_temple_id": "brihadeeswarar"}
  ]
}
```

`history` is optional and contains up to eight messages from completed turns, alternating user and assistant. Each message is limited to 1,000 characters. Keep it within one chat session. Responses include `context_temple_id` when a temple has been resolved for the current conversation.

Response:

```json
{
  "answer": "...",
  "citations": [
    {
      "source_id": "brihadeeswarar_001",
      "source_title": "Great Living Chola Temples",
      "source_url": "https://whc.unesco.org/en/list/250/",
      "publisher": "UNESCO World Heritage Centre",
      "excerpt": "..."
    }
  ],
  "language": "en",
  "insufficient_evidence": false,
  "generation_disabled": false
}
```

Citation URLs and titles always come from stored source metadata; the model is
not allowed to invent them. If no relevant evidence passes the relevance
threshold, `insufficient_evidence` is `true` and the answer says so.

### Temple discovery

- `GET /api/temples/states` returns the national state and union-territory selector options (28 states and 8 UTs); it does not claim each region has catalogue entries.
- `GET /api/temples/facets?state=&district=` returns only districts and temple options supported by catalogue records.
- `GET /api/temples/?query=&search=&state=&district=&area=&limit=50&offset=0` lists and filters entries. Search is case-insensitive, partial, and includes supported alternate names; `search` and `query` are aliases.
- `GET /api/temples/{temple_id}` returns a full entry or HTTP 404 when it is unknown.

The current catalogue contains 217 distinct records across 17 states and 76 state/district pairs. `data/raw/temple_sources.json` contains 268 source-attributed documents, indexed as 296 persistent Chroma chunks. Batch 1 and Batch 2 additions remain pending human review; inventory-only entries support listed names and locations and do not establish other historical, deity, architectural, or festival claims. No catalogue entry is marked verified. State and district availability reflects data represented in the catalogue; the state selector may list regions without temple records. Invalid or missing catalogue data is logged and reported as HTTP 503.

The ASI subset is maintained by the deterministic manual seed `python scripts/import_asi_inventory_seed.py`. It does not perform network collection. The `asi-cpm-inventory` registry entry is disabled until an operator completes source terms/access review. Validate and preview indexing before making a change to Chroma:

```powershell
python -m app.ingestion validate
python -m app.ingestion index --dry-run
python -m app.ingestion index
```

## 4. Tests

From the `backend/` directory:

```bash
pytest
```

Tests use fakes for embeddings and the LLM client, so they require neither an
API key nor live network access. They cover request validation, retrieval from
an indexed test collection, citation mapping to stored URLs, rejection of
hallucinated citation IDs, insufficient-evidence behavior, and retrieval-only
mode.

## Limitations

- Python 3.10.11 is pinned by `.python-version` and the Render configuration.
- The embedding model is loaded lazily on first retrieval/chat use. It needs
  network access to download on first use unless its Hugging Face cache exists;
  configure `HF_HOME` on persistent storage in deployment.
- RAG reduces but does not eliminate hallucination risk; when evidence is
  insufficient, the system explicitly says so rather than guessing.
- UNESCO, Tamil Nadu Archaeology and Tamil Nadu district pages have explicit URLs and supported HTML connectors; live collection remains gated on operator terms review and robots permission. Tamil Nadu Archaeology's listing has a structured table parser. HR&CE is configured but disabled until an approved static connector is available. No applicable bulk API or feed was confirmed; coverage is not exhaustive.
- New records and sources remain pending human review and are not considered verified merely because they were downloaded.
- Citation parsing expects the LLM to return JSON; a keyword fallback handles
  other formats.
