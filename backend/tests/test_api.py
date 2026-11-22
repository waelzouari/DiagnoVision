from datetime import date
import uuid

def test_auth_and_csrf(client, auth):
    assert client.get("/api/v1/auth/me").status_code == 200
    denied = client.post("/api/v1/patients", json={"name": "Synthetic Test", "date_of_birth": "1990-01-01"})
    assert denied.status_code == 403

def test_patient_vertical_slice(client, auth):
    created = client.post("/api/v1/patients", headers=auth, json={"name": "Synthetic Test Patient", "date_of_birth": "1990-01-01", "medical_history": "Fictional"})
    assert created.status_code == 201
    patient_id = created.json()["id"]
    listing = client.get("/api/v1/patients").json()
    assert any(item["id"] == patient_id for item in listing["items"])
    consultation = client.post(f"/api/v1/patients/{patient_id}/consultations", headers=auth, json={"mode": "manual", "manual_notes": "Patient reports fatigue and denies chest pain. Blood pressure 128/82. Follow-up soon."})
    assert consultation.status_code == 201
    consultation_id = consultation.json()["id"]
    extracted = client.post(f"/api/v1/consultations/{consultation_id}/extract", headers=auth)
    assert extracted.status_code == 202
    approved = client.post(f"/api/v1/consultations/{consultation_id}/approve", headers=auth)
    assert approved.status_code == 200
    observations = client.get(f"/api/v1/patients/{patient_id}/observations").json()
    assert len(observations) == 2
    analysis = client.post(f"/api/v1/patients/{patient_id}/analyze", headers=auth)
    assert analysis.status_code == 202

def test_audio_requires_consent(client, auth):
    patient_id = client.get("/api/v1/patients").json()["items"][0]["id"]
    consultation_id = client.post(f"/api/v1/patients/{patient_id}/consultations", headers=auth, json={"mode": "audio"}).json()["id"]
    result = client.post(f"/api/v1/consultations/{consultation_id}/audio", headers=auth, files={"file": ("demo.wav", b"RIFFsynthetic", "audio/wav")})
    assert result.status_code == 409
    client.post(f"/api/v1/consultations/{consultation_id}/consent", headers=auth, json={"granted": True})
    result = client.post(f"/api/v1/consultations/{consultation_id}/audio", headers=auth, files={"file": ("demo.wav", b"RIFFsynthetic", "audio/wav")})
    assert result.status_code == 201

def test_cross_doctor_patient_is_hidden(client, auth):
    assert client.get("/api/v1/patients/not-a-real-id").status_code == 404


def test_dashboard_returns_only_authorized_approved_observations(client, auth):
    overview = client.get("/api/v1/dashboard/overview")
    assert overview.status_code == 200
    payload = overview.json()
    assert payload["patient_count"] >= 1
    assert "relevant_observations" in payload
    assert len(payload["relevant_observations"]) <= 12
    assert all(item["approved"] is True for item in payload["relevant_observations"])

    visible_patient_ids = {
        item["id"] for item in client.get("/api/v1/patients", params={"page_size": 100}).json()["items"]
    }
    assert all(
        item["patient_id"] in visible_patient_ids
        for item in payload["relevant_observations"]
    )


def test_patient_search_trend_sort_and_pagination(client, auth):
    first = client.get(
        "/api/v1/patients",
        params={"sort_by": "name", "sort_order": "asc", "page": 1, "page_size": 2},
    )
    assert first.status_code == 200
    payload = first.json()
    assert len(payload["items"]) == 2
    assert payload["items"] == sorted(payload["items"], key=lambda item: (item["name"], item["id"]))
    second = client.get("/api/v1/patients", params={"page": 2, "page_size": 2}).json()
    assert {item["id"] for item in payload["items"]}.isdisjoint(item["id"] for item in second["items"])

    stable = client.get("/api/v1/patients", params={"trend": "stable"})
    assert stable.status_code == 200
    assert any(item["name"] == "Noura Trabelsi" for item in stable.json()["items"])

    escaped_wildcard = client.get("/api/v1/patients", params={"search": "%"})
    assert escaped_wildcard.status_code == 200
    assert escaped_wildcard.json()["total"] == 0
    assert client.get("/api/v1/patients", params={"page_size": 0}).status_code == 422
    assert client.get("/api/v1/patients", params={"sort_by": "unknown"}).status_code == 422


