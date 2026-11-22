import json
import os
import re
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Literal
from fastapi import Cookie, Depends, FastAPI, File, HTTPException, Query, Request, Response, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session
from .config import get_settings
from .database import Base, SessionLocal, engine, get_db
from .models import *
from .providers import DeterministicExtractionProvider, DeterministicSpeechProvider, trend_analysis
from .schemas import *
from .security import create_token, decode_token, enforce_csrf, get_current_doctor, hash_password, new_csrf, verify_password

settings = get_settings()
app = FastAPI(title="DiagnoVision Clinical Intelligence API", version="0.1.0", description="Research and hackathon prototype; not a diagnostic system.")
app.add_middleware(CORSMiddleware, allow_origins=settings.origins, allow_credentials=True, allow_methods=["*"], allow_headers=["Content-Type", "X-CSRF-Token"])
speech = DeterministicSpeechProvider(); extractor = DeterministicExtractionProvider()
upload_root = Path(__file__).resolve().parents[1] / "data" / "private"


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
    return response


def cookie(response: Response, key: str, value: str, max_age: int, httponly: bool = True):
    response.set_cookie(key, value, max_age=max_age, httponly=httponly, secure=settings.secure_cookies, samesite="strict", path="/")


def access_patient(db: Session, doctor: Doctor, patient_id: str) -> Patient:
    patient = db.scalar(select(Patient).join(PatientAccess).where(Patient.id == patient_id, PatientAccess.doctor_id == doctor.id))
    if not patient: raise HTTPException(404, "Patient not found")
    return patient


def access_consultation(db: Session, doctor: Doctor, consultation_id: str) -> Consultation:
    item = db.scalar(select(Consultation).where(Consultation.id == consultation_id, Consultation.doctor_id == doctor.id))
    if not item: raise HTTPException(404, "Consultation not found")
    return item


def audit(db: Session, doctor_id: str | None, action: str, resource: str, resource_id: str | None = None):
    db.add(AuditLog(doctor_id=doctor_id, action=action, resource_type=resource, resource_id=resource_id))


@app.on_event("startup")
def startup():
    Base.metadata.create_all(engine); upload_root.mkdir(parents=True, exist_ok=True)
    if settings.demo_mode: seed_demo()


def seed_demo():
    db = SessionLocal()
    try:
        if db.scalar(select(Doctor).where(Doctor.email == "doctor@diagnovision.local")): return
        doctor = Doctor(email="doctor@diagnovision.local", full_name="Dr. Amira Ben Salem", password_hash=hash_password("DemoPass123!")); db.add(doctor); db.flush()
        profiles = [
            ("Leila Mansour", "improving", [152, 138, 126]), ("Sami Gharbi", "worsening", [124, 139, 154]),
            ("Noura Trabelsi", "stable", [118, 119, 118]), ("Youssef Ayari", "incomplete", []), ("Rim Jaziri", "conflicting", [130, 158, 129]),
        ]
        for idx, (name, scenario, values) in enumerate(profiles):
            patient = Patient(name=name, date_of_birth=datetime(1955 + idx * 7, 1 + idx, 10).date(), sex="female" if idx % 2 == 0 else "male", demographics={"city": "Synthetic Tunis", "scenario": scenario}, medical_history="Entirely fictional synthetic demonstration record.")
            db.add(patient); db.flush(); db.add(PatientAccess(doctor_id=doctor.id, patient_id=patient.id))
            for step, value in enumerate(values): db.add(Observation(patient_id=patient.id, code="8480-6", display="Systolic blood pressure", value=value, unit="mmHg", original_value=str(value), observed_at=datetime(2026, 8 + step, 1, tzinfo=timezone.utc), source_reference=f"synthetic:{scenario}:{step}"))
        db.add(DoctorSetting(doctor_id=doctor.id)); db.commit()
    finally: db.close()


@app.get("/health")
def health(): return {"status": "healthy", "demo_mode": settings.demo_mode}


