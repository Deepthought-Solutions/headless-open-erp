import pytest
from fastapi.testclient import TestClient
import sys
import os
from altcha import solve_challenge, Challenge
import base64
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from infrastructure.web.app import app, get_current_user
from infrastructure.web.auth import oauth2_scheme, TokenData
from domain.orm import Fingerprint, Report

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
    from domain.orm import LeadStatus, LeadUrgency, RecommendedPack, NoteReason

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
def clean_fingerprint_report_tables():
    from infrastructure.database import SessionLocal
    db = SessionLocal()
    db.query(Report).delete()
    db.query(Fingerprint).delete()
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


# Fingerprint endpoint tests
def test_create_fingerprint_success(client):
    altcha_payload = get_altcha_payload(client)
    data = {
        "altcha": altcha_payload,
        "visitorId": "test-visitor-123",
        "components": {
            "userAgent": "Mozilla/5.0",
            "platform": "Linux",
            "screenResolution": "1920x1080"
        }
    }

    response = client.post('/fingerprint/', json=data)
    assert response.status_code == 200
    assert response.json() == {'message': 'Fingerprint saved successfully'}

    # Verify fingerprint was saved
    from infrastructure.database import SessionLocal
    db = SessionLocal()
    fingerprint = db.query(Fingerprint).filter_by(visitorId="test-visitor-123").first()
    assert fingerprint is not None
    assert fingerprint.visitorId == "test-visitor-123"
    db.close()


def test_create_fingerprint_duplicate_visitor_id(client):
    """Test that creating a fingerprint with the same visitor_id updates the existing one"""
    altcha_payload = get_altcha_payload(client)

    # Create first fingerprint
    data1 = {
        "altcha": altcha_payload,
        "visitorId": "duplicate-visitor",
        "components": {
            "userAgent": "Mozilla/5.0",
            "platform": "Linux"
        }
    }
    response1 = client.post('/fingerprint/', json=data1)
    assert response1.status_code == 200

    # Create second fingerprint with same visitor_id but different components
    altcha_payload2 = get_altcha_payload(client)
    data2 = {
        "altcha": altcha_payload2,
        "visitorId": "duplicate-visitor",
        "components": {
            "userAgent": "Chrome",
            "platform": "Windows"
        }
    }
    response2 = client.post('/fingerprint/', json=data2)
    assert response2.status_code == 200

    # Verify only one fingerprint exists and it's been updated
    from infrastructure.database import SessionLocal
    db = SessionLocal()
    fingerprints = db.query(Fingerprint).filter_by(visitorId="duplicate-visitor").all()
    assert len(fingerprints) == 1
    db.close()


def test_create_fingerprint_missing_visitor_id(client):
    altcha_payload = get_altcha_payload(client)
    data = {
        "altcha": altcha_payload,
        "components": {}
    }

    response = client.post('/fingerprint/', json=data)
    assert response.status_code == 422  # Validation error


def test_create_fingerprint_missing_altcha(client):
    data = {
        "visitorId": "test-visitor",
        "components": {}
    }

    response = client.post('/fingerprint/', json=data)
    assert response.status_code == 422  # Validation error


# Report endpoint tests
def test_create_report_success(client):
    # First create a fingerprint
    from infrastructure.database import SessionLocal
    db = SessionLocal()
    fingerprint = Fingerprint(visitorId="test-visitor-report", components={})
    db.add(fingerprint)
    db.commit()
    db.close()

    # Now create a report
    altcha_payload = get_altcha_payload(client)
    data = {
        "altcha": altcha_payload,
        "visitorId": "test-visitor-report",
        "page": "/products/item-123"
    }

    response = client.post('/report/', json=data)
    assert response.status_code == 200
    assert response.json() == {'message': 'Report saved successfully'}

    # Verify report was saved
    db = SessionLocal()
    report = db.query(Report).filter_by(page="/products/item-123").first()
    assert report is not None
    assert report.fingerprint.visitorId == "test-visitor-report"
    db.close()


def test_create_report_fingerprint_not_found(client):
    """Test creating a report when fingerprint doesn't exist returns warning"""
    altcha_payload = get_altcha_payload(client)
    data = {
        "altcha": altcha_payload,
        "visitorId": "nonexistent-visitor",
        "page": "/some/page"
    }

    response = client.post('/report/', json=data)
    assert response.status_code == 200
    assert response.json() == {'warning': 'Fingerprint not found'}

    # Verify report was NOT saved
    from infrastructure.database import SessionLocal
    db = SessionLocal()
    report = db.query(Report).filter_by(page="/some/page").first()
    assert report is None
    db.close()


def test_create_report_missing_visitor_id(client):
    altcha_payload = get_altcha_payload(client)
    data = {
        "altcha": altcha_payload,
        "page": "/page"
    }

    response = client.post('/report/', json=data)
    assert response.status_code == 422  # Validation error


def test_create_report_missing_page(client):
    altcha_payload = get_altcha_payload(client)
    data = {
        "altcha": altcha_payload,
        "visitorId": "test-visitor"
    }

    response = client.post('/report/', json=data)
    assert response.status_code == 422  # Validation error


def test_create_report_missing_altcha(client):
    data = {
        "visitorId": "test-visitor",
        "page": "/page"
    }

    response = client.post('/report/', json=data)
    assert response.status_code == 422  # Validation error


def test_create_multiple_reports_for_same_fingerprint(client):
    """Test that multiple reports can be created for the same fingerprint"""
    # Create fingerprint
    from infrastructure.database import SessionLocal
    db = SessionLocal()
    fingerprint = Fingerprint(visitorId="multi-report-visitor", components={})
    db.add(fingerprint)
    db.commit()
    db.close()

    # Create first report
    altcha_payload1 = get_altcha_payload(client)
    data1 = {
        "altcha": altcha_payload1,
        "visitorId": "multi-report-visitor",
        "page": "/page1"
    }
    response1 = client.post('/report/', json=data1)
    assert response1.status_code == 200

    # Create second report
    altcha_payload2 = get_altcha_payload(client)
    data2 = {
        "altcha": altcha_payload2,
        "visitorId": "multi-report-visitor",
        "page": "/page2"
    }
    response2 = client.post('/report/', json=data2)
    assert response2.status_code == 200

    # Verify both reports exist
    db = SessionLocal()
    reports = db.query(Report).join(Fingerprint).filter(
        Fingerprint.visitorId == "multi-report-visitor"
    ).all()
    assert len(reports) == 2
    pages = {report.page for report in reports}
    assert pages == {"/page1", "/page2"}
    db.close()


