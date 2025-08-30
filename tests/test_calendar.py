import pytest
import pytest_asyncio
from httpx import AsyncClient
from fastapi import status
import uuid

# Fixtures are now in conftest.py and test_rbac.py
from tests.test_rbac import seed_rbac_data
from infrastructure.web.app import app
from infrastructure.web.auth import TokenData, get_current_user
from application.rbac_service import RbacService
from infrastructure.database import get_db

# Helper to switch the current user for a test
def set_current_user(client: AsyncClient, username: str):
    app.dependency_overrides[get_current_user] = lambda: TokenData(username=username)

async def create_calendar(client: AsyncClient, name: str = "test.ics", user: str = "testuser") -> tuple[int, str]:
    """Helper to create a calendar for a specific user."""
    from infrastructure.web.app import get_current_user
    app.dependency_overrides[get_current_user] = lambda: TokenData(username=user)

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
    assert response.status_code == status.HTTP_200_OK, response.text
    calendar_id = response.json()["id"]
    created_event_uid = response.json()["events"][0]["uid"]
    return calendar_id, created_event_uid

@pytest.mark.asyncio
async def test_upload_calendar_creates_owner(client: AsyncClient, seed_rbac_data):
    """Test that uploading a calendar makes the uploader the owner."""
    calendar_id, _ = await create_calendar(client, user="owner_user")

    # Check permissions by trying to get the calendar as the same user
    set_current_user(client, "owner_user")
    response = await client.get(f"/calendars/{calendar_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == calendar_id

@pytest.mark.asyncio
async def test_list_calendars_shows_only_accessible(client: AsyncClient, seed_rbac_data):
    """Tests that a user can only list calendars they have access to."""
    await create_calendar(client, name="cal_A.ics", user="user_a")
    await create_calendar(client, name="cal_B.ics", user="user_b")

    set_current_user(client, "user_a")
    response_a = await client.get("/calendars/")
    assert response_a.status_code == status.HTTP_200_OK
    data_a = response_a.json()
    assert len(data_a) == 1
    assert data_a[0]["name"] == "cal_A.ics"

    set_current_user(client, "user_b")
    response_b = await client.get("/calendars/")
    assert response_b.status_code == status.HTTP_200_OK
    data_b = response_b.json()
    assert len(data_b) == 1
    assert data_b[0]["name"] == "cal_B.ics"

@pytest.mark.asyncio
async def test_calendar_permissions(client: AsyncClient, seed_rbac_data):
    """A comprehensive test of different roles and their permissions."""
    calendar_id, _ = await create_calendar(client, user="owner")

    # A different user, 'viewer_user', tries to access it and fails
    set_current_user(client, "viewer_user")
    response = await client.get(f"/calendars/{calendar_id}")
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # The owner grants 'viewer' role to the 'viewer_user'
    db_session = next(app.dependency_overrides[get_db]())
    rbac_service = RbacService(db_session)
    rbac_service.grant_role_to_user_for_resource(
        user_sub="viewer_user", role_name="viewer", resource_name="calendar", resource_id=calendar_id
    )
    db_session.close()

    # Now, the 'viewer_user' should be able to read the calendar
    response = await client.get(f"/calendars/{calendar_id}")
    assert response.status_code == status.HTTP_200_OK

    # But the 'viewer_user' should NOT be able to add an event (write operation)
    event_data = {"summary": "Viewer Event", "start_time": "2025-03-01T10:00:00Z", "end_time": "2025-03-01T11:00:00Z"}
    response = await client.post(f"/calendars/{calendar_id}/events", json=event_data)
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # Now, let's grant the 'editor' role to a new user 'editor_user'
    db_session = next(app.dependency_overrides[get_db]())
    rbac_service = RbacService(db_session)
    rbac_service.grant_role_to_user_for_resource(
        user_sub="editor_user", role_name="editor", resource_name="calendar", resource_id=calendar_id
    )
    db_session.close()

    # The 'editor_user' should be able to add an event
    set_current_user(client, "editor_user")
    event_data = {"summary": "Editor Event", "start_time": "2025-04-01T10:00:00Z", "end_time": "2025-04-01T11:00:00Z"}
    response = await client.post(f"/calendars/{calendar_id}/events", json=event_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["summary"] == "Editor Event"

@pytest.mark.asyncio
async def test_owner_can_manage_events(client: AsyncClient, seed_rbac_data):
    """Confirms that the original owner retains full control."""
    calendar_id, event_uid = await create_calendar(client, user="test_owner")
    set_current_user(client, "test_owner")

    # Update event
    update_data = {"summary": "Updated By Owner"}
    response = await client.put(f"/calendars/{calendar_id}/events/{event_uid}", json=update_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["summary"] == "Updated By Owner"

    # Delete event
    response = await client.delete(f"/calendars/{calendar_id}/events/{event_uid}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