@app.post("/api/v1/auth/login", response_model=DoctorOut)
def login(body: Login, response: Response, db: Session = Depends(get_db)):
    doctor = db.scalar(select(Doctor).where(func.lower(Doctor.email) == body.email.lower()))
    if not doctor or not verify_password(body.password, doctor.password_hash): raise HTTPException(401, "Invalid email or password")
    csrf = new_csrf(); cookie(response, "access_token", create_token(doctor.id, "access", timedelta(minutes=settings.access_minutes)), settings.access_minutes * 60)
    cookie(response, "refresh_token", create_token(doctor.id, "refresh", timedelta(days=settings.refresh_days)), settings.refresh_days * 86400)
    cookie(response, "csrf_token", csrf, settings.refresh_days * 86400, httponly=False)
    audit(db, doctor.id, "login", "session"); db.commit(); return doctor


@app.get("/api/v1/auth/me", response_model=DoctorOut)
def me(doctor: Doctor = Depends(get_current_doctor)): return doctor


@app.get("/api/v1/auth/csrf")
def csrf(response: Response, doctor: Doctor = Depends(get_current_doctor)):
    value = new_csrf(); cookie(response, "csrf_token", value, settings.refresh_days * 86400, httponly=False); return {"csrf_token": value}


@app.post("/api/v1/auth/refresh")
def refresh(response: Response, refresh_token: str | None = Cookie(default=None), db: Session = Depends(get_db)):
    if not refresh_token: raise HTTPException(401, "Refresh token required")
    doctor_id = decode_token(refresh_token, "refresh"); doctor = db.get(Doctor, doctor_id)
    if not doctor: raise HTTPException(401, "Account not found")
    csrf = new_csrf(); cookie(response, "access_token", create_token(doctor.id, "access", timedelta(minutes=settings.access_minutes)), settings.access_minutes * 60)
    cookie(response, "refresh_token", create_token(doctor.id, "refresh", timedelta(days=settings.refresh_days)), settings.refresh_days * 86400)
    cookie(response, "csrf_token", csrf, settings.refresh_days * 86400, httponly=False); return {"status": "refreshed", "csrf_token": csrf}


@app.post("/api/v1/auth/logout", dependencies=[Depends(enforce_csrf)])
def logout(response: Response, doctor: Doctor = Depends(get_current_doctor), db: Session = Depends(get_db)):
    audit(db, doctor.id, "logout", "session"); db.commit()
    for key in ("access_token", "refresh_token", "csrf_token"): response.delete_cookie(key, path="/")
    return {"status": "logged_out"}


def patient_trend(db: Session, patient_id: str) -> str:
    """Return a deterministic population-filtering label from approved facts only."""
    values = list(
        db.scalars(
            select(Observation)
            .where(
                Observation.patient_id == patient_id,
                Observation.approved.is_(True),
                Observation.value.is_not(None),
            )
            .order_by(Observation.code, Observation.observed_at, Observation.id)
        )
    )
    by_code: dict[str, list[Observation]] = {}
    for value in values:
        by_code.setdefault(value.code, []).append(value)
    deltas = [items[-1].value - items[0].value for items in by_code.values() if len(items) > 1]
    if not deltas:
        return "insufficient_data"
    if all(abs(delta) < 0.01 for delta in deltas):
        return "stable"
    # Direction is deliberately descriptive, not a clinical judgment. For the
    # supported synthetic blood-pressure series, decreasing is labelled improving.
    return "improving" if sum(deltas) < 0 else "worsening"


@app.get("/api/v1/patients", response_model=PatientList)
def patients(
    search: str = Query("", max_length=100),
    trend: Literal["improving", "stable", "worsening", "insufficient_data"] | None = None,
    sort_by: Literal["name", "date_of_birth", "created_at", "updated_at"] = "name",
    sort_order: Literal["asc", "desc"] = "asc",
    page: int = Query(1, ge=1, le=100000),
    page_size: int = Query(20, ge=1, le=100),
    doctor: Doctor = Depends(get_current_doctor),
    db: Session = Depends(get_db),
):
    # Authorization is the first and invariant query predicate.
    base = select(Patient).join(PatientAccess).where(PatientAccess.doctor_id == doctor.id)
    normalized_search = search.strip()
    if normalized_search:
        escaped = normalized_search.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        base = base.where(Patient.name.ilike(f"%{escaped}%", escape="\\"))
    column = getattr(Patient, sort_by)
    ordering = column.asc() if sort_order == "asc" else column.desc()
    # A UUID tie-breaker makes pagination stable when sort keys are equal.
    authorized = list(db.scalars(base.order_by(ordering, Patient.id.asc())))
    if trend:
        authorized = [item for item in authorized if patient_trend(db, item.id) == trend]
    total = len(authorized)
    start = (page - 1) * page_size
    return PatientList(items=authorized[start : start + page_size], total=total, page=page, page_size=page_size)


