# Architecture

DiagnoVision is a modular monorepo. The React single-page application is the sole user interface; no Flutter, mobile-native, or desktop-native target exists.

```text
Browser
  | HTTPS/WSS, secure cookies, CSRF header
  v
Nginx gateway :8080
  |-- static Vite bundle + SPA fallback
  `-- /api/v1 + WebSocket upgrade --> FastAPI
                                      |-- SQLAlchemy --> PostgreSQL + pgvector
                                      |-- jobs -------> Redis --> Celery workers
                                      |-- schedules --> Celery Beat
                                      `-- objects ----> private MinIO bucket
```

## Repository boundaries

- `frontend/`: feature-first React application, browser recording/WebSocket hooks, typed API repositories, tests, and production image.
- `backend/`: FastAPI controllers, schemas, domain services, repositories, SQLAlchemy models, migrations, provider adapters, and workers.
- `ml/`: optional research interfaces and reproducible model artifacts; absence of a predictive model must not disable the application.
- `infrastructure/`: Nginx, PostgreSQL bootstrap, and private object-storage bootstrap.
- `docs/`: contracts, safety controls, limitations, and operator guidance.
- `.github/workflows/`: automated checks.

## Architectural contracts

1. All browser traffic uses relative `/api/v1` paths; no credential is placed in a URL or browser storage.
2. Access and refresh JWTs are short-lived/rotated HttpOnly cookies. State-changing calls require a matching CSRF token and allowed Origin.
3. Patient authorization is enforced in backend repositories/services for every patient, consultation, socket, document, and analysis reference.
4. Long-running work returns `202 Accepted` plus a processing-job ID; the UI polls with TanStack Query until a terminal state.
5. Raw material enters Bronze, only doctor-approved facts enter Silver, and Gold analytics derives only from Silver.
6. AI providers implement replaceable interfaces and produce validated, source-referenced structures. Provider failures remain visible.
7. Clinical drafts never mutate approved records without an explicit doctor approval action and audit event.

## Runtime profiles

The default `DEMO_MODE=true` profile is deterministic, CPU-compatible, and clearly labels simulated output. PostgreSQL, Redis, and MinIO are isolated on an internal Docker network; only Nginx publishes a host port. The optional `ollama` profile is not required for the core workflow.

The development workflow exposes Vite on 5173 and FastAPI on 8000. It is not a production network topology.

