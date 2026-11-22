# Team tasks and delivery status

This file records scope and dependencies; test results in the final delivery report are authoritative.

## P0 vertical slice

| Workstream | Contract | Depends on |
| --- | --- | --- |
| Backend/platform | session security, patient access, OpenAPI schemas, jobs | database/migrations |
| Patient UI | guarded routes, CRUD, timeline, charts | auth + patient APIs |
| Consultation | consent, upload/recording, transcript, extraction, approval | private objects + jobs |
| Intelligence | trends, analysis versions, source references | approved Silver facts |
| Documents | private upload, OCR extraction, approval | object storage + jobs |
| Operations | Nginx, Compose, CI, tests, docs | stable service entrypoints |

## P1/P2 boundaries

Real Faster Whisper, PaddleOCR, sentence-transformer/pgvector retrieval, and Ollama adapters are optional runtime capabilities; deterministic providers keep P0 reproducible. Experimental prediction and medical-image classification must remain disabled unless a licensed dataset/model and documented validation are available.

## Definition of done

- Browser accepts synthetic login and completes the clinical vertical slice.
- All resource access is backend-authorized and mutating calls are CSRF-protected.
- Approved facts—not AI drafts—feed history and analytics.
- Direct route refresh works behind Nginx; WebSockets upgrade through the same origin.
- Backend/frontend tests, type checks, build, Compose validation, and Playwright smoke results are reported exactly, including failures or unavailable tooling.