@app.post("/api/v1/patients", response_model=PatientOut, status_code=201, dependencies=[Depends(enforce_csrf)])
def create_patient(body: PatientCreate, doctor: Doctor = Depends(get_current_doctor), db: Session = Depends(get_db)):
    patient = Patient(**body.model_dump()); db.add(patient); db.flush(); db.add(PatientAccess(doctor_id=doctor.id, patient_id=patient.id)); audit(db, doctor.id, "create", "patient", patient.id); db.commit(); db.refresh(patient); return patient


@app.get("/api/v1/patients/{patient_id}", response_model=PatientOut)
def patient(patient_id: str, doctor: Doctor = Depends(get_current_doctor), db: Session = Depends(get_db)): return access_patient(db, doctor, patient_id)


@app.patch("/api/v1/patients/{patient_id}", response_model=PatientOut, dependencies=[Depends(enforce_csrf)])
def patch_patient(patient_id: str, body: PatientPatch, doctor: Doctor = Depends(get_current_doctor), db: Session = Depends(get_db)):
    item = access_patient(db, doctor, patient_id)
    for key, value in body.model_dump(exclude_unset=True).items(): setattr(item, key, value)
    audit(db, doctor.id, "update", "patient", item.id); db.commit(); db.refresh(item); return item


@app.get("/api/v1/patients/{patient_id}/observations")
def observations(
    patient_id: str,
    code: str | None = Query(None, max_length=100),
    category: str | None = Query(None, max_length=100),
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    sort_order: Literal["asc", "desc"] = "asc",
    offset: int = Query(0, ge=0, le=1_000_000),
    limit: int = Query(100, ge=1, le=500),
    doctor: Doctor = Depends(get_current_doctor),
    db: Session = Depends(get_db),
):
    access_patient(db, doctor, patient_id)
    if date_from and date_to and date_from > date_to:
        raise HTTPException(422, "date_from must not be after date_to")
    query = select(Observation).where(
        Observation.patient_id == patient_id, Observation.approved.is_(True)
    )
    if code:
        query = query.where(Observation.code == code.strip())
    if category:
        escaped = category.strip().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        query = query.where(Observation.display.ilike(f"%{escaped}%", escape="\\"))
    if date_from:
        query = query.where(Observation.observed_at >= date_from)
    if date_to:
        query = query.where(Observation.observed_at <= date_to)
    order = Observation.observed_at.asc() if sort_order == "asc" else Observation.observed_at.desc()
    return list(db.scalars(query.order_by(order, Observation.id.asc()).offset(offset).limit(limit)))


@app.get("/api/v1/patients/{patient_id}/timeline")
def timeline(
    patient_id: str,
    event_type: Literal["consultation", "document", "observation"] | None = None,
    status_filter: str | None = Query(None, alias="status", max_length=40),
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    sort_order: Literal["asc", "desc"] = "desc",
    offset: int = Query(0, ge=0, le=1_000_000),
    limit: int = Query(100, ge=1, le=500),
    doctor: Doctor = Depends(get_current_doctor),
    db: Session = Depends(get_db),
):
    access_patient(db, doctor, patient_id)
    if date_from and date_to and date_from > date_to:
        raise HTTPException(422, "date_from must not be after date_to")
    events = []
    if event_type in (None, "consultation"):
        query = select(Consultation).where(
            Consultation.patient_id == patient_id, Consultation.doctor_id == doctor.id
        )
        if status_filter:
            query = query.where(Consultation.status == status_filter)
        if date_from:
            query = query.where(Consultation.created_at >= date_from)
        if date_to:
            query = query.where(Consultation.created_at <= date_to)
        for item in db.scalars(query):
            events.append({"id": item.id, "type": "consultation", "date": item.created_at, "occurred_at": item.created_at, "title": f"{item.mode.title()} consultation", "status": item.status})
    if event_type in (None, "document"):
        query = select(Document).where(
            Document.patient_id == patient_id, Document.doctor_id == doctor.id
        )
        if status_filter:
            query = query.where(Document.status == status_filter)
        if date_from:
            query = query.where(Document.created_at >= date_from)
        if date_to:
            query = query.where(Document.created_at <= date_to)
        for item in db.scalars(query):
            events.append({"id": item.id, "type": "document", "date": item.created_at, "occurred_at": item.created_at, "title": item.filename, "status": item.status})
    if event_type in (None, "observation") and not status_filter:
        query = select(Observation).where(
            Observation.patient_id == patient_id, Observation.approved.is_(True)
        )
        if date_from:
            query = query.where(Observation.observed_at >= date_from)
        if date_to:
            query = query.where(Observation.observed_at <= date_to)
        for item in db.scalars(query):
            events.append({"id": item.id, "type": "observation", "date": item.observed_at, "occurred_at": item.observed_at, "title": item.display, "status": "approved"})
    events.sort(key=lambda item: (item["date"], item["id"]), reverse=sort_order == "desc")
    return events[offset : offset + limit]


