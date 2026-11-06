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
  `temple_heritage`, with 557 chunks at the last read-only verification. There is also a separate stale
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
copy until the deployed health endpoint reports the verified current chunk count.

1. From PowerShell, stop any local backend process using the database, then
   create a transfer archive from the **backend** database (not root `data/chroma`):

   ```powershell
   Set-Location D:\GEN-AI\temple-heritage-assistant\backend
   python scripts\migrate_chroma_store.py --source .\data\chroma --target .\migration-preview --expected-count 557 --dry-run
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
     --expected-count 557
   ```

   The target is a new sibling directory on the persistent disk. The script
   stages and validates the copied database before publishing it by rename.
   If the database count has intentionally changed, inspect the source first
   and pass the verified count with `--expected-count`.

4. Set Render's `CHROMA_PERSIST_DIR` to `/var/data/chroma-imported` and restart
   the service. Check `GET /api/health`; it should return
   `"indexed_chunks": 557`. Also verify a known temple query before switching
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

## Embedding memory experiment (optional)

PyTorch remains the default backend for the existing `temple_heritage`
collection. Query vectors must come from the same backend used to index the
collection. Do not set `EMBEDDING_BACKEND=onnx` for production while
`EMBEDDING_INDEX_BACKEND=pytorch`; the application rejects this mismatch. A
different vector space needs a separately re-embedded collection and retrieval
evaluation before cutover.

The service can run `model_quint8_avx2.onnx` through ONNX Runtime without loading
PyTorch during inference. This is experimental, not a deployment recommendation.
It uses the model tokenizer, attention-mask mean pooling, 128-token truncation,
and normalized 384-dimensional vectors. Use a compatible x86 CPU; do not use
ARM or AVX-512-specific artifacts unless the host supports them. Keep
`EMBEDDING_BACKEND` and `EMBEDDING_INDEX_BACKEND` aligned.

From `backend/`, measure fresh-process memory and vector similarity:

```powershell
python scripts\benchmark_embeddings.py --compare --output data\embedding_benchmark_report.json
```

The all-temple ONNX retrieval comparison creates a separate experimental copy
under the OS temporary directory and retains its JSON report. It never writes
to `backend/data/chroma`:

```powershell
python scripts\evaluate_onnx_experiment.py
```

Do not switch the live collection based on embedding cosine similarity alone;
review the retrieval report and run application-level QA. The original
Tokenizers-based full app measured 539.71 MB RSS. An ONNX path using the model's
SentencePiece tokenizer measured 334.06 MB peak RSS in a fresh Windows process,
a 205.65 MB reduction. This is about 178 MB below the nominal 512 MB plan limit
on that host, but is not a Linux/cgroup compatibility result. Docker is not
installed and WSL is unavailable in this environment, so no 512 MB Linux test
was run. Render Free is therefore promising on memory, but not yet demonstrated
safe; validate on Linux under the actual cgroup limit before relying on it. The
current `render.yaml` also assumes a paid persistent disk. See the backup
design below; that storage concern is separate from runtime memory.

For a smaller ONNX deployment, `requirements-onnx.txt` omits PyTorch,
Sentence Transformers, pytest, and scikit-learn. The regular
`requirements.txt` intentionally retains the PyTorch backend and test tooling.
Use the ONNX-only set only for an ONNX-indexed collection and an ONNX backend;
it does not include the PyTorch fallback. The app modules and ONNX API path were
checked for direct imports: `torch`, `sentence_transformers`, and `transformers`
are not imported when using ONNX. ChromaDB remains the largest non-model runtime
dependency. The benchmark confirmed one Uvicorn worker; raising worker count
would duplicate the model and increase RAM.

