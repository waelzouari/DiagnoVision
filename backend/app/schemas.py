from datetime import date, datetime
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Login(BaseModel): email: str; password: str
class DoctorOut(ORMModel): id: str; email: str; full_name: str
class PatientCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255); date_of_birth: date; sex: str | None = None; demographics: dict[str, Any] = {}; medical_history: str = ""
class PatientPatch(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=255); date_of_birth: date | None = None; sex: str | None = None; demographics: dict[str, Any] | None = None; medical_history: str | None = None
class PatientOut(ORMModel):
    id: str; name: str; date_of_birth: date; sex: str | None; demographics: dict[str, Any]; medical_history: str; created_at: datetime; updated_at: datetime
class PatientList(BaseModel): items: list[PatientOut]; total: int; page: int; page_size: int
class ConsultationCreate(BaseModel): mode: Literal["manual", "audio", "live"] = "manual"; manual_notes: str = ""
class ConsentIn(BaseModel): granted: bool
class DraftPatch(BaseModel): data: dict[str, Any]; corrected_transcript: str | None = None
class ReviewIn(BaseModel): reviewed: bool = True; note: str | None = None
class SettingsPatch(BaseModel): analysis_interval_minutes: int | None = Field(default=None, ge=1, le=525600); language: str | None = None; retention_days: int | None = Field(default=None, ge=1, le=3650)