@app.get("/api/v1/patients/{patient_id}/consultations")
def consultations(
    patient_id: str,
    status_filter: str | None = Query(None, alias="status", max_length=40),
    mode: Literal["manual", "audio", "live"] | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    offset: int = Query(0, ge=0, le=1_000_000),
    limit: int = Query(50, ge=1, le=200),
    doctor: Doctor = Depends(get_current_doctor),
    db: Session = Depends(get_db),
):
    access_patient(db, doctor, patient_id)
    if date_from and date_to and date_from > date_to:
        raise HTTPException(422, "date_from must not be after date_to")
    query = select(Consultation).where(
        Consultation.patient_id == patient_id, Consultation.doctor_id == doctor.id
    )
    if status_filter:
        query = query.where(Consultation.status == status_filter)
    if mode:
        query = query.where(Consultation.mode == mode)
    if date_from:
        query = query.where(Consultation.created_at >= date_from)
    if date_to:
        query = query.where(Consultation.created_at <= date_to)
    return list(db.scalars(query.order_by(Consultation.created_at.desc(), Consultation.id.asc()).offset(offset).limit(limit)))


@app.post("/api/v1/patients/{patient_id}/consultations", status_code=201, dependencies=[Depends(enforce_csrf)])
def create_consultation(patient_id: str, body: ConsultationCreate, doctor: Doctor = Depends(get_current_doctor), db: Session = Depends(get_db)):
    access_patient(db, doctor, patient_id); item = Consultation(patient_id=patient_id, doctor_id=doctor.id, **body.model_dump()); db.add(item); db.commit(); db.refresh(item); return item


@app.get("/api/v1/consultations/{consultation_id}")
def get_consultation(consultation_id: str, doctor: Doctor = Depends(get_current_doctor), db: Session = Depends(get_db)):
    item = access_consultation(db, doctor, consultation_id); transcript = db.scalar(select(Transcript).where(Transcript.consultation_id == item.id)); draft = db.scalar(select(ClinicalDraft).where(ClinicalDraft.consultation_id == item.id)); return {"consultation": item, "transcript": transcript, "draft": draft}


@app.post("/api/v1/consultations/{consultation_id}/consent", dependencies=[Depends(enforce_csrf)])
def consent(consultation_id: str, body: ConsentIn, doctor: Doctor = Depends(get_current_doctor), db: Session = Depends(get_db)):
    item = access_consultation(db, doctor, consultation_id); old = db.scalar(select(RecordingConsent).where(RecordingConsent.consultation_id == item.id))
    if old: old.granted = body.granted; old.recorded_at = datetime.now(timezone.utc)
    else: old = RecordingConsent(consultation_id=item.id, doctor_id=doctor.id, granted=body.granted); db.add(old)
    db.commit(); return old


async def safe_upload(file: UploadFile, allowed: set[str]) -> tuple[bytes, str]:
    content_type = (file.content_type or "").lower()
    if content_type not in allowed: raise HTTPException(415, "Unsupported content type")
    data = await file.read(settings.max_upload_bytes + 1)
    if not data or len(data) > settings.max_upload_bytes: raise HTTPException(413, "Invalid upload size")
    return data, content_type