The current ONNX loader calls `hf_hub_download` for exactly
`sentencepiece.bpe.model` (5,069,051 bytes) and
`onnx/model_quint8_avx2.onnx` (118,453,870 bytes), not `snapshot_download`.
Together they are about 123.5 MB; the host's existing Hub cache contains about
4.38 GB of unique multi-format model blobs accumulated separately, which the
loader does not request. The tokenizer change preserves the 384-dimensional
model, token IDs, max length, attention-mask mean pooling, and L2 normalization.
Exact token-ID equivalence passed for all 403 current knowledge documents plus
20 multilingual and edge-case inputs (423/423). The experimental runtime
benchmark kept ONNX Runtime graph optimization at `all` and one intra-op
thread: graph levels `disable`, `basic`, and `extended`, plus 2 and 4 threads,
changed sampled peak RSS by at most about 1.9 MB and did not justify changing
the defaults. Disabling CPU arena and memory-pattern reuse also showed no
benefit, so those experimental flags were reverted to ONNX Runtime defaults.
An in-place masked-pooling experiment preserved the chat result but measured
334.50 MB peak versus 334.06 MB before it, so that change was also reverted;
there was no demonstrated whole-process saving.
The x86 AVX2 model was used; the deployed
CPU feature set was not checked. Pin `EMBEDDING_REVISION` to the tested model
revision `e8f8c211226b894fcb81acc59f3b34ba3efd5f42` for repeatable downloads.
See the [model's ONNX artifacts](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2/tree/main/onnx).

### Free Docker candidate: bundled ONNX snapshot

`render-free.yaml` is a separate, no-disk Docker candidate. The image contains
the ONNX-indexed `backend/data/chroma_onnx` snapshot. Its manifest checksums
all five persisted Chroma files and records the ONNX backend, model revision,
SentencePiece tokenizer, 384 dimensions, 557 count and sorted chunk-ID digest.
At container startup, `python -m app.bootstrap` validates those checksums and
copies the snapshot to `/tmp/temple-chroma-runtime`; Chroma uses that temporary
copy because its SQLite runtime requires a writable directory. The bundled
`/app/data` source remains root-owned and read-only. The Docker verification
script also asks Docker for a read-only root filesystem and a bounded `/tmp`.
Changes made to the runtime copy disappear on restart; this service must not
run ingestion or index writes.

The ONNX loader calls `hf_hub_download` for only the configured tokenizer and
ONNX model files. It does not call `snapshot_download`. With the pinned model
revision, the files previously measured were 5,069,051 bytes and 118,453,870
bytes. Because Render Free has ephemeral storage, a cold instance may fetch
these files again into `/tmp/huggingface`. This was not measured on Render.

The selected model artifact is named `model_quint8_avx2.onnx`. Linux startup
now checks the visible x86 CPU flags and fails before download if AVX2 is not
confirmed. Render's documented Free resource limits do not identify a CPU
model or guarantee AVX2, so compatibility remains unverified until a real
Render instance or equivalent Linux host confirms `/proc/cpuinfo` and passes
the container test. Do not select a non-AVX2 artifact without a separately
validated model file and retrieval equivalence run.

To restore a private ONNX backup locally before building an image, use a new
target and keep the original ONNX and PyTorch directories untouched:

```powershell
Set-Location D:\GEN-AI\temple-heritage-assistant\backend
$backup = Join-Path $env:LOCALAPPDATA 'TempleHeritageBackups'
python scripts\chroma_snapshot.py restore `
  --archive (Join-Path $backup 'chroma_onnx_final.zip') `
  --manifest (Join-Path $backup 'chroma_onnx_final.zip.manifest.json') `
  --target .\data\chroma_onnx_restore_candidate `
  --collection temple_heritage --expected-count 557 --backend onnx
```

Review the restore JSON for `archive_sha256_verified: true`, count `557`,
dimension `384`, and the expected IDs digest before swapping anything. Preserve
the existing `data\chroma_onnx` as a timestamped rollback directory, move the
validated candidate into its place, regenerate
`data\chroma_onnx_snapshot_manifest.json` with
`python scripts\create_chroma_snapshot_manifest.py`, then run the restore and
Docker checks again. The original PyTorch collection is a distinct source and
must not be used as an ONNX backup or query index.

The deployment test command is
`powershell -ExecutionPolicy Bypass -File backend\scripts\test_linux_512mb.ps1`.
It builds and starts a single worker with a 512 MiB memory+swap ceiling, a
read-only root filesystem, bounded temporary storage, and retrieval-only chat
requests. Docker is unavailable in the current verification environment, so
this command still needs to pass on a Linux Docker host before deployment.

### Full application memory and retrieval check

The benchmark ran a fresh single-worker Uvicorn process with FastAPI, ChromaDB,
the ONNX model, a real retrieval query, and a real `/api/chat` request (LLM
generation disabled). Peak sampled RSS was 334.06 MB: 23.09 MB after Python
start, 128.53 MB after FastAPI/Chroma initialization, 329.12 MB after ONNX and
SentencePiece load, 330.62 MB after retrieval, and 334.05 MB after the API call.
The chat returned HTTP 200 with a source citation. `torch`,
`sentence_transformers`, `transformers`, and the Hugging Face `tokenizers`
runtime were absent from that process. The original `backend/data/chroma`
collection remained at 557 chunks with the same IDs; all memory and ONNX
retrieval checks used a separate temporary ONNX-indexed copy.

After fixing the unsupported heritage-context gate, local retrieval evaluation
reported 217/217 temple-name checks, 392/392 evidence-available topic checks,
4,016/4,016 citation metadata checks, 217/217 follow-up checks, and 30/30
similar-name checks passed. Potential unrelated context was retained for 0 of
1,127 unsupported-category tests. This tests local retrieval/context admission,
not live LLM answer correctness; no OpenRouter request was made. The full
backend suite passed 106 tests. TypeScript checking and the Vite production
build also passed. The 512 MB conclusion remains provisional until the same
app and data are exercised in a real Linux 512 MB cgroup.

## Remote object-storage backup design (not implemented)

The local `backend/data/chroma` directory measured about 6.55 MB at this
checkpoint. Cloudflare R2 Standard currently includes 10 GB-month storage, 1M
Class A operations and 10M Class B operations monthly, with no R2 egress fee;
usage above the included tier is billable. This is ample for a few timestamped
Chroma snapshots at the current size, but not a guarantee of zero cost if the
account's total R2 use exceeds its free allowance. See [R2 pricing](https://developers.cloudflare.com/r2/pricing/).

Recommended backup procedure:

1. Stop the backend and all index/ingestion writers. Do not zip a live Chroma
   directory: the SQLite database and HNSW files need to form one consistent
   snapshot.
2. Archive the *entire* selected persistence directory under a timestamped,
   never-overwritten object key. Include a manifest with archive SHA-256,
   collection name, chunk count, dimension, embedding backend/model and
   revision. The current original collection is a legacy PyTorch collection;
   do not label it ONNX.
3. Upload to a private R2 Standard bucket using bucket-scoped S3 credentials
   and keep credentials only in operator secrets. R2's S3 API accepts scoped
   Access Key/Secret credentials; see [R2 S3 setup](https://developers.cloudflare.com/r2/get-started/s3/).
4. Restore to a new staging directory, verify SHA-256 before extraction, then
   open the collection read-only and check the expected count and sample IDs
   before changing `CHROMA_PERSIST_DIR`. Keep the previous directory as a
   rollback copy until retrieval checks pass.

Example PowerShell archive and upload commands (run only after stopping the
backend; keep credentials out of command history):

```powershell
Set-Location D:\GEN-AI\temple-heritage-assistant\backend
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$archive = ".\chroma-$stamp.zip"
Compress-Archive -Path .\data\chroma\* -DestinationPath $archive
Get-FileHash -Algorithm SHA256 $archive
aws s3 cp $archive "s3://<private-bucket>/temple-heritage/chroma-$stamp.zip" `
  --endpoint-url "https://<account-id>.r2.cloudflarestorage.com" --region auto
```

To restore, download the selected timestamped object, compare its SHA-256 with
the manifest, extract to a *new* sibling directory, and validate it before
pointing the service at it. Never download a PyTorch snapshot and start the
ONNX backend against it; the embedding spaces are incompatible. A future Render
Free bootstrap would have to download the vetted archive to ephemeral storage
on every cold start and select the matching backend. Render says Free services
spin down after 15 minutes idle, lose local files, and cannot attach persistent
disks. The R2 restore download also counts as Render outbound service traffic;
the Hobby workspace currently includes 5 GB shared monthly, and free services
can be suspended after the included bandwidth is exhausted. Since the model
cache is also lost on spin-down, its 123.5 MB download repeats at cold starts,
in addition to the Chroma archive and normal API responses. See [Render Free
limitations](https://render.com/docs/free) and [outbound
bandwidth](https://render.com/docs/outbound-bandwidth).

No R2 bucket, token, upload integration, or remote backup was created. A local
integrity-checked ZIP/manifest backup and restore utility, with private local
backup copies, is implemented below. Remote free-tier pricing and no-card
eligibility have not been relied on.

## Render Free Docker profile (prepared, not deployed)

The existing `render.yaml` above attaches a persistent disk and uses the
PyTorch requirements; it is **not** a no-billing Render Free configuration.
The separate `render-free.yaml` defines a Docker Free service with no disk. It
expects the independently indexed ONNX snapshot at `backend/data/chroma_onnx`.
The image includes that static 557-chunk snapshot and checks its count before
serving. The production app uses the collection for retrieval/discovery only;
do not run ingestion or indexing inside the service. Future knowledge-base
updates require a newly verified snapshot and image build.

`backend/Dockerfile` installs `requirements-onnx.txt`, copies only the app,
catalogue and ONNX Chroma snapshot, pins the tested model revision, warms ONNX
before health succeeds, and runs one Uvicorn worker. The ONNX requirements
omit PyTorch, Sentence Transformers, Transformers, scikit-learn and pytest.
ChromaDB installs `tokenizers` transitively, but the ONNX code path does not
import it. `EXPECTED_INDEXED_CHUNKS=557` makes the app fail startup if the image
contains an empty or incomplete collection.

Render Free has no persistent disk; writable filesystem changes are lost on
restart/spin-down. Bundling the immutable snapshot in the image avoids relying
on a paid object store, but does not preserve runtime DB writes. The service
must remain read-only with respect to the knowledge index. Render also
describes Free as a testing/hobby plan rather than production. No Linux 512 MB
cgroup run was possible here because Docker is absent and WSL is not installed.
The measured Windows peak (334.06 MB) is not a substitute for Linux testing.

### Run the Docker 512 MiB verification in Windows PowerShell

After installing and starting Docker Desktop with Linux containers, run from
the repository root:

```powershell
Set-Location D:\GEN-AI\temple-heritage-assistant
.\backend\scripts\test_linux_512mb.ps1
```

The script builds the image and starts one Uvicorn worker with a 512 MiB memory
and swap limit. It waits for `/api/health` after ONNX warmup, sends two chat
requests with OpenRouter disabled, and prints process RSS, cgroup current/peak
memory, memory events and Docker's OOM status. It leaves the container running
for inspection; remove it with the command printed by the script. Until this
test runs on a Linux container, do not report Linux/Render memory verification
as passed.

### Render settings

Select `render-free.yaml` as the Blueprint file. Confirm the service plan is
`free` and no disk is attached. Set `CORS_ORIGINS` to the exact Vercel origin,
such as `https://your-project.vercel.app`. Set `LLM_API_KEY` and `LLM_MODEL` in
Render's private environment settings only if generation is available; retrieval
works without them. Never place the OpenRouter key in a `VITE_*` variable.

The model's two pinned files are downloaded at startup if absent from the
ephemeral cache. A Render restart/spin-down may download them again. The app
does not re-index on startup. The health endpoint is `/api/health` and the
expected count is 557.

### Vercel frontend

Set Vercel Root Directory to `frontend`, Framework Preset to Vite, Build Command
to `npm run build`, and Output Directory to `dist`. Set the public, non-secret
`VITE_API_BASE_URL` to the Render origin, for example
`https://temple-heritage-api-free.onrender.com` (no `/api` suffix; the client
adds it). Add that exact Vercel site origin to Render `CORS_ORIGINS`. Rebuild
the frontend after setting its API URL. `frontend/vercel.json` provides the SPA
route fallback. Vite-prefixed values are embedded in public assets.

### ONNX collection migration and backup/restore

Migration completed locally to `backend/data/chroma_onnx`. The original
`backend/data/chroma` remains PyTorch-indexed and is not used by the ONNX app.
The migration report records all 557 unique chunk IDs, text and metadata
preserved, source URLs preserved, 384 dimensions, normalized vectors, and no
source modification. Retrieval evaluation on this exact persisted collection
passed 217/217 temple-name checks, 392/392 evidence-backed topic checks,
4,016/4,016 citation metadata checks, 217/217 follow-up checks, 30/30
similar-name checks, and 0/1,127 unsupported-context leaks. These are local
retrieval checks, not generated-answer checks; no OpenRouter request was made.

`backend/scripts/chroma_snapshot.py` writes a ZIP and a separate SHA-256
manifest. The manifest identifies collection, count, embedding backend/model,
dimension and a digest of all chunk IDs. Restore validates the archive checksum,
collection and vectors, then publishes only to a new target after verification.
Stop the API and all writers before backup. Keep both files in an
access-controlled private location outside the public frontend and repository.
No cloud bucket, paid service, or credentials were created.

PowerShell commands from `backend/`:

```powershell
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
python scripts\chroma_snapshot.py backup `
  --source data\chroma_onnx `
  --archive "data\backups\chroma_onnx-$stamp.zip" `
  --collection temple_heritage `
  --backend onnx `
  --model-revision e8f8c211226b894fcb81acc59f3b34ba3efd5f42 `
  --embedding-artifact model_quint8_avx2.onnx `
  --tokenizer sentencepiece `
  --max-seq-length 128

python scripts\chroma_snapshot.py restore `
  --archive "data\backups\chroma_onnx-$stamp.zip" `
  --manifest "data\backups\chroma_onnx-$stamp.zip.manifest.json" `
  --target data\chroma_onnx-restore `
  --collection temple_heritage `
  --expected-count 557 `
  --backend onnx
```

The backup/restore path was tested into a separate local directory: SHA-256
matched; the restored collection had 557 chunks, 384 dimensions, the ONNX
marker and the same chunk-ID digest. That verification copy is retained as an
ignored local validation copy, is not copied into
the Docker image, and is not the production collection. Local private copies
of both PyTorch source and ONNX snapshot backup pairs were also written to
`%LOCALAPPDATA%\TempleHeritageBackups`; keep that directory protected by the
Windows account ACL and do not upload it publicly. Never restore over the
original PyTorch directory.

## Local verification commands

From `backend/`:

```powershell
python -m py_compile app\main.py app\config.py app\services\embedding_service.py app\services\retrieval_service.py scripts\build_onnx_collection.py scripts\chroma_snapshot.py
python -m pytest -q
```

From `frontend/`:

```powershell
npx tsc --noEmit
npm run build
```
