import pytest
from fastapi.testclient import TestClient
import sys
import os
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from infrastructure.web.app import app, get_current_user
from infrastructure.web.auth import oauth2_scheme, TokenData
from domain.orm import EmailAccount, ClassifiedEmail, EmailClassificationHistory, Lead, Contact, Company, LeadStatus, LeadUrgency

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
def clean_email_tables():
    from infrastructure.database import SessionLocal
    db = SessionLocal()
    db.query(EmailClassificationHistory).delete()
    db.query(ClassifiedEmail).delete()
    db.query(EmailAccount).delete()
    db.commit()
    db.close()


# Email Account API Tests
def test_create_email_account_success(client):
    data = {
        "name": "Test IMAP Account",
        "imap_host": "imap.example.com",
        "imap_port": 993,
        "imap_username": "user@example.com",
        "imap_password": "securepassword",
        "imap_use_ssl": True
    }

    response = client.post("/email-accounts/", json=data)
    assert response.status_code == 200

    result = response.json()
    assert result["name"] == "Test IMAP Account"
    assert result["imap_host"] == "imap.example.com"
    assert result["imap_port"] == 993
    assert result["imap_username"] == "user@example.com"
    assert result["imap_use_ssl"] is True
    assert "imap_password" not in result  # Password should not be in response
    assert "id" in result
    assert "created_at" in result


def test_create_email_account_missing_fields(client):
    data = {
        "name": "Test Account"
        # Missing required fields
    }

    response = client.post("/email-accounts/", json=data)
    assert response.status_code == 422


def test_list_email_accounts(client):
    # Create two accounts
    client.post("/email-accounts/", json={
        "name": "Account 1",
        "imap_host": "imap1.example.com",
        "imap_port": 993,
        "imap_username": "user1@example.com",
        "imap_password": "pass1"
    })
    client.post("/email-accounts/", json={
        "name": "Account 2",
        "imap_host": "imap2.example.com",
        "imap_port": 993,
        "imap_username": "user2@example.com",
        "imap_password": "pass2"
    })

    response = client.get("/email-accounts/")
    assert response.status_code == 200

    accounts = response.json()
    assert len(accounts) == 2
    assert accounts[0]["name"] == "Account 1"
    assert accounts[1]["name"] == "Account 2"


def test_get_email_account_by_id(client):
    # Create an account
    create_response = client.post("/email-accounts/", json={
        "name": "Test Account",
        "imap_host": "imap.example.com",
        "imap_port": 993,
        "imap_username": "user@example.com",
        "imap_password": "password"
    })
    account_id = create_response.json()["id"]

    # Get the account
    response = client.get(f"/email-accounts/{account_id}")
    assert response.status_code == 200

    account = response.json()
    assert account["id"] == account_id
    assert account["name"] == "Test Account"