@app.post("/api/v1/consultations/{consultation_id}/audio", status_code=201, dependencies=[Depends(enforce_csrf)])
async def audio(consultation_id: str, file: UploadFile = File(...), doctor: Doctor = Depends(get_current_doctor), db: Session = Depends(get_db)):
    item = access_consultation(db, doctor, consultation_id); granted = db.scalar(select(RecordingConsent).where(RecordingConsent.consultation_id == item.id, RecordingConsent.granted.is_(True)))
    if not granted: raise HTTPException(409, "Recording consent is required")
    data, content_type = await safe_upload(file, {"audio/wav", "audio/x-wav", "audio/mpeg", "audio/mp4", "audio/webm", "video/webm"})
    key = f"audio/{item.id}/{secrets.token_hex(12)}"; path = upload_root / key; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(data)
    record = AudioRecording(consultation_id=item.id, object_key=key, content_type=content_type, size_bytes=len(data)); db.add(record); db.commit(); db.refresh(record); return record


def completed_job(db: Session, doctor: Doctor, kind: str, resource_id: str, result: dict, dedupe: str | None = None) -> ProcessingJob:
    if dedupe:
        existing = db.scalar(select(ProcessingJob).where(ProcessingJob.deduplication_key == dedupe, ProcessingJob.status.in_(["pending", "processing", "completed"])))
        if existing: return existing
    job = ProcessingJob(doctor_id=doctor.id, kind=kind, resource_id=resource_id, status="completed", result=result, deduplication_key=dedupe); db.add(job); db.commit(); db.refresh(job); return job


@app.post("/api/v1/consultations/{consultation_id}/transcribe", status_code=202, dependencies=[Depends(enforce_csrf)])
def transcribe(consultation_id: str, doctor: Doctor = Depends(get_current_doctor), db: Session = Depends(get_db)):
    item = access_consultation(db, doctor, consultation_id); recording = db.scalar(select(AudioRecording).where(AudioRecording.consultation_id == item.id).order_by(AudioRecording.created_at.desc()))
    content = (upload_root / recording.object_key).read_bytes() if recording else item.manual_notes.encode()
    result = speech.transcribe(content); transcript = Transcript(consultation_id=item.id, original_text=result["text"], language=result["language"], provider=result["provider"]); db.add(transcript); db.flush()
    for segment in result["segments"]: db.add(TranscriptSegment(transcript_id=transcript.id, **segment))
    job = completed_job(db, doctor, "transcription", item.id, {"transcript_id": transcript.id}); return {"job_id": job.id, "status": job.status}


@app.post("/api/v1/consultations/{consultation_id}/extract", status_code=202, dependencies=[Depends(enforce_csrf)])
def extract(consultation_id: str, doctor: Doctor = Depends(get_current_doctor), db: Session = Depends(get_db)):
    item = access_consultation(db, doctor, consultation_id); transcript = db.scalar(select(Transcript).where(Transcript.consultation_id == item.id).order_by(Transcript.created_at.desc())); text = (transcript.corrected_text or transcript.original_text) if transcript else item.manual_notes
    if not text: raise HTTPException(409, "No transcript or manual notes available")
    data = extractor.extract(text, f"consultation:{item.id}"); draft = db.scalar(select(ClinicalDraft).where(ClinicalDraft.consultation_id == item.id))
    if draft: draft.data = data; draft.approved = False
    else: draft = ClinicalDraft(consultation_id=item.id, data=data); db.add(draft)
    db.flush(); job = completed_job(db, doctor, "extraction", item.id, {"draft_id": draft.id}); return {"job_id": job.id, "status": job.status}


@app.patch("/api/v1/consultations/{consultation_id}/draft", dependencies=[Depends(enforce_csrf)])
def patch_draft(consultation_id: str, body: DraftPatch, doctor: Doctor = Depends(get_current_doctor), db: Session = Depends(get_db)):
    item = access_consultation(db, doctor, consultation_id); draft = db.scalar(select(ClinicalDraft).where(ClinicalDraft.consultation_id == item.id))
    if not draft: raise HTTPException(404, "Draft not found")
    draft.data = body.data
    if body.corrected_transcript is not None:
        transcript = db.scalar(select(Transcript).where(Transcript.consultation_id == item.id).order_by(Transcript.created_at.desc())); transcript.corrected_text = body.corrected_transcript
    db.commit(); return draft


