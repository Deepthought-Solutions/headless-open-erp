import pytest
from fastapi.testclient import TestClient
import sys
import os

# Set ALTCHA_HMAC_KEY before importing the app
os.environ.setdefault('ALTCHA_HMAC_KEY', 'test-hmac-key-for-altcha')

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from infrastructure.web.app import app, get_current_user
from infrastructure.web.auth import oauth2_scheme, TokenData
from domain.orm import Lead, Contact, Company, Position, Concern, LeadPosition, LeadConcern, LeadUrgency, LeadStatus, NoteReason, Fingerprint, Report, LeadModificationLog

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
    db.query(LeadModificationLog).delete()
    db.query(LeadPosition).delete()
    db.query(LeadConcern).delete()
    db.query(Lead).delete()
    db.query(Report).delete()
    db.query(Fingerprint).delete()
    db.query(Contact).delete()
    db.query(Company).delete()
    db.query(Position).delete()
    db.query(Concern).delete()
    db.commit()
    db.close()
