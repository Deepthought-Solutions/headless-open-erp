from pydantic import BaseModel
from typing import List, Optional

# --- Permission Schemas ---
class PermissionBase(BaseModel):
    name: str

class PermissionCreate(PermissionBase):
    pass

class PermissionSchema(PermissionBase):
    id: int

    class Config:
        orm_mode = True

# --- Role Schemas ---
class RoleBase(BaseModel):
    name: str

class RoleCreate(RoleBase):
    pass

class RoleSchema(RoleBase):
    id: int
    permissions: List[PermissionSchema] = []

    class Config:
        orm_mode = True

# --- UserRoleAssignment Schemas ---
class UserRoleAssignmentBase(BaseModel):
    user_sub: str
    resource_name: str
    resource_id: int

# This will be the input for the grant endpoint
class GrantRequestSchema(UserRoleAssignmentBase):
    role_name: str

# This will be the response schema
class UserRoleAssignmentSchema(UserRoleAssignmentBase):
    id: int
    role: RoleSchema

    class Config:
        orm_mode = True