@app.post("/api/v1/consultations/{consultation_id}/approve", dependencies=[Depends(enforce_csrf)])
def approve(consultation_id: str, doctor: Doctor = Depends(get_current_doctor), db: Session = Depends(get_db)):
    item = access_consultation(db, doctor, consultation_id); draft = db.scalar(select(ClinicalDraft).where(ClinicalDraft.consultation_id == item.id))
    if not draft: raise HTTPException(404, "Draft not found")
    if draft.approved: return {"status": "already_approved", "draft_id": draft.id}
    for value in draft.data.get("observations", []): db.add(Observation(patient_id=item.patient_id, consultation_id=item.id, **{k: value.get(k) for k in ("code", "display", "value", "unit", "original_value", "source_reference")}))
    for value in draft.data.get("symptoms", []): db.add(Symptom(patient_id=item.patient_id, name=value["name"], negated=value.get("negated", False)))
    draft.approved = True; draft.approved_at = datetime.now(timezone.utc); item.status = "approved"; audit(db, doctor.id, "approve", "clinical_draft", draft.id); db.commit(); return {"status": "approved", "draft_id": draft.id}


@app.post("/api/v1/patients/{patient_id}/analyze", status_code=202, dependencies=[Depends(enforce_csrf)])
def analyze(patient_id: str, doctor: Doctor = Depends(get_current_doctor), db: Session = Depends(get_db)):
    patient = access_patient(db, doctor, patient_id); values = list(db.scalars(select(Observation).where(Observation.patient_id == patient.id, Observation.approved.is_(True)))); result = trend_analysis(values)
    run = AnalysisRun(patient_id=patient.id, doctor_id=doctor.id, result=result); db.add(run); db.flush(); job = completed_job(db, doctor, "analysis", patient.id, {"analysis_id": run.id}, f"analysis:{patient.id}:{patient.updated_at.isoformat()}"); return {"job_id": job.id, "status": job.status}


@app.get("/api/v1/patients/{patient_id}/analyses")
def analyses(
    patient_id: str,
    status_filter: Literal["pending", "processing", "completed", "failed", "cancelled"] | None = Query(None, alias="status"),
    reviewed: bool | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    offset: int = Query(0, ge=0, le=1_000_000),
    limit: int = Query(50, ge=1, le=200),
    doctor: Doctor = Depends(get_current_doctor),
    db: Session = Depends(get_db),
):
    access_patient(db, doctor, patient_id)
    if date_from and date_to and date_from > date_to:
        raise HTTPException(422, "date_from must not be after date_to")
    query = select(AnalysisRun).where(
        AnalysisRun.patient_id == patient_id, AnalysisRun.doctor_id == doctor.id
    )
    if status_filter:
        query = query.where(AnalysisRun.status == status_filter)
    if reviewed is not None:
        query = query.where(AnalysisRun.reviewed.is_(reviewed))
    if date_from:
        query = query.where(AnalysisRun.created_at >= date_from)
    if date_to:
        query = query.where(AnalysisRun.created_at <= date_to)
    return list(db.scalars(query.order_by(AnalysisRun.created_at.desc(), AnalysisRun.id.asc()).offset(offset).limit(limit)))


@app.get("/api/v1/analyses/{analysis_id}")
def analysis(analysis_id: str, doctor: Doctor = Depends(get_current_doctor), db: Session = Depends(get_db)):
    run = db.scalar(select(AnalysisRun).where(AnalysisRun.id == analysis_id, AnalysisRun.doctor_id == doctor.id));
    if not run: raise HTTPException(404, "Analysis not found")
    return run


@app.post("/api/v1/analyses/{analysis_id}/review", dependencies=[Depends(enforce_csrf)])
def review_analysis(analysis_id: str, body: ReviewIn, doctor: Doctor = Depends(get_current_doctor), db: Session = Depends(get_db)):
    run = db.scalar(select(AnalysisRun).where(AnalysisRun.id == analysis_id, AnalysisRun.doctor_id == doctor.id));
    if not run: raise HTTPException(404, "Analysis not found")
    run.reviewed = body.reviewed; db.commit(); return run


