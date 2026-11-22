# Database schema

DiagnoVision uses UUID primary keys, UTC timestamps, foreign keys, and patient/doctor indexes. Core records are FHIR-inspired, not FHIR-compliant.

## Operational tables

- Identity/access: `doctors`, `doctor_settings`, `patients`, `patient_access`.
- Encounters: `consultations`, `recording_consents`, `audio_recordings`, `transcripts`, `transcript_segments`, `clinical_drafts`.
- Approved clinical facts: `symptoms`, `conditions`, `medications`, `allergies`, `observations`.
- Documents: `documents`, `document_extractions`.
- Intelligence: `analysis_runs`, `ai_findings`, `alerts`, `embeddings`.
- Operations/governance: `processing_jobs`, `audit_logs`.

`patient_access` is the authoritative doctor-to-patient mapping. Services must join through it rather than accept ownership supplied by clients. Consultation and document records inherit authorization through their patient.

## Provenance and corrections

Draft and extracted facts retain source kind, source record ID, optional transcript timestamps/page number, original value/unit, normalized value/unit, confidence where applicable, and author/approver timestamps. Corrections append history and audit events rather than overwriting raw Bronze evidence.

## Migrations

Alembic owns schema evolution. Apply before application startup:

```bash
alembic upgrade head
```

PostgreSQL bootstrap enables `vector` and creates `bronze`, `silver`, and `gold` schemas. SQLite is suitable only for lightweight development/tests; it does not exercise pgvector, production locking, or PostgreSQL constraints.

