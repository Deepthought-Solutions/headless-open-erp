import pytest
from unittest.mock import patch, MagicMock
from domain.orm import Lead, LeadModificationLog, Fingerprint
from application.lead_service import LeadService
from domain.contact import LeadUpdateRequest, LeadPayload
from infrastructure.database import SessionLocal

@pytest.fixture
def lead_service():
    from infrastructure.persistence.repositories.sqlalchemy_lead_repository import SqlAlchemyLeadRepository
    from infrastructure.persistence.repositories.sqlalchemy_contact_repository import SqlAlchemyContactRepository
    from infrastructure.persistence.repositories.sqlalchemy_company_repository import SqlAlchemyCompanyRepository
    from infrastructure.persistence.repositories.sqlalchemy_position_repository import SqlAlchemyPositionRepository
    from infrastructure.persistence.repositories.sqlalchemy_concern_repository import SqlAlchemyConcernRepository
    from infrastructure.persistence.repositories.sqlalchemy_note_repository import SqlAlchemyNoteRepository
    from domain.services.lead_scoring_service import LeadScoringService

    db = SessionLocal()
    lead_repository = SqlAlchemyLeadRepository(db)
    contact_repository = SqlAlchemyContactRepository(db)
    company_repository = SqlAlchemyCompanyRepository(db)
    position_repository = SqlAlchemyPositionRepository(db)
    concern_repository = SqlAlchemyConcernRepository(db)
    note_repository = SqlAlchemyNoteRepository(db)
    scoring_service = LeadScoringService()

    yield LeadService(
        db,
        lead_repository,
        contact_repository,
        company_repository,
        position_repository,
        concern_repository,
        note_repository,
        scoring_service
    )
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
