import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import sys
import os
from altcha import solve_challenge, Challenge
import base64
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from infrastructure.web.app import app, get_current_user
from infrastructure.web.auth import oauth2_scheme
from domain.orm import Lead, Contact, Company, Position, Concern, LeadPosition, LeadConcern, LeadUrgency, LeadStatus
from tests.conftest import override_get_current_user, override_oauth2_scheme

def get_altcha_payload(client):
    challenge_response = client.get('/altcha-challenge/')
    assert challenge_response.status_code == 200
    challenge_dict = challenge_response.json()
    challenge = Challenge(
        algorithm=challenge_dict["algorithm"],
        challenge=challenge_dict["challenge"],
        max_number=challenge_dict["maxNumber"],
        salt=challenge_dict["salt"],
        signature=challenge_dict["signature"],
    )
    solution = solve_challenge(challenge)
    if solution is None:
        raise Exception("Failed to solve challenge")

    payload = {
        "algorithm": challenge.algorithm,
        "challenge": challenge.challenge,
        "number": solution.number,
        "salt": challenge.salt,
        "signature": challenge.signature,
        "took": solution.took,
    }
    return base64.b64encode(json.dumps(payload).encode('utf-8')).decode('utf-8')

@pytest.mark.asyncio
async def test_create_lead_success(client):
    with patch('application.notification_service.EmailNotificationService.send_lead_notification_email') as mock_send_email:
        altcha_payload = get_altcha_payload(client)
        data = {
            "lead": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "phone": "1234567890",
                "job_title": "CEO",
                "company_name": "Doe Inc.",
                "company_size": 10,
                "positions": ["Developer", "Manager"],
                "concerns": ["PSSI", "Dev"],
                "problem_summary": "This is a test message.",
                "estimated_users": 5,
                "urgency": "ce mois",
                "conscent": True
            },
            "altcha": altcha_payload
        }
        response = client.post('/lead/', json=data)
        assert response.json() == {'message': 'Lead created successfully'}
        assert response.status_code == 200
        mock_send_email.assert_called_once()

def test_create_lead_invalid_email(client):
    altcha_payload = get_altcha_payload(client)
    data = {
        "lead": {
            "name": "John Doe",
            "email": "john.doe",
            "company_name": "Doe Inc.",
            "positions": [],
            "concerns": [],
            "urgency": "ce mois",
            "conscent": True
        },
        "altcha": altcha_payload
    }
    response = client.post('/lead/', json=data)
    assert response.status_code == 422


@pytest.mark.parametrize("note_data, expected_status, expected_response", [
    (
        {"note": "", "reason": "appel sortant"},
        400,
        {
            "error": "Bad Request",
            "message": "The following fields are required: note",
            "missing_fields": ["note"]
        }
    ),
    (
        {"note": "This is a test note.", "reason": ""},
        400,
        {
            "error": "Bad Request",
            "message": "The following fields are required: reason",
            "missing_fields": ["reason"]
        }
    ),
    (
        {"note": "", "reason": ""},
        400,
        {
            "error": "Bad Request",
            "message": "The following fields are required: note, reason",
            "missing_fields": ["note", "reason"]
        }
    ),
    (
        {"note": "This is a test note.", "reason": "invalid reason"},
        400,
        {"detail": "Reason 'invalid reason' not found"}
    )
])
def test_create_note_bad_requests(client, seed_db, note_data, expected_status, expected_response):
    from infrastructure.database import SessionLocal
    db = SessionLocal()
    lead = db.query(Lead).first()
    db.close()

    response = client.post(f"/leads/{lead.id}/notes", json=note_data)
    assert response.status_code == expected_status
    assert response.json() == expected_response

def test_create_and_get_notes(client, seed_db):
    from infrastructure.database import SessionLocal
    db = SessionLocal()
    lead = db.query(Lead).first()
    db.close()

    # Create a note
    note_data = {
        "note": "This is a test note.",
        "reason": "appel sortant"
    }
    response = client.post(f"/leads/{lead.id}/notes", json=note_data)
    assert response.status_code == 200
    created_note = response.json()
    assert created_note["note"] == "This is a test note."
    assert created_note["author_name"] == "testuser"
    assert created_note["reason"]["name"] == "appel sortant"

    # Get notes
    response = client.get(f"/leads/{lead.id}/notes")
    assert response.status_code == 200
    notes = response.json()
    assert len(notes) == 1
    assert notes[0]["note"] == "This is a test note."

