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
from infrastructure.web.auth import oauth2_scheme, TokenData
from domain.orm import Lead, Contact, Company, Position, Concern, LeadPosition, LeadConcern, LeadUrgency, LeadStatus, NoteReason

# Override the OIDC dependency for testing
async def override_get_current_user():
    return TokenData(username="testuser")

async def override_oauth2_scheme():
    return "fake-token"

app.dependency_overrides[get_current_user] = override_get_current_user
app.dependency_overrides[oauth2_scheme] = override_oauth2_scheme

@pytest.fixture(scope="session", autouse=True)
def test_db():
    from infrastructure.database import Base, engine, SessionLocal
    from domain.orm import LeadStatus, LeadUrgency, RecommendedPack
    # Set up the database
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    # Clean up enum tables before seeding
    db.query(LeadStatus).delete()
    db.query(LeadUrgency).delete()
    db.query(RecommendedPack).delete()
    db.query(NoteReason).delete()
    db.commit()

    # Seed enum tables
    db.add_all([
        NoteReason(name='appel sortant'),
        NoteReason(name='mail sortant'),
        NoteReason(name='appel entrant'),
        NoteReason(name='mail entrant'),
        NoteReason(name='rencontre'),
        LeadStatus(name='nouveau'),
        LeadStatus(name='à rappeler'),
        LeadStatus(name='relancé'),
        LeadStatus(name='proposition envoyée'),
        LeadStatus(name='gagné'),
        LeadStatus(name='perdu'),
        LeadUrgency(name='immédiat'),
        LeadUrgency(name='ce mois'),
        LeadUrgency(name='moyen terme'),
        RecommendedPack(name='conformité'),
        RecommendedPack(name='confiance'),
        RecommendedPack(name='croissance'),
    ])
    db.commit()
    db.close()

    yield
    # Tear down the database
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    from infrastructure.database import SessionLocal
    db = SessionLocal()
    yield TestClient(app)
    db.close()

@pytest.fixture(autouse=True)
def clean_db_before_each_test():
    from infrastructure.database import SessionLocal
    db = SessionLocal()
    db.query(LeadPosition).delete()
    db.query(LeadConcern).delete()
    db.query(Lead).delete()
    db.query(Contact).delete()
    db.query(Company).delete()
    db.query(Position).delete()
    db.query(Concern).delete()
    db.commit()
    db.close()

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
