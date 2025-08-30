import pytest
from sqlalchemy.orm import Session
from domain.orm import Role, Permission, RolePermission

# This fixture is auto-used by all tests to ensure RBAC roles and perms are in the DB.
@pytest.fixture(scope="function", autouse=True)
def seed_rbac_data(client): # We depend on the `client` fixture from conftest or a base file
    """Seeds the database with initial RBAC roles and permissions."""
    # The client fixture should handle db creation/teardown.
    # We just need to get a session to add our data.
    from infrastructure.database import SessionLocal
    db: Session = SessionLocal()

    try:
        # Create Permissions if they don't exist
        permissions = {
            "calendar:read": Permission(name="calendar:read"),
            "calendar:write": Permission(name="calendar:write"),
            "admin:manage": Permission(name="admin:manage")
        }
        for key, p in permissions.items():
            permissions[key] = db.merge(p)
        db.commit()

        # Create Roles if they don't exist
        roles = {
            "owner": Role(name="owner"),
            "editor": Role(name="editor"),
            "viewer": Role(name="viewer"),
            "admin": Role(name="admin")
        }
        for key, r in roles.items():
            roles[key] = db.merge(r)
        db.commit()

        # Assign Permissions to Roles, ensuring no duplicates
        role_permissions = [
            (roles["owner"], permissions["calendar:read"]),
            (roles["owner"], permissions["calendar:write"]),
            (roles["editor"], permissions["calendar:read"]),
            (roles["editor"], permissions["calendar:write"]),
            (roles["viewer"], permissions["calendar:read"]),
            (roles["admin"], permissions["admin:manage"])
        ]

        for role, perm in role_permissions:
            # Check if the relationship already exists
            exists = db.query(RolePermission).filter_by(role_id=role.id, permission_id=perm.id).first()
            if not exists:
                db.add(RolePermission(role_id=role.id, permission_id=perm.id))
        db.commit()
    finally:
        db.close()

from httpx import AsyncClient
from fastapi import status
from application.rbac_service import RbacService
from infrastructure.database import get_db
from infrastructure.web.app import app  # Import the app
from tests.test_calendar import set_current_user, create_calendar

@pytest.mark.asyncio
async def test_admin_grant_permission(client: AsyncClient, seed_rbac_data):
    """Test that an admin can grant permissions."""
    calendar_id, _ = await create_calendar(client, user="test_owner")

    db_session = next(app.dependency_overrides[get_db]())
    rbac_service = RbacService(db_session)
    rbac_service.grant_role_to_user_for_resource(
        user_sub="global_admin", role_name="admin", resource_name="global", resource_id=0
    )
    db_session.close()

    set_current_user(client, "not_an_admin")
    grant_data = {
        "user_sub": "some_user", "role_name": "viewer",
        "resource_name": "calendar", "resource_id": calendar_id
    }
    response = await client.post("/admin/grant", json=grant_data)
    assert response.status_code == status.HTTP_403_FORBIDDEN

    set_current_user(client, "global_admin")
    grant_data["user_sub"] = "new_viewer"
    response = await client.post("/admin/grant", json=grant_data)
    assert response.status_code == status.HTTP_200_OK

    set_current_user(client, "new_viewer")
    response = await client.get(f"/calendars/{calendar_id}")
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.asyncio
async def test_admin_revoke_permission(client: AsyncClient, seed_rbac_data):
    """Test that an admin can revoke permissions."""
    calendar_id, _ = await create_calendar(client, user="owner")

    db_session = next(app.dependency_overrides[get_db]())
    rbac_service = RbacService(db_session)
    rbac_service.grant_role_to_user_for_resource(
        user_sub="global_admin", role_name="admin", resource_name="global", resource_id=0
    )
    rbac_service.grant_role_to_user_for_resource(
        user_sub="temp_viewer", role_name="viewer", resource_name="calendar", resource_id=calendar_id
    )
    db_session.close()

    set_current_user(client, "temp_viewer")
    response = await client.get(f"/calendars/{calendar_id}")
    assert response.status_code == status.HTTP_200_OK

    set_current_user(client, "global_admin")
    revoke_data = {
        "user_sub": "temp_viewer", "role_name": "viewer",
        "resource_name": "calendar", "resource_id": calendar_id
    }
    response = await client.post("/admin/revoke", json=revoke_data)
    assert response.status_code == status.HTTP_200_OK

    set_current_user(client, "temp_viewer")
    response = await client.get(f"/calendars/{calendar_id}")
    assert response.status_code == status.HTTP_403_FORBIDDEN
