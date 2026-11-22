# DiagnoVision

DiagnoVision is a desktop-first clinical intelligence dashboard for synthetic healthcare demonstrations. It is a browser application built with React, TypeScript, Vite, Tailwind CSS, TanStack Query, Axios, Recharts, and accessible Radix-style components, backed by Python and FastAPI.

> **Research prototype only.** DiagnoVision is not clinically validated, is not a diagnostic device, and must not be used for real patient care. The bundled demo data and AI outputs are synthetic and simulated.

## What the MVP demonstrates

- Cookie-authenticated doctor sessions with CSRF protection and patient-level access checks.
- Searchable fictional patient records, timelines, observations, and longitudinal charts.
- Manual consultation entry, audio upload, browser `MediaRecorder`, and native WebSocket streaming.
- Deterministic demo transcription and structured clinical extraction with editable doctor approval.
- Immutable, source-referenced clinical analyses and deterministic trend calculations.
- Private document upload and demo OCR/extraction review.
- PostgreSQL/pgvector, Redis, Celery/Beat, and private MinIO services in Docker Compose.
- Responsive browser routes with same-origin API/WebSocket proxying through Nginx.

See [DEMO_GUIDE](docs/DEMO_GUIDE.md) for the walkthrough and [MODEL_LIMITATIONS](docs/MODEL_LIMITATIONS.md) before evaluating any AI output.

## Quick start: full stack

Requirements: Docker Engine with Compose v2 and approximately 4 GB free RAM for the default CPU/demo profile.

```bash
cp .env.example .env
docker compose up --build
```

Open <http://localhost:8080>. The only host-published production-like service is the Nginx gateway. Synthetic demo credentials:

- Email: `doctor@diagnovision.local`
- Password: `DemoPass123!`

For an existing database, apply migrations before use:

```bash
docker compose run --rm backend alembic upgrade head
```

Stop services with `docker compose down`. Add `-v` only when you intentionally want to irreversibly remove local database, queue, and object-storage volumes.

## Local development

The backend supports its documented development database fallback; PostgreSQL is required to exercise pgvector and the full warehouse path.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn app.main:app --app-dir backend --reload --port 8000
```

In a second terminal:

```bash
cd frontend
npm ci
npm run dev
```

Open <http://localhost:5173>. Vite proxies `/api/v1` and WebSocket upgrades to <http://localhost:8000>. Browser microphone access requires `localhost` or HTTPS and explicit consent in the UI.

## Verification commands

```bash
cd backend
ruff check .
pytest

cd ../frontend
npm ci
npm run lint
npm run typecheck
npm run test
npm run build
npm run test:e2e

cd ..
docker compose config
```

CI runs the backend and frontend static checks, tests, and production build. Browser recording still requires manual codec/permission checks in the target browsers; see [DEMO_GUIDE](docs/DEMO_GUIDE.md).

## Configuration

Copy `.env.example` and replace all local-only credentials and secrets. `VITE_*` variables are public build inputs and must never contain keys or clinical information. The default provider is explicitly `mock`; production-like inference never silently falls back when a configured provider fails.

Optional local Ollama service:

```bash
docker compose --profile ollama up --build
```

Download the configured model explicitly with the Ollama CLI/API before selecting it. Faster Whisper, PaddleOCR, and embedding models may download large artifacts; use the deterministic providers for an offline, CPU-only demo.

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [API contract](docs/API_CONTRACT.md)
- [Database schema](docs/DATABASE_SCHEMA.md)
- [AI pipeline](docs/AI_PIPELINE.md)
- [Data warehouse](docs/DATA_WAREHOUSE.md)
- [Security](docs/SECURITY.md)
- [Model limitations](docs/MODEL_LIMITATIONS.md)
- [Demo guide](docs/DEMO_GUIDE.md)
- [Team tasks and delivery status](docs/TEAM_TASKS.md)

## HTTPS

The local gateway is plain HTTP for localhost development. For any non-local deployment, terminate TLS at a trusted reverse proxy or load balancer, redirect HTTP to HTTPS, enable `SECURE_COOKIES=true`, and retain WebSocket upgrade headers. Encryption-at-rest and managed backup key rotation are deployment responsibilities; they are not provided merely by this repository.