def test_observation_filters_and_bounds(client, auth):
    listing = client.get("/api/v1/patients", params={"search": "Leila Mansour"}).json()
    patient_id = listing["items"][0]["id"]
    all_items = client.get(f"/api/v1/patients/{patient_id}/observations").json()
    assert len(all_items) >= 3
    code_items = client.get(
        f"/api/v1/patients/{patient_id}/observations",
        params={"code": "8480-6", "sort_order": "desc", "limit": 2},
    ).json()
    assert len(code_items) == 2
    assert all(item["code"] == "8480-6" for item in code_items)
    assert code_items[0]["observed_at"] >= code_items[1]["observed_at"]
    assert client.get(
        f"/api/v1/patients/{patient_id}/observations",
        params={"code": "does-not-exist"},
    ).json() == []
    invalid_dates = client.get(
        f"/api/v1/patients/{patient_id}/observations",
        params={"date_from": "2026-12-01T00:00:00Z", "date_to": "2026-01-01T00:00:00Z"},
    )
    assert invalid_dates.status_code == 422
    assert client.get(
        f"/api/v1/patients/{patient_id}/observations", params={"limit": 501}
    ).status_code == 422


def test_timeline_consultation_document_and_analysis_filters(client, auth):
    patient_id = client.get("/api/v1/patients").json()["items"][0]["id"]
    consultation = client.post(
        f"/api/v1/patients/{patient_id}/consultations",
        headers=auth,
        json={"mode": "manual", "manual_notes": "Synthetic filtering fixture"},
    )
    assert consultation.status_code == 201
    consultation_id = consultation.json()["id"]

    filtered = client.get(
        f"/api/v1/patients/{patient_id}/consultations",
        params={"mode": "manual", "status": "draft", "limit": 1},
    )
    assert filtered.status_code == 200
    assert len(filtered.json()) == 1
    assert filtered.json()[0]["mode"] == "manual"
    assert client.get(
        f"/api/v1/patients/{patient_id}/consultations", params={"mode": "fax"}
    ).status_code == 422

    timeline = client.get(
        f"/api/v1/patients/{patient_id}/timeline",
        params={"event_type": "consultation", "status": "draft"},
    )
    assert timeline.status_code == 200
    assert all(item["type"] == "consultation" and item["status"] == "draft" for item in timeline.json())
    assert client.get(
        f"/api/v1/patients/{patient_id}/timeline", params={"event_type": "invalid"}
    ).status_code == 422

    assert client.get(
        f"/api/v1/patients/{patient_id}/documents", params={"status": "approved"}
    ).json() == []
    run = client.post(f"/api/v1/patients/{patient_id}/analyze", headers=auth)
    assert run.status_code == 202
    analyses = client.get(
        f"/api/v1/patients/{patient_id}/analyses",
        params={"status": "completed", "reviewed": False, "limit": 1},
    )
    assert analyses.status_code == 200
    assert len(analyses.json()) == 1
    assert analyses.json()[0]["reviewed"] is False


def test_cross_patient_filter_isolation(client, auth):
    from app.database import SessionLocal
    from app.models import Doctor, Observation, Patient, PatientAccess
    from app.security import hash_password

    db = SessionLocal()
    try:
        foreign_doctor = Doctor(
            email=f"foreign-filter-test-{uuid.uuid4()}@diagnovision.local",
            full_name="Dr. Foreign",
            password_hash=hash_password("Foreign123!"),
        )
        foreign_patient = Patient(name="Hidden Filter Patient", date_of_birth=date(1988, 2, 2))
        db.add_all([foreign_doctor, foreign_patient])
        db.flush()
        db.add(PatientAccess(doctor_id=foreign_doctor.id, patient_id=foreign_patient.id))
        db.add(
            Observation(
                patient_id=foreign_patient.id,
                code="SECRET",
                display="Hidden observation",
                value=99,
                unit="x",
                source_reference="synthetic:foreign",
            )
        )
        db.commit()
        hidden_id = foreign_patient.id
    finally:
        db.close()

    search = client.get("/api/v1/patients", params={"search": "Hidden Filter Patient"})
    assert search.status_code == 200
    assert search.json()["total"] == 0
    assert client.get(f"/api/v1/patients/{hidden_id}/observations", params={"code": "SECRET"}).status_code == 404
    assert client.get(f"/api/v1/patients/{hidden_id}/timeline").status_code == 404
    assert client.get(f"/api/v1/patients/{hidden_id}/documents").status_code == 404
    assert client.get(f"/api/v1/patients/{hidden_id}/analyses").status_code == 404

