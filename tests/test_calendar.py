import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from fastapi import status
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Set environment to pytest before importing the app
os.environ['ENV'] = 'pytest'

from infrastructure.database import Base
from infrastructure.web.app import app, get_db
from infrastructure.web.auth import get_current_user, oauth2_scheme

# Setup the Test Database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

async def override_get_current_user():
    return {"username": "testuser"}

async def override_oauth2_scheme(token: str = None):
    return "test_token"

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user
app.dependency_overrides[oauth2_scheme] = override_oauth2_scheme

@pytest_asyncio.fixture(scope="function", autouse=True)
def create_test_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.fixture(scope="session", autouse=True)
def cleanup(request):
    """Cleanup a testing database"""
    def remove_db():
        if os.path.exists("./test.db"):
            os.remove("./test.db")
    request.addfinalizer(remove_db)


@pytest.mark.asyncio
async def test_upload_calendar(client: AsyncClient):
    # Create a dummy ics file
    ics_content = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//My Calendar//EN
BEGIN:VEVENT
UID:12345
DTSTAMP:20250101T120000Z
DTSTART:20250101T130000Z
DTEND:20250101T140000Z
SUMMARY:Test Event
END:VEVENT
END:VCALENDAR
"""
    files = {'file': ('test.ics', ics_content, 'text/calendar')}
    response = await client.post("/calendars/", files=files)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "test.ics"
    assert len(data["events"]) == 1
    assert data["events"][0]["summary"] == "Test Event"

@pytest.mark.asyncio
async def test_upload_invalid_file(client: AsyncClient):
    files = {'file': ('test.txt', b'some content', 'text/plain')}
    response = await client.post("/calendars/", files=files)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Invalid file type. Please upload a .ics file."

@pytest.mark.asyncio
async def test_get_calendars(client: AsyncClient):
    # First, upload a calendar to ensure there is at least one.
    ics_content = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//My Calendar//EN
BEGIN:VEVENT
UID:123456
DTSTAMP:20250101T120000Z
DTSTART:20250101T130000Z
DTEND:20250101T140000Z
SUMMARY:Test Event for listing
END:VEVENT
END:VCALENDAR
"""
    files = {'file': ('test_for_list.ics', ics_content, 'text/calendar')}
    await client.post("/calendars/", files=files)

    response = await client.get("/calendars/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert "test_for_list.ics" in [cal["name"] for cal in data]

@pytest.mark.asyncio
async def test_get_calendar(client: AsyncClient):
    # First, upload a calendar to ensure one exists
    ics_content = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//My Calendar//EN
BEGIN:VEVENT
UID:54321
DTSTAMP:20250101T120000Z
DTSTART:20250101T150000Z
DTEND:20250101T160000Z
SUMMARY:Another Test Event
END:VEVENT
END:VCALENDAR
"""
    files = {'file': ('another_test.ics', ics_content, 'text/calendar')}
    upload_response = await client.post("/calendars/", files=files)
    assert upload_response.status_code == status.HTTP_200_OK
    calendar_id = upload_response.json()["id"]

    response = await client.get(f"/calendars/{calendar_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == calendar_id
    assert data["name"] == "another_test.ics"
    assert len(data["events"]) == 1
    assert data["events"][0]["summary"] == "Another Test Event"

@pytest.mark.asyncio
async def test_get_nonexistent_calendar(client: AsyncClient):
    response = await client.get("/calendars/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
