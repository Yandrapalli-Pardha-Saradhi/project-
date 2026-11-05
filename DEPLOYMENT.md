# Public deployment: Vercel + Render

This repository uses a Vite static frontend and a FastAPI backend. Deploy the
`frontend/` directory as a Vercel project and the `backend/` directory as a
Render Python web service. No deployment has been performed from this workspace.

## Audit findings

- The frontend already calls relative `/api` paths. There was no production
  localhost URL in the API client; the `127.0.0.1:8001` URL is only Vite's
  local development proxy. The client now uses `VITE_API_BASE_URL` when set
  and retains the local proxy behavior when it is unset.
- FastAPI already reads `CORS_ORIGINS`, `CHROMA_PERSIST_DIR`, `COLLECTION_NAME`,
  `EMBEDDING_MODEL`, `LLM_BASE_URL`, `LLM_API_KEY`, and `LLM_MODEL` from its
  existing Pydantic Settings configuration. Production CORS must list the
  exact Vercel origin(s); wildcard CORS is not enabled by this guide.
- The active local database is `backend/data/chroma`, collection
  `temple_heritage`, with 296 chunks. There is also a separate stale
  `data/chroma` directory at repository root containing an empty collection.
  **Do not use that root-level directory as the migration source.**
- Backend startup opens the persistent collection with `get_or_create`; it
  does not clear data, recreate a non-empty collection, or run ingestion.
  Embeddings load lazily once per process. Indexing is a separate CLI action.
- Requirements were unpinned. They now pin the direct packages to versions
  present in the working Python 3.10.11 environment. Render is pinned to the
  same Python version so a future platform default cannot silently change it.

## Render setup

The root `render.yaml` defines the service, health check, environment, and a
persistent disk mounted at `/var/data`. Review it before creating the Blueprint.
The Render service root is `backend/`.

Build command:

```text
pip install -r requirements.txt
```

Start command:

```text
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Set these Render environment variables:

| Variable | Value |
|---|---|
| `PYTHON_VERSION` | `3.10.11` (also set by `.python-version` and `render.yaml`) |
| `CHROMA_PERSIST_DIR` | `/var/data/chroma-imported` during migration; retain this path after cutover |
| `HF_HOME` | `/var/data/huggingface` so downloaded model files survive restarts |
| `CORS_ORIGINS` | Comma-separated exact origins, e.g. `https://your-app.vercel.app,https://your-custom-domain.example` |
| `LLM_API_KEY` | OpenRouter key, set as a secret in Render only |
| `LLM_MODEL` | OpenRouter model identifier |
| `LLM_BASE_URL` | Optional; defaults to `https://openrouter.ai/api/v1` |
| `COLLECTION_NAME` | Optional; defaults to `temple_heritage` |
| `EMBEDDING_MODEL` | Optional; defaults to `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` |

Do not create any `VITE_*` secret. Vite embeds those values in public frontend
assets. `LLM_API_KEY` must exist only in Render's backend environment.

The first model use needs network access to download the embedding model unless
it is already cached. `HF_HOME` places that cache on the persistent disk so
ordinary restarts do not download it again. Model loading is lazy, so the first
retrieval/chat request after an empty cache can take longer. The app does not
re-index on startup.

## Migrate the existing Chroma collection

This copies the Chroma persistence directory and verifies the collection name,
all chunk IDs, documents, metadata, and embedding vectors. It refuses to
overwrite an existing target. Keep the source database untouched as a rollback
copy until the deployed health endpoint reports 296 indexed chunks.

1. From PowerShell, stop any local backend process using the database, then
   create a transfer archive from the **backend** database (not root `data/chroma`):

   ```powershell
   Set-Location D:\GEN-AI\temple-heritage-assistant\backend
   python scripts\migrate_chroma_store.py --source .\data\chroma --target .\migration-preview --expected-count 296 --dry-run
   Compress-Archive -Path .\data\chroma\* -DestinationPath .\chroma-migration.zip
   ```

2. Create the Render web service with its `/var/data` disk. Use the Render
   Dashboard Shell or SCP/SFTP to place `chroma-migration.zip` under the
   mounted disk, for example `/var/data/chroma-migration.zip`. Render supports
   SCP with its documented `-s` mode. Do not put the archive in the repository
   or a public URL.

3. In the Render Shell, extract the archive into a fresh source directory, then
   run the copy/verification tool from the deployed backend root:

   ```sh
   mkdir -p /var/data/chroma-upload
   unzip -q /var/data/chroma-migration.zip -d /var/data/chroma-upload
   python scripts/migrate_chroma_store.py \
     --source /var/data/chroma-upload \
     --target /var/data/chroma-imported \
     --expected-count 296
   ```

   The target is a new sibling directory on the persistent disk. The script
   stages and validates the copied database before publishing it by rename.
   If the database count has intentionally changed, inspect the source first
   and pass the verified count with `--expected-count`.

4. Set Render's `CHROMA_PERSIST_DIR` to `/var/data/chroma-imported` and restart
   the service. Check `GET /api/health`; it should return
   `"indexed_chunks": 296`. Also verify a known temple query before switching
   production traffic. Keep the original local copy and the uploaded archive
   until these checks pass.

The migration utility's `--dry-run` reads and validates the source without
copying or writing. Do not run normal ingestion/indexing during migration.

## Vercel setup

Create a Vercel project with **Root Directory** `frontend/`, framework preset
**Vite**, build command `npm run build`, and output directory `dist`. The added
`frontend/vercel.json` configures these build settings and rewrites direct
client-side routes to the Vite entry page.

Set this Vercel environment variable for Production and Preview as appropriate:

```text
VITE_API_BASE_URL=https://<your-render-service>.onrender.com
```

Use the backend origin only; do not append `/api`. The API client appends that
prefix. Add each stable deployed frontend origin to Render's `CORS_ORIGINS`,
then redeploy the backend after changing it. For local Vite development, leave
`VITE_API_BASE_URL` unset to use the existing proxy to `127.0.0.1:8001`.

## Operational limits and blockers

- Render persistent disks are available only on paid services, attach to one
  instance, and prevent scaling that service horizontally. This embedded
  Chroma deployment must run as one backend instance; it is not a multi-instance
  or high-availability vector database configuration.
- Disk-backed deploys have a short service interruption during instance swaps.
- The production Vercel domain and OpenRouter model were not supplied. Set their
  actual values in the respective dashboards before deployment.
- The source database is not committed to the repository. The manual migration
  above is required; the Render service must not be considered ready until its
  health endpoint reports the expected nonzero count.
- No deployment or live hosted URL was tested from this workspace.

## Local verification commands

From `backend/`:

```powershell
python -m py_compile app\main.py app\config.py app\services\retrieval_service.py scripts\migrate_chroma_store.py
python -m pytest -q
```

From `frontend/`:

```powershell
npx tsc --noEmit
npm run build
```
