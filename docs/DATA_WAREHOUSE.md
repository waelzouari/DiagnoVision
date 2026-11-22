# Data warehouse

The lightweight medallion design shares PostgreSQL with the modular monolith for the MVP while keeping layer contracts explicit. Private files remain in MinIO; rows contain authorized object references, not public URLs.

## Bronze

Append-only source metadata, upload references, raw transcripts, raw OCR, provider/version metadata, and ingestion timestamps. Original clinical values are never discarded.

## Silver

Doctor-approved, schema-validated facts with normalized dates/units, provenance, correction history, and duplicate keys. Unknown values stay null. Idempotency keys prevent the same approved draft or document extraction from being loaded twice.

## Gold

Patient/date/observation dimensions, consultation and observation facts, indicator trends, and model feature snapshots. Gold derives only from approved Silver rows. Patient access continues to apply to analytics queries.

## ETL guarantees

- A stable source/version key makes every transform repeatable and idempotent.
- Duplicate candidates are flagged rather than destructively merged.
- Unit conversion occurs only for known compatible dimensions and retains original values.
- Watermarks use committed approval timestamps, not client clocks.
- Job locking prevents concurrent processing of the same source version.
- Gold refreshes are transactional so readers never see a half-applied version.

For a hackathon-scale workload, SQL views/materialized tables and Celery tasks are sufficient; Kafka, Spark, and a separate warehouse service are intentionally excluded.

