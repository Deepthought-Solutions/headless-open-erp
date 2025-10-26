import pytest
from unittest.mock import patch
from domain.orm import Lead, LeadModificationLog, Fingerprint
from application.lead_service import LeadService
from domain.contact import LeadUpdateRequest, LeadPayload
from infrastructure.database import SessionLocal

@pytest.fixture
def lead_service():
    db = SessionLocal()
    yield LeadService(db)
    db.close()

def test_create_lead_with_fingerprint_and_altcha(lead_service, client):
    # First, create a fingerprint
    fingerprint_data = {
        "visitorId": "test-visitor-id",
        "components": {"test": "data"}
    }
    fingerprint = Fingerprint(**fingerprint_data)
    db = SessionLocal()
    db.add(fingerprint)
    db.commit()
    db.close()

    lead_payload = LeadPayload(
        name="Test Lead",
        email="test-lead-service-create@example.com",
        company_name="Test Company",
        positions=["Developer"],
        concerns=["PSSI"],
        urgency="ce mois",
        conscent=True
    )
    altcha_solution = "test-altcha-solution"
    visitor_id = "test-visitor-id"

    lead = lead_service.create_lead(lead_payload, altcha_solution, visitor_id)

    assert lead is not None
    assert lead.altcha_solution == altcha_solution
    assert lead.fingerprint_visitor_id == visitor_id

def test_update_lead_success(lead_service, client):
    # First, create a lead with a fingerprint and altcha
    fingerprint_data = {
        "visitorId": "test-visitor-id-update",
        "components": {"test": "data"}
    }
    fingerprint = Fingerprint(**fingerprint_data)
    db = SessionLocal()
    db.add(fingerprint)
    db.commit()

    lead_payload = LeadPayload(
        name="Test Lead",
        email="test-lead-service-update@example.com",
        company_name="Test Company",
        positions=["Developer"],
        concerns=["PSSI"],
        urgency="ce mois",
        conscent=True
    )
    altcha_solution = "test-altcha-solution-update"
    visitor_id = "test-visitor-id-update"
    lead = lead_service.create_lead(lead_payload, altcha_solution, visitor_id)
    db.close()

    # Now, update the lead
    update_data = LeadUpdateRequest(
        name="Updated Lead Name",
        altcha=altcha_solution,
        visitorId=visitor_id
    )
    updated_lead = lead_service.update_lead(lead.id, update_data)

    assert updated_lead is not None
    assert updated_lead.contact.name == "Updated Lead Name"

    # Check that the change was logged
    db = SessionLocal()
    log_entry = db.query(LeadModificationLog).filter_by(lead_id=lead.id).first()
    assert log_entry is not None
    assert log_entry.field_name == "name"
    assert log_entry.old_value == "Test Lead"
    assert log_entry.new_value == "Updated Lead Name"
    db.close()

def test_update_lead_invalid_fingerprint(lead_service, client):
    # First, create a lead with a fingerprint and altcha
    fingerprint_data = {
        "visitorId": "test-visitor-id-invalid",
        "components": {"test": "data"}
    }
    fingerprint = Fingerprint(**fingerprint_data)
    db = SessionLocal()
    db.add(fingerprint)
    db.commit()

    lead_payload = LeadPayload(
        name="Test Lead",
        email="test-lead-service-invalid@example.com",
        company_name="Test Company",
        positions=["Developer"],
        concerns=["PSSI"],
        urgency="ce mois",
        conscent=True
    )
    altcha_solution = "test-altcha-solution-invalid"
    visitor_id = "test-visitor-id-invalid"
    lead = lead_service.create_lead(lead_payload, altcha_solution, visitor_id)
    db.close()

    # Now, try to update the lead with an invalid fingerprint
    update_data = LeadUpdateRequest(
        name="Updated Lead Name",
        altcha=altcha_solution,
        visitorId="invalid-visitor-id"
    )

    with pytest.raises(ValueError, match="Fingerprint or Altcha solution does not match."):
        lead_service.update_lead(lead.id, update_data)
