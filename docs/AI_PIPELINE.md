# AI pipeline

All inputs are untrusted evidence. Transcript text and document content are data, never instructions. Providers receive bounded content and schema-constrained tasks; they do not receive database credentials or unrestricted query access.

## Speech

The `SpeechRecognitionProvider` contract accepts an authorized private object and returns language metadata plus timestamped segments. Demo mode uses deterministic fixtures. The production adapter is intended for Faster Whisper with configurable model, CPU/GPU device, compute type, language, and VAD. Requests enqueue work rather than blocking FastAPI.

Original transcripts are immutable Bronze evidence. Corrections are stored separately and remain traceable. English and French are expected to perform better than Tunisian Arabic; dialect, code-switching, speaker attribution, silence, and clinical vocabulary require human review.

## Structured extraction

The extraction provider produces a Pydantic-validated object containing complaints, positive and negated symptoms, history, explicit diagnoses, medicines/doses, allergies, vitals/labs, recommendations, follow-up, and missing information. Every fact needs a source reference. Unknown fields remain null; the system must not infer a dose, diagnosis, date, or unit.

Extracted content remains an AI draft until doctor approval. Approval normalizes supported units/dates, writes Silver facts, records corrections and provenance, and emits an audit event.

## Clinical analysis and RAG

Deterministic trend calculations precede generation. Retrieval is filtered by authenticated doctor and exact patient before similarity search. Patient evidence and permitted general references are separated, and source IDs are returned with each assertion. Insufficient evidence yields `insufficient_data` or an abstention.

Analyses are immutable versions containing model/provider version, references, limitations, uncertainty, and review state. They may surface evidence-supported items for physician review, but never definitive new diagnoses, treatment prescriptions, disease probabilities, or automatic clinical-record changes.

## Document extraction

PDF embedded text is preferred. Scans/images may pass through resource-limited OpenCV preprocessing and PaddleOCR. Page number, original text/value/unit/range, provider version, and edits are preserved. The module recognizes documents; it does not claim general radiology interpretation.

## Failure behavior

Provider selection is explicit. A failing real provider returns a visible failed job and is never silently replaced with mock output. Demo output is labeled simulated in persisted records and UI.

