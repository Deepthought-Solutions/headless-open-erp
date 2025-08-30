import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from fastapi import status
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import uuid

os.environ['ENV'] = 'pytest'
os.environ['ALTCHA_HMAC_KEY'] = 'test-key'

from infrastructure.database import Base
from infrastructure.web.app import app, get_db
from infrastructure.web.auth import get_current_user, oauth2_scheme, TokenData

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
    return TokenData(username="testuser")

@pytest_asyncio.fixture
async def client():
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[oauth2_scheme] = lambda: "fake-token"

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides = {}

@pytest_asyncio.fixture(scope="function", autouse=True)
def create_test_database(client: AsyncClient): # Depends on client to ensure overrides are set
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


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

async def create_calendar(client: AsyncClient, name: str = "test.ics") -> tuple[int, str]:
    event_uid = str(uuid.uuid4())
    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//My Calendar//EN
BEGIN:VEVENT
UID:{event_uid}
DTSTAMP:20250101T120000Z
DTSTART:20250101T130000Z
DTEND:20250101T140000Z
SUMMARY:Initial Event
END:VEVENT
END:VCALENDAR
"""
    files = {'file': (name, ics_content, 'text/calendar')}
    response = await client.post("/calendars/", files=files)
    assert response.status_code == status.HTTP_200_OK
    calendar_id = response.json()["id"]
    created_event_uid = response.json()["events"][0]["uid"]
    return calendar_id, created_event_uid

@pytest.mark.asyncio
async def test_create_event(client: AsyncClient):
    calendar_id, _ = await create_calendar(client)
    event_data = {
        "summary": "New Event",
        "description": "A new event created via API",
        "start_time": "2025-02-01T10:00:00Z",
        "end_time": "2025-02-01T11:00:00Z"
    }
    response = await client.post(f"/calendars/{calendar_id}/events", json=event_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["summary"] == "New Event"
    assert "uid" in data

@pytest.mark.asyncio
async def test_update_event(client: AsyncClient):
    calendar_id, event_uid = await create_calendar(client)
    update_data = {"summary": "Updated Summary"}
    response = await client.put(f"/calendars/{calendar_id}/events/{event_uid}", json=update_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["summary"] == "Updated Summary"

@pytest.mark.asyncio
async def test_delete_event(client: AsyncClient):
    calendar_id, event_uid = await create_calendar(client)
    response = await client.delete(f"/calendars/{calendar_id}/events/{event_uid}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify the event is deleted
    cal_response_after_delete = await client.get(f"/calendars/{calendar_id}")
    events = cal_response_after_delete.json()["events"]
    assert all(event["uid"] != event_uid for event in events)

@pytest.mark.asyncio
async def test_update_nonexistent_event(client: AsyncClient):
    calendar_id, _ = await create_calendar(client)
    update_data = {"summary": "This should fail"}
    response = await client.put(f"/calendars/{calendar_id}/events/nonexistent-uid", json=update_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_delete_nonexistent_event(client: AsyncClient):
    calendar_id, _ = await create_calendar(client)
    response = await client.delete(f"/calendars/{calendar_id}/events/nonexistent-uid")
    assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_update_event_wrong_calendar(client: AsyncClient):
    calendar_id_a, event_uid_a = await create_calendar(client, name="cal_a.ics")
    calendar_id_b, _ = await create_calendar(client, name="cal_b.ics")

    update_data = {"summary": "This should fail"}
    response = await client.put(f"/calendars/{calendar_id_b}/events/{event_uid_a}", json=update_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_delete_event_wrong_calendar(client: AsyncClient):
    calendar_id_a, event_uid_a = await create_calendar(client, name="cal_a_2.ics")
    calendar_id_b, _ = await create_calendar(client, name="cal_b_2.ics")

    response = await client.delete(f"/calendars/{calendar_id_b}/events/{event_uid_a}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
