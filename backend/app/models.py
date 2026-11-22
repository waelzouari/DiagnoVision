import enum
import uuid
from datetime import date, datetime, timezone
from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


def uid() -> str:
    return str(uuid.uuid4())


def now() -> datetime:
    return datetime.now(timezone.utc)


class Status(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


class Doctor(Base):
    __tablename__ = "doctors"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255))
    password_hash: Mapped[str] = mapped_column(String(255))
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Patient(Base):
    __tablename__ = "patients"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    name: Mapped[str] = mapped_column(String(255), index=True)
    date_of_birth: Mapped[date] = mapped_column(Date)
    sex: Mapped[str | None] = mapped_column(String(40), nullable=True)
    demographics: Mapped[dict] = mapped_column(JSON, default=dict)
    medical_history: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)


class PatientAccess(Base):
    __tablename__ = "patient_access"
    __table_args__ = (UniqueConstraint("doctor_id", "patient_id"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    doctor_id: Mapped[str] = mapped_column(ForeignKey("doctors.id", ondelete="CASCADE"), index=True)
    patient_id: Mapped[str] = mapped_column(ForeignKey("patients.id", ondelete="CASCADE"), index=True)
    role: Mapped[str] = mapped_column(String(40), default="owner")


class Consultation(Base):
    __tablename__ = "consultations"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    patient_id: Mapped[str] = mapped_column(ForeignKey("patients.id"), index=True)
    doctor_id: Mapped[str] = mapped_column(ForeignKey("doctors.id"), index=True)
    mode: Mapped[str] = mapped_column(String(30), default="manual")
    status: Mapped[str] = mapped_column(String(30), default="draft")
    manual_notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class RecordingConsent(Base):
    __tablename__ = "recording_consents"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    consultation_id: Mapped[str] = mapped_column(ForeignKey("consultations.id"), unique=True)
    doctor_id: Mapped[str] = mapped_column(ForeignKey("doctors.id"))
    granted: Mapped[bool] = mapped_column(Boolean)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class AudioRecording(Base):
    __tablename__ = "audio_recordings"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    consultation_id: Mapped[str] = mapped_column(ForeignKey("consultations.id"), index=True)
    object_key: Mapped[str] = mapped_column(String(500))
    content_type: Mapped[str] = mapped_column(String(100))
    size_bytes: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Transcript(Base):
    __tablename__ = "transcripts"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    consultation_id: Mapped[str] = mapped_column(ForeignKey("consultations.id"), index=True)
    original_text: Mapped[str] = mapped_column(Text)
    corrected_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    language: Mapped[str] = mapped_column(String(16), default="en")
    provider: Mapped[str] = mapped_column(String(100), default="deterministic-demo")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class TranscriptSegment(Base):
    __tablename__ = "transcript_segments"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    transcript_id: Mapped[str] = mapped_column(ForeignKey("transcripts.id"), index=True)
    sequence: Mapped[int] = mapped_column(Integer)
    start_seconds: Mapped[float] = mapped_column(Float)
    end_seconds: Mapped[float] = mapped_column(Float)
    text: Mapped[str] = mapped_column(Text)


class ClinicalDraft(Base):
    __tablename__ = "clinical_drafts"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    consultation_id: Mapped[str] = mapped_column(ForeignKey("consultations.id"), unique=True)
    data: Mapped[dict] = mapped_column(JSON, default=dict)
    approved: Mapped[bool] = mapped_column(Boolean, default=False)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)


class Observation(Base):
    __tablename__ = "observations"
    __table_args__ = (Index("ix_observation_patient_code_date", "patient_id", "code", "observed_at"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    patient_id: Mapped[str] = mapped_column(ForeignKey("patients.id"), index=True)
    consultation_id: Mapped[str | None] = mapped_column(ForeignKey("consultations.id"), nullable=True)
    code: Mapped[str] = mapped_column(String(100))
    display: Mapped[str] = mapped_column(String(255))
    value: Mapped[float | None] = mapped_column(Float, nullable=True)
    unit: Mapped[str | None] = mapped_column(String(40), nullable=True)
    original_value: Mapped[str | None] = mapped_column(String(100), nullable=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    source_reference: Mapped[str] = mapped_column(String(255))
    approved: Mapped[bool] = mapped_column(Boolean, default=True)


class Condition(Base):
    __tablename__ = "conditions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    patient_id: Mapped[str] = mapped_column(ForeignKey("patients.id"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(40), default="confirmed")
    source_reference: Mapped[str] = mapped_column(String(255))


class Medication(Base):
    __tablename__ = "medications"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    patient_id: Mapped[str] = mapped_column(ForeignKey("patients.id"), index=True)
    name: Mapped[str] = mapped_column(String(255)); dosage: Mapped[str | None] = mapped_column(String(100), nullable=True)


class Allergy(Base):
    __tablename__ = "allergies"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    patient_id: Mapped[str] = mapped_column(ForeignKey("patients.id"), index=True)
    substance: Mapped[str] = mapped_column(String(255)); reaction: Mapped[str | None] = mapped_column(String(255), nullable=True)


class Symptom(Base):
    __tablename__ = "symptoms"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    patient_id: Mapped[str] = mapped_column(ForeignKey("patients.id"), index=True)
    name: Mapped[str] = mapped_column(String(255)); negated: Mapped[bool] = mapped_column(Boolean, default=False)


class Document(Base):
    __tablename__ = "documents"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    patient_id: Mapped[str] = mapped_column(ForeignKey("patients.id"), index=True)
    doctor_id: Mapped[str] = mapped_column(ForeignKey("doctors.id"))
    filename: Mapped[str] = mapped_column(String(255)); content_type: Mapped[str] = mapped_column(String(100))
    object_key: Mapped[str] = mapped_column(String(500)); status: Mapped[str] = mapped_column(String(30), default="uploaded")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class DocumentExtraction(Base):
    __tablename__ = "document_extractions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id"), unique=True)
    raw_text: Mapped[str] = mapped_column(Text); data: Mapped[dict] = mapped_column(JSON, default=dict)
    approved: Mapped[bool] = mapped_column(Boolean, default=False)


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    patient_id: Mapped[str] = mapped_column(ForeignKey("patients.id"), index=True)
    doctor_id: Mapped[str] = mapped_column(ForeignKey("doctors.id"))
    status: Mapped[str] = mapped_column(String(30), default="completed")
    result: Mapped[dict] = mapped_column(JSON, default=dict); model_version: Mapped[str] = mapped_column(String(100), default="deterministic-v1")
    reviewed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class AIFinding(Base):
    __tablename__ = "ai_findings"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    analysis_id: Mapped[str] = mapped_column(ForeignKey("analysis_runs.id"), index=True)
    category: Mapped[str] = mapped_column(String(60)); text: Mapped[str] = mapped_column(Text); references: Mapped[list] = mapped_column(JSON, default=list)


class Alert(Base):
    __tablename__ = "alerts"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    doctor_id: Mapped[str] = mapped_column(ForeignKey("doctors.id"), index=True); text: Mapped[str] = mapped_column(Text); reviewed: Mapped[bool] = mapped_column(Boolean, default=False)


class ProcessingJob(Base):
    __tablename__ = "processing_jobs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    doctor_id: Mapped[str] = mapped_column(ForeignKey("doctors.id"), index=True); kind: Mapped[str] = mapped_column(String(60))
    resource_id: Mapped[str] = mapped_column(String(36)); status: Mapped[str] = mapped_column(String(30), default=Status.pending.value)
    result: Mapped[dict] = mapped_column(JSON, default=dict); error: Mapped[str | None] = mapped_column(Text, nullable=True)
    deduplication_key: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Embedding(Base):
    __tablename__ = "embeddings"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid); patient_id: Mapped[str] = mapped_column(ForeignKey("patients.id"), index=True)
    doctor_id: Mapped[str] = mapped_column(ForeignKey("doctors.id"), index=True); source_reference: Mapped[str] = mapped_column(String(255)); text: Mapped[str] = mapped_column(Text); vector: Mapped[list] = mapped_column(JSON, default=list)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid); doctor_id: Mapped[str | None] = mapped_column(ForeignKey("doctors.id"), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(100)); resource_type: Mapped[str] = mapped_column(String(100)); resource_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class DoctorSetting(Base):
    __tablename__ = "doctor_settings"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid); doctor_id: Mapped[str] = mapped_column(ForeignKey("doctors.id"), unique=True)
    analysis_interval_minutes: Mapped[int] = mapped_column(Integer, default=1440); language: Mapped[str] = mapped_column(String(16), default="en"); retention_days: Mapped[int] = mapped_column(Integer, default=365)