@app.post("/api/v1/patients/{patient_id}/documents", status_code=201, dependencies=[Depends(enforce_csrf)])
async def upload_document(patient_id: str, file: UploadFile = File(...), doctor: Doctor = Depends(get_current_doctor), db: Session = Depends(get_db)):
    access_patient(db, doctor, patient_id); data, content_type = await safe_upload(file, {"application/pdf", "image/png", "image/jpeg"}); safe_name = re.sub(r"[^A-Za-z0-9._-]", "_", Path(file.filename or "document").name)[:120]; key = f"documents/{patient_id}/{secrets.token_hex(12)}"; path = upload_root / key; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(data)
    doc = Document(patient_id=patient_id, doctor_id=doctor.id, filename=safe_name, content_type=content_type, object_key=key); db.add(doc); db.commit(); db.refresh(doc); return doc


@app.get("/api/v1/patients/{patient_id}/documents")
def documents(
    patient_id: str,
    status_filter: Literal["uploaded", "review_required", "approved"] | None = Query(None, alias="status"),
    content_type: Literal["application/pdf", "image/png", "image/jpeg"] | None = None,
    search: str = Query("", max_length=100),
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    offset: int = Query(0, ge=0, le=1_000_000),
    limit: int = Query(50, ge=1, le=200),
    doctor: Doctor = Depends(get_current_doctor),
    db: Session = Depends(get_db),
):
    access_patient(db, doctor, patient_id)
    if date_from and date_to and date_from > date_to:
        raise HTTPException(422, "date_from must not be after date_to")
    query = select(Document).where(
        Document.patient_id == patient_id, Document.doctor_id == doctor.id
    )
    if status_filter:
        query = query.where(Document.status == status_filter)
    if content_type:
        query = query.where(Document.content_type == content_type)
    if search.strip():
        escaped = search.strip().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        query = query.where(Document.filename.ilike(f"%{escaped}%", escape="\\"))
    if date_from:
        query = query.where(Document.created_at >= date_from)
    if date_to:
        query = query.where(Document.created_at <= date_to)
    return list(db.scalars(query.order_by(Document.created_at.desc(), Document.id.asc()).offset(offset).limit(limit)))


@app.post("/api/v1/documents/{document_id}/process", status_code=202, dependencies=[Depends(enforce_csrf)])
def process_document(document_id: str, doctor: Doctor = Depends(get_current_doctor), db: Session = Depends(get_db)):
    doc = db.scalar(select(Document).where(Document.id == document_id, Document.doctor_id == doctor.id));
    if not doc: raise HTTPException(404, "Document not found")
    raw = "Synthetic laboratory report. Hemoglobin 13.6 g/dL. Collection date 2026-10-12."
    data = {"observations": [{"name": "Hemoglobin", "value": 13.6, "unit": "g/dL", "original_value": "13.6", "source_page": 1}], "document_date": "2026-10-12", "simulated": True}; ext = DocumentExtraction(document_id=doc.id, raw_text=raw, data=data); db.add(ext); doc.status = "review_required"; db.flush(); job = completed_job(db, doctor, "document_processing", doc.id, {"extraction_id": ext.id}); return {"job_id": job.id, "status": job.status}


@app.post("/api/v1/documents/{document_id}/approve", dependencies=[Depends(enforce_csrf)])
def approve_document(document_id: str, doctor: Doctor = Depends(get_current_doctor), db: Session = Depends(get_db)):
    doc = db.scalar(select(Document).where(Document.id == document_id, Document.doctor_id == doctor.id));
    if not doc: raise HTTPException(404, "Document not found")
    ext = db.scalar(select(DocumentExtraction).where(DocumentExtraction.document_id == doc.id));
    if not ext: raise HTTPException(409, "Process document first")
    ext.approved = True; doc.status = "approved"; db.commit(); return {"status": "approved", "extraction_id": ext.id}