@pytest.fixture
def seed_db(client):
    from infrastructure.database import SessionLocal
    db = SessionLocal()

    company = Company(name="Test Company", size=50)
    position = Position(title="Test Position")
    concern = Concern(label="Test Concern")
    contact = Contact(name="Test User", email="test@example.com", phone="123456789", job_title="Tester")
    db.add_all([company, position, concern, contact])
    db.commit()

    status = db.query(LeadStatus).filter_by(name="nouveau").one()
    urgency = db.query(LeadUrgency).filter_by(name="immédiat").one()

    lead = Lead(
        contact_id=contact.id,
        company_id=company.id,
        problem_summary="A test message",
        status_id=status.id,
        urgency_id=urgency.id
    )
    db.add(lead)
    db.commit()

    lead_position = LeadPosition(lead_id=lead.id, position_id=position.id)
    lead_concern = LeadConcern(lead_id=lead.id, concern_id=concern.id)
    db.add_all([lead_position, lead_concern])
    db.commit()

    yield

    db.query(LeadPosition).delete()
    db.query(LeadConcern).delete()
    db.query(Lead).delete()
    db.query(Contact).delete()
    db.query(Company).delete()
    db.query(Position).delete()
    db.query(Concern).delete()
    db.commit()
    db.close()

def test_list_leads_unauthenticated(client):
    app.dependency_overrides = {}
    response = client.get("/leads/")
    assert response.status_code == 401
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[oauth2_scheme] = override_oauth2_scheme

def test_list_leads_authenticated(client, seed_db):
    response = client.get("/leads/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    lead = data[0]
    assert lead["contact"]["name"] == "Test User"
    assert lead["company"]["name"] == "Test Company"
    assert lead["positions"][0]["title"] == "Test Position"

def test_create_lead_missing_data(client):
    altcha_payload = get_altcha_payload(client)
    data = {
        "lead": {
            "name": "John Doe",
            "email": "john.doe@example.com"
        },
        "altcha": altcha_payload
    }
    response = client.post('/lead/', json=data)
    assert response.status_code == 422


# GET /leads/{lead_id} endpoint tests
def test_get_lead_by_id_success(client, seed_db):
    from infrastructure.database import SessionLocal
    db = SessionLocal()
    lead = db.query(Lead).first()
    lead_id = lead.id
    db.close()

    response = client.get(f"/leads/{lead_id}")
    assert response.status_code == 200

    lead_data = response.json()
    assert lead_data["id"] == lead_id
    assert lead_data["contact"]["name"] == "Test User"
    assert lead_data["company"]["name"] == "Test Company"
    assert lead_data["problem_summary"] == "A test message"


def test_get_lead_by_id_not_found(client):
    response = client.get("/leads/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Lead not found"


def test_get_lead_unauthenticated(client, seed_db):
    from infrastructure.database import SessionLocal
    db = SessionLocal()
    lead = db.query(Lead).first()
    lead_id = lead.id
    db.close()

    # Temporarily remove auth override
    app.dependency_overrides = {}

    response = client.get(f"/leads/{lead_id}")
    assert response.status_code == 401

    # Restore auth override
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[oauth2_scheme] = override_oauth2_scheme


def test_get_lead_not_found(client):
    response = client.get("/leads/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Lead not found"


# GET /note-reasons/ endpoint tests
def test_list_note_reasons_success(client):
    response = client.get("/note-reasons/")
    assert response.status_code == 200

    reasons = response.json()
    assert len(reasons) == 5
    reason_names = {reason["name"] for reason in reasons}
    assert reason_names == {
        'appel sortant',
        'mail sortant',
        'appel entrant',
        'mail entrant',
        'rencontre'
    }


def test_list_note_reasons_unauthenticated(client):
    # Temporarily remove auth override
    app.dependency_overrides = {}

    response = client.get("/note-reasons/")
    assert response.status_code == 401

    # Restore auth override
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[oauth2_scheme] = override_oauth2_scheme
