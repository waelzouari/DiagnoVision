# Security and privacy

DiagnoVision contains defense-in-depth controls for a synthetic-data prototype. It is not certified for healthcare privacy regulation and does not by itself provide a compliant production environment.

## Implemented application controls

- Argon2 password verification and short-lived access/rotated refresh JWT cookies.
- HttpOnly, SameSite cookies; `Secure` is mandatory outside localhost.
- Double-submit CSRF tokens, strict allowed-Origin checks, and WebSocket Origin/authentication checks.
- Doctor and patient authorization on every referenced resource.
- Audit events for security-sensitive and clinical approval actions without clinical payload logging.
- Allowlisted upload types, signature/size checks, sanitized names, resource-limited processing, and private object references.
- Restricted CORS and Nginx body limits, no-store authenticated responses, CSP, framing denial, and content-type sniffing protection.
- No secrets or tokens in localStorage, IndexedDB, query strings, or `VITE_*` variables.
- Explicit consent before microphone activation and cleanup of media tracks on stop/unmount.
- AI inputs treated as untrusted content; provider access is bounded and schema validated.

## Deployment responsibilities

Before use outside localhost:

1. Generate unique high-entropy JWT, database, Redis (if network-accessible), and MinIO credentials through a secret manager.
2. Terminate TLS with modern HTTPS/WSS, set `SECURE_COOKIES=true`, and narrow `WEB_ORIGIN`/`ALLOWED_ORIGINS`.
3. Encrypt database, object, volume, and backup storage at rest with managed keys and tested rotation/recovery.
4. Place services in private subnets, restrict egress, patch images, scan dependencies, and collect security-only audit logs.
5. Configure retention/deletion, backup restoration, incident response, availability monitoring, and account provisioning.
6. Perform threat modeling, penetration testing, privacy assessment, and applicable legal/regulatory review.

Docker's internal network is isolation, not encryption at rest. The example passwords are local demo values and must never be reused.

## Logging and telemetry

Logs use request/job IDs, safe error categories, durations, and actor IDs only where necessary. Patient names, transcript text, findings, filenames, tokens, cookies, and object URLs are prohibited. No third-party browser analytics are included.

## Reporting

Do not put vulnerabilities or patient-like data in public issues. Rotate exposed local secrets and recreate affected demo volumes.