@app.get("/api/v1/jobs/{job_id}")
def job(job_id: str, doctor: Doctor = Depends(get_current_doctor), db: Session = Depends(get_db)):
    item = db.scalar(select(ProcessingJob).where(ProcessingJob.id == job_id, ProcessingJob.doctor_id == doctor.id));
    if not item: raise HTTPException(404, "Job not found")
    return item


@app.get("/api/v1/dashboard/overview")
def dashboard(doctor: Doctor = Depends(get_current_doctor), db: Session = Depends(get_db)):
    patient_ids = select(PatientAccess.patient_id).where(PatientAccess.doctor_id == doctor.id)
    return {
        "patient_count": db.scalar(
            select(func.count())
            .select_from(PatientAccess)
            .where(PatientAccess.doctor_id == doctor.id)
        )
        or 0,
        "recent_consultations": list(
            db.scalars(
                select(Consultation)
                .where(Consultation.doctor_id == doctor.id)
                .order_by(Consultation.created_at.desc())
                .limit(5)
            )
        ),
        "pending_reviews": db.scalar(
            select(func.count())
            .select_from(ClinicalDraft)
            .join(Consultation)
            .where(
                Consultation.doctor_id == doctor.id,
                ClinicalDraft.approved.is_(False),
            )
        )
        or 0,
        "latest_analyses": list(
            db.scalars(
                select(AnalysisRun)
                .where(AnalysisRun.doctor_id == doctor.id)
                .order_by(AnalysisRun.created_at.desc())
                .limit(5)
            )
        ),
        "relevant_observations": list(
            db.scalars(
                select(Observation)
                .where(
                    Observation.patient_id.in_(patient_ids),
                    Observation.approved.is_(True),
                    Observation.value.is_not(None),
                )
                .order_by(Observation.observed_at.desc(), Observation.id.asc())
                .limit(12)
            )
        ),
        "demo_mode": settings.demo_mode,
    }


@app.get("/api/v1/settings")
def get_doctor_settings(doctor: Doctor = Depends(get_current_doctor), db: Session = Depends(get_db)):
    return db.scalar(select(DoctorSetting).where(DoctorSetting.doctor_id == doctor.id))


@app.patch("/api/v1/settings", dependencies=[Depends(enforce_csrf)])
def patch_settings(body: SettingsPatch, doctor: Doctor = Depends(get_current_doctor), db: Session = Depends(get_db)):
    item = db.scalar(select(DoctorSetting).where(DoctorSetting.doctor_id == doctor.id)) or DoctorSetting(doctor_id=doctor.id); db.add(item)
    for key, value in body.model_dump(exclude_unset=True).items(): setattr(item, key, value)
    db.commit(); db.refresh(item); return item


@app.websocket("/api/v1/consultations/{consultation_id}/stream")
async def stream(websocket: WebSocket, consultation_id: str):
    origin = websocket.headers.get("origin")
    if origin and origin not in settings.origins: await websocket.close(code=1008); return
    token = websocket.cookies.get("access_token")
    try: doctor_id = decode_token(token or "", "access")
    except HTTPException: await websocket.close(code=1008); return
    db = SessionLocal()
    try:
        item = db.scalar(select(Consultation).where(Consultation.id == consultation_id, Consultation.doctor_id == doctor_id)); consent = db.scalar(select(RecordingConsent).where(RecordingConsent.consultation_id == consultation_id, RecordingConsent.granted.is_(True)))
        if not item or not consent: await websocket.close(code=1008); return
        await websocket.accept(); sequence = 0; chunks = bytearray()
        while True:
            message = await websocket.receive()
            if message.get("bytes") is not None:
                chunks.extend(message["bytes"])
                if len(chunks) > settings.max_upload_bytes: await websocket.send_json({"event": "error", "code": "limit_exceeded"}); await websocket.close(code=1009); return
                await websocket.send_json({"event": "partial", "session_id": consultation_id, "sequence": sequence, "text": "Listening…", "timestamp": datetime.now(timezone.utc).isoformat()}); sequence += 1
            elif message.get("text"):
                data = json.loads(message["text"])
                if data.get("event") == "stop":
                    result = speech.transcribe(bytes(chunks)); await websocket.send_json({"event": "final", "session_id": consultation_id, "sequence": sequence, "text": result["text"], "segments": result["segments"]}); return
    except WebSocketDisconnect: pass
    finally: db.close()

