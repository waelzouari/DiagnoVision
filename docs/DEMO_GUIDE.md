# Synthetic demo guide

Everything in this walkthrough is fictional. Do not enter real patient information.

## Start

```bash
cp .env.example .env
docker compose up --build
```

Open <http://localhost:8080> and sign in with:

- `doctor@diagnovision.local`
- `DemoPass123!`

The interface should display a persistent research-prototype notice and simulated badges on mock AI output.

## End-to-end walkthrough

1. Open **Patients** and inspect the five synthetic profiles: improving, worsening, stable, incomplete, and conflicting-history examples.
2. Create another fictional patient and confirm it appears in search and overview counts.
3. Open a patient timeline and observations chart; use the adjacent textual values as the accessible chart equivalent.
4. Start a consultation, record consent, then choose manual entry, upload a synthetic audio fixture, or explicitly permit the microphone.
5. Stop and preview browser audio before upload. Start transcription and observe the job transition to a terminal state.
6. Review/edit the transcript, request structured extraction, inspect source references and negated symptoms, then approve the draft.
7. Return to the patient and verify the approved timeline/observations update.
8. Request an analysis and inspect evidence references, trends, missing/conflicting information, limitations, and immutable version metadata.
9. Upload an included synthetic lab report, process it, correct extracted values if necessary, and approve it.
10. In settings, show the periodic-analysis interval. The short demo interval is for demonstration only; daily is the operational default.

## Recommended jury walkthrough (5 minutes)

Use this short path when reliability and timing matter more than showing every feature.

1. **Problem (30 seconds):** explain that physicians must listen, reason, and document at the same time. DiagnoVision reduces the documentation burden while keeping the physician in control.
2. **Dashboard (30 seconds):** show patient count, pending reviews, approved observations, and the permanent research-prototype notice.
3. **Patient context (30 seconds):** open **Leila Mansour** and point to the synthetic history and approved timeline.
4. **Recording consent (30 seconds):** click **Start recording** and show that all capture actions remain disabled until consent is checked.
5. **Reliable demo path (30 seconds):** check consent and use **Use jury demo sample**. This avoids microphone, room-noise, and browser-permission failures.
6. **Data cleaning (60 seconds):** show the raw transcript, click **Run data cleaning**, then compare the before/after table: fillers removed, values and units normalized, and clinical negation preserved.
7. **Structured draft (60 seconds):** show complaint, negated symptom, observation, medication, provenance, and missing information. Emphasize that the result is editable and requires physician validation.
8. **Close (30 seconds):** state that this frontend demo validates the workflow; real speech-to-text and clinical extraction providers are future integrations.

Suggested closing sentence:

> DiagnoVision does not replace clinical judgment. It converts an explicitly consented conversation into a traceable draft, highlights missing information, and leaves final validation to the physician.

### Claims to avoid

- Do not call the static transcription or extraction a deployed AI model.
- Do not claim clinical accuracy, certification, medical-device status, or production confidentiality compliance.
- Do not enter or record real patient information during the demonstration.
- Do not describe the structured draft as a diagnosis or treatment recommendation.

### Jury-day reliability checklist

- Start the backend and frontend before the presentation and keep the authenticated dashboard open.
- Use `doctor@diagnovision.local` / `DemoPass123!` only for the synthetic local workspace.
- Prefer **Use jury demo sample**; demonstrate the microphone only if time and browser permissions are already verified.
- Keep a second browser tab on the patient record as a fallback.
- Use a desktop viewport and browser zoom near 90–100% so the pipeline and structured draft remain visible.
- Rehearse the five-minute path twice and stop after the structured draft unless the jury asks for architecture details.

## Manual browser checks

- Chrome, Firefox, and Safari: microphone allow/deny, stop/cancel, track-release indicator, playback, and detected MIME type.
- Disconnect/reconnect the network during streaming; verify bounded retry/fallback to final upload.
- Refresh a nested patient route and use browser back/forward navigation.
- Expire/logout the session; verify protected routes redirect and in-memory query data clears.
- Attempt an unsupported/oversize upload and verify a safe error without filename/content in console logs.

MediaRecorder codecs differ by browser. The app detects supported MIME types at runtime; upload and manual entry remain the reliable fallback. Microphone capture works on localhost or HTTPS only.

