import re
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from .models import Observation


class SpeechProvider(ABC):
    @abstractmethod
    def transcribe(self, content: bytes, language: str | None = None) -> dict: ...


class DeterministicSpeechProvider(SpeechProvider):
    def transcribe(self, content: bytes, language: str | None = None) -> dict:
        if not content:
            raise ValueError("Recording is empty")
        text = "Patient reports fatigue for three days and denies chest pain. Blood pressure is 128/82 mmHg. Follow-up in two weeks."
        return {"text": text, "language": language or "en", "segments": [{"sequence": 0, "start_seconds": 0.0, "end_seconds": 8.0, "text": text}], "provider": "deterministic-demo"}


class ExtractionProvider(ABC):
    @abstractmethod
    def extract(self, text: str, source: str) -> dict: ...


class DeterministicExtractionProvider(ExtractionProvider):
    def extract(self, text: str, source: str) -> dict:
        lower = text.lower()
        symptoms = []
        if "fatigue" in lower: symptoms.append({"name": "fatigue", "negated": False, "source_reference": source})
        if "denies chest pain" in lower or "no chest pain" in lower: symptoms.append({"name": "chest pain", "negated": True, "source_reference": source})
        match = re.search(r"(?:blood pressure|bp)(?: is)?\s*(\d{2,3})/(\d{2,3})", lower)
        observations = []
        if match:
            observations.extend([
                {"code": "8480-6", "display": "Systolic blood pressure", "value": float(match.group(1)), "unit": "mmHg", "original_value": match.group(1), "source_reference": source},
                {"code": "8462-4", "display": "Diastolic blood pressure", "value": float(match.group(2)), "unit": "mmHg", "original_value": match.group(2), "source_reference": source},
            ])
        return {"chief_complaint": "Fatigue" if "fatigue" in lower else None, "symptoms": symptoms, "observations": observations, "conditions": [], "medications": [], "allergies": [], "recommendations": ["Follow-up in two weeks"] if "follow-up" in lower else [], "missing_information": ["Medication reconciliation"], "source_reference": source, "status": "draft", "simulated": True}


def trend_analysis(observations: list[Observation]) -> dict:
    grouped: dict[str, list[Observation]] = {}
    for item in observations: grouped.setdefault(item.code, []).append(item)
    trends = []
    for code, values in grouped.items():
        values.sort(key=lambda x: x.observed_at)
        if len(values) < 2 or values[0].value is None or values[-1].value is None: continue
        delta = values[-1].value - values[0].value
        trends.append({"code": code, "display": values[-1].display, "absolute_change": round(delta, 2), "direction": "stable" if abs(delta) < 0.01 else ("increasing" if delta > 0 else "decreasing"), "references": [values[0].id, values[-1].id]})
    return {"overall_summary": "Longitudinal review of approved synthetic clinical facts.", "recent_developments": [], "improving_indicators": [x for x in trends if x["direction"] == "decreasing"], "stable_indicators": [x for x in trends if x["direction"] == "stable"], "worsening_indicators": [x for x in trends if x["direction"] == "increasing"], "missing_or_conflicting_information": [] if observations else ["insufficient_data"], "limitations": ["Research prototype", "Trend direction is not a diagnosis"], "simulated": True}