def test_get_email_account_not_found(client):
    response = client.get("/email-accounts/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Email account not found"


def test_update_email_account(client):
    # Create an account
    create_response = client.post("/email-accounts/", json={
        "name": "Original Name",
        "imap_host": "imap.example.com",
        "imap_port": 993,
        "imap_username": "user@example.com",
        "imap_password": "password"
    })
    account_id = create_response.json()["id"]

    # Update the account
    update_data = {
        "name": "Updated Name",
        "imap_port": 143
    }
    response = client.put(f"/email-accounts/{account_id}", json=update_data)
    assert response.status_code == 200

    updated = response.json()
    assert updated["name"] == "Updated Name"
    assert updated["imap_port"] == 143
    assert updated["imap_host"] == "imap.example.com"  # Unchanged


def test_delete_email_account(client):
    # Create an account
    create_response = client.post("/email-accounts/", json={
        "name": "To Delete",
        "imap_host": "imap.example.com",
        "imap_port": 993,
        "imap_username": "user@example.com",
        "imap_password": "password"
    })
    account_id = create_response.json()["id"]

    # Delete the account
    response = client.delete(f"/email-accounts/{account_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Email account deleted successfully"

    # Verify deletion
    get_response = client.get(f"/email-accounts/{account_id}")
    assert get_response.status_code == 404


# Classified Email API Tests
def test_create_classified_email_success(client):
    # First create an email account
    account_response = client.post("/email-accounts/", json={
        "name": "Test Account",
        "imap_host": "imap.example.com",
        "imap_port": 993,
        "imap_username": "user@example.com",
        "imap_password": "password"
    })
    account_id = account_response.json()["id"]

    # Create classified email
    email_data = {
        "email_account_id": account_id,
        "imap_id": "12345",
        "sender": "sender@example.com",
        "recipients": "recipient1@example.com,recipient2@example.com",
        "subject": "Test Email Subject",
        "email_date": "2025-10-25T10:00:00Z",
        "classification": "sales_inquiry",
        "emergency_level": 3,
        "abstract": "This is a test email abstract"
    }

    response = client.post("/classified-emails/", json=email_data)
    assert response.status_code == 200

    result = response.json()
    assert result["imap_id"] == "12345"
    assert result["sender"] == "sender@example.com"
    assert result["classification"] == "sales_inquiry"
    assert result["emergency_level"] == 3
    assert result["abstract"] == "This is a test email abstract"


def test_create_classified_email_invalid_emergency_level(client):
    # Create account first
    account_response = client.post("/email-accounts/", json={
        "name": "Test Account",
        "imap_host": "imap.example.com",
        "imap_port": 993,
        "imap_username": "user@example.com",
        "imap_password": "password"
    })
    account_id = account_response.json()["id"]

    # Try to create email with invalid emergency level
    email_data = {
        "email_account_id": account_id,
        "imap_id": "12345",
        "sender": "sender@example.com",
        "recipients": "recipient@example.com",
        "emergency_level": 6  # Invalid: must be 1-5
    }

    response = client.post("/classified-emails/", json=email_data)
    assert response.status_code == 400
    assert "Emergency level must be between 1 and 5" in response.json()["detail"]


def test_create_classified_email_abstract_too_long(client):
    # Create account first
    account_response = client.post("/email-accounts/", json={
        "name": "Test Account",
        "imap_host": "imap.example.com",
        "imap_port": 993,
        "imap_username": "user@example.com",
        "imap_password": "password"
    })
    account_id = account_response.json()["id"]

    # Try to create email with abstract > 200 chars
    email_data = {
        "email_account_id": account_id,
        "imap_id": "12345",
        "sender": "sender@example.com",
        "recipients": "recipient@example.com",
        "abstract": "x" * 201
    }

    response = client.post("/classified-emails/", json=email_data)
    assert response.status_code == 400
    assert "Abstract must be 200 characters or less" in response.json()["detail"]


def test_list_classified_emails(client):
    # Create account
    account_response = client.post("/email-accounts/", json={
        "name": "Test Account",
        "imap_host": "imap.example.com",
        "imap_port": 993,
        "imap_username": "user@example.com",
        "imap_password": "password"
    })
    account_id = account_response.json()["id"]

    # Create two emails
    client.post("/classified-emails/", json={
        "email_account_id": account_id,
        "imap_id": "1",
        "sender": "sender1@example.com",
        "recipients": "recipient@example.com",
        "classification": "sales",
        "emergency_level": 2
    })
    client.post("/classified-emails/", json={
        "email_account_id": account_id,
        "imap_id": "2",
        "sender": "sender2@example.com",
        "recipients": "recipient@example.com",
        "classification": "support",
        "emergency_level": 5
    })

    # List all emails
    response = client.get("/classified-emails/")
    assert response.status_code == 200
    emails = response.json()
    assert len(emails) == 2


def test_list_classified_emails_with_filters(client):
    # Create account
    account_response = client.post("/email-accounts/", json={
        "name": "Test Account",
        "imap_host": "imap.example.com",
        "imap_port": 993,
        "imap_username": "user@example.com",
        "imap_password": "password"
    })
    account_id = account_response.json()["id"]

    # Create emails with different emergency levels
    client.post("/classified-emails/", json={
        "email_account_id": account_id,
        "imap_id": "1",
        "sender": "sender@example.com",
        "recipients": "recipient@example.com",
        "emergency_level": 5
    })
    client.post("/classified-emails/", json={
        "email_account_id": account_id,
        "imap_id": "2",
        "sender": "sender@example.com",
        "recipients": "recipient@example.com",
        "emergency_level": 1
    })

    # Filter by emergency level
    response = client.get("/classified-emails/?emergency_level=5")
    assert response.status_code == 200
    emails = response.json()
    assert len(emails) == 1
    assert emails[0]["emergency_level"] == 5


def test_get_classified_email_by_id_with_history(client):
    # Create account
    account_response = client.post("/email-accounts/", json={
        "name": "Test Account",
        "imap_host": "imap.example.com",
        "imap_port": 993,
        "imap_username": "user@example.com",
        "imap_password": "password"
    })
    account_id = account_response.json()["id"]

    # Create email
    create_response = client.post("/classified-emails/", json={
        "email_account_id": account_id,
        "imap_id": "12345",
        "sender": "sender@example.com",
        "recipients": "recipient@example.com",
        "classification": "initial",
        "emergency_level": 2
    })
    email_id = create_response.json()["id"]

    # Update classification (creates history)
    client.put(f"/classified-emails/{email_id}", json={
        "classification": "updated",
        "emergency_level": 4,
        "change_reason": "LLM re-evaluation"
    })

    # Get email with history
    response = client.get(f"/classified-emails/{email_id}")
    assert response.status_code == 200

    email = response.json()
    assert email["classification"] == "updated"
    assert email["emergency_level"] == 4
    assert "classification_history" in email
    assert len(email["classification_history"]) == 1
    assert email["classification_history"][0]["classification"] == "initial"
    assert email["classification_history"][0]["emergency_level"] == 2


def test_update_classified_email(client):
    # Create account and email
    account_response = client.post("/email-accounts/", json={
        "name": "Test Account",
        "imap_host": "imap.example.com",
        "imap_port": 993,
        "imap_username": "user@example.com",
        "imap_password": "password"
    })
    account_id = account_response.json()["id"]

    create_response = client.post("/classified-emails/", json={
        "email_account_id": account_id,
        "imap_id": "12345",
        "sender": "sender@example.com",
        "recipients": "recipient@example.com",
        "classification": "old",
        "emergency_level": 1
    })
    email_id = create_response.json()["id"]

    # Update classification
    update_data = {
        "classification": "new",
        "emergency_level": 5,
        "change_reason": "Re-classified by LLM"
    }
    response = client.put(f"/classified-emails/{email_id}", json=update_data)
    assert response.status_code == 200

    updated = response.json()
    assert updated["classification"] == "new"
    assert updated["emergency_level"] == 5


def test_delete_classified_email(client):
    # Create account and email
    account_response = client.post("/email-accounts/", json={
        "name": "Test Account",
        "imap_host": "imap.example.com",
        "imap_port": 993,
        "imap_username": "user@example.com",
        "imap_password": "password"
    })
    account_id = account_response.json()["id"]

    create_response = client.post("/classified-emails/", json={
        "email_account_id": account_id,
        "imap_id": "12345",
        "sender": "sender@example.com",
        "recipients": "recipient@example.com"
    })
    email_id = create_response.json()["id"]

    # Delete email
    response = client.delete(f"/classified-emails/{email_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Classified email deleted successfully"

    # Verify deletion
    get_response = client.get(f"/classified-emails/{email_id}")
    assert get_response.status_code == 404


def test_classified_email_with_lead_relationship(client):
    from infrastructure.database import SessionLocal

    # Create a lead first
    db = SessionLocal()
    contact = Contact(name="Test Contact", email="contact@example.com")
    company = Company(name="Test Company", size=100)
    db.add_all([contact, company])
    db.commit()

    status = db.query(LeadStatus).filter_by(name="nouveau").first()
    urgency = db.query(LeadUrgency).filter_by(name="immédiat").first()

    lead = Lead(
        contact_id=contact.id,
        company_id=company.id,
        status_id=status.id,
        urgency_id=urgency.id
    )
    db.add(lead)
    db.commit()
    lead_id = lead.id
    db.close()

    # Create account and email with lead relationship
    account_response = client.post("/email-accounts/", json={
        "name": "Test Account",
        "imap_host": "imap.example.com",
        "imap_port": 993,
        "imap_username": "user@example.com",
        "imap_password": "password"
    })
    account_id = account_response.json()["id"]

    response = client.post("/classified-emails/", json={
        "email_account_id": account_id,
        "imap_id": "12345",
        "sender": "sender@example.com",
        "recipients": "recipient@example.com",
        "lead_id": lead_id
    })

    assert response.status_code == 200
    email = response.json()
    assert email["lead_id"] == lead_id


def test_email_accounts_require_authentication(client):
    # Temporarily remove auth override
    app.dependency_overrides = {}

    response = client.get("/email-accounts/")
    assert response.status_code == 401

    # Restore auth override
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[oauth2_scheme] = override_oauth2_scheme


def test_classified_emails_require_authentication(client):
    # Temporarily remove auth override
    app.dependency_overrides = {}

    response = client.get("/classified-emails/")
    assert response.status_code == 401

    # Restore auth override
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[oauth2_scheme] = override_oauth2_scheme
