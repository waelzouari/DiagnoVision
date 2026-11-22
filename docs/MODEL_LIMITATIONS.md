# Model limitations

DiagnoVision is a research and hackathon prototype for clinical documentation support. It is not clinically validated, regulated, or suitable for autonomous diagnosis, triage, treatment, or patient communication.

## Demo providers

The default mock speech, extraction, analysis, and OCR providers are deterministic fixtures. They do not perform genuine inference and their output is labeled simulated. They exist to demonstrate workflow behavior offline; they are not accuracy evidence.

## Speech recognition

Faster Whisper performance varies with microphone quality, accents, noise, overlapping speech, medical vocabulary, codecs, and language switching. Tunisian Arabic and mixed Arabic/French speech are specifically under-evaluated. Speaker labels must not be treated as confirmed identities. Every transcript requires doctor review against the source audio.

## Extraction and generation

LLMs can omit, distort, over-generalize, mishandle negation/temporality, or follow malicious text embedded in evidence. JSON validation checks shape, not truth. Source references and human approval are mandatory. The system abstains when evidence is insufficient and must not invent missing fields.

## Retrieval

Embedding similarity is not clinical relevance. Retrieval can miss evidence or rank stale context highly. Access filters prevent cross-patient retrieval, but clinicians must inspect returned sources. General reference material is distinct from patient evidence.

## OCR and imaging

OCR is sensitive to scan quality, handwriting, layout, language, and unit typography. Parsed values and ranges require review against the page. No general radiology interpretation is claimed. Optional DICOM support is transport/parsing only unless a separately documented research adapter is installed.

## Predictive modeling

No clinically validated predictive model or performance result is bundled. Deterministic trends describe recorded measurements and do not establish overall recovery, causality, risk, or diagnosis. Any future experimental model must document the legally usable dataset, target population, outcome/time horizon, patient-level splits, preprocessing artifact, discrimination/calibration, provenance, and refusal rules. Synthetic metrics must never be represented as clinical performance.

