from sqlalchemy.orm import Session, joinedload
from domain.orm import Role, Permission, UserRoleAssignment

class RbacService:
    def __init__(self, db: Session):
        self.db = db

    def _get_role_by_name(self, role_name: str) -> Role:
        return self.db.query(Role).filter(Role.name == role_name).first()

    def grant_role_to_user_for_resource(self, user_sub: str, role_name: str, resource_name: str, resource_id: int) -> UserRoleAssignment:
        """Grants a role to a user for a specific resource instance."""
        role = self._get_role_by_name(role_name)
        if not role:
            raise ValueError(f"Role '{role_name}' not found.")

        # Avoid creating duplicate assignments
        existing_assignment = self.db.query(UserRoleAssignment).filter_by(
            user_sub=user_sub,
            role_id=role.id,
            resource_name=resource_name,
            resource_id=resource_id
        ).first()

        if existing_assignment:
            return existing_assignment

        new_assignment = UserRoleAssignment(
            user_sub=user_sub,
            role_id=role.id,
            resource_name=resource_name,
            resource_id=resource_id
        )
        self.db.add(new_assignment)
        self.db.commit()
        self.db.refresh(new_assignment)
        return new_assignment

    def revoke_role_from_user_for_resource(self, user_sub: str, role_name: str, resource_name: str, resource_id: int) -> bool:
        """Revokes a role from a user for a specific resource instance."""
        role = self._get_role_by_name(role_name)
        if not role:
            # Depending on requirements, could raise an error instead
            return False

        assignment = self.db.query(UserRoleAssignment).filter_by(
            user_sub=user_sub,
            role_id=role.id,
            resource_name=resource_name,
            resource_id=resource_id
        ).first()

        if assignment:
            self.db.delete(assignment)
            self.db.commit()
            return True

        return False

    def check_user_permission_for_resource(self, user_sub: str, permission_name: str, resource_name: str, resource_id: int) -> bool:
        """
        Checks if a user has a specific permission for a resource instance.
        This is the main function for authorization checks.
        """
        # Find all roles the user has for the given resource
        # Eagerly load roles and their permissions to avoid N+1 queries
        assignments = self.db.query(UserRoleAssignment).options(
            joinedload(UserRoleAssignment.role).joinedload(Role.permissions)
        ).filter_by(
            user_sub=user_sub,
            resource_name=resource_name,
            resource_id=resource_id
        ).all()

        if not assignments:
            return False

        # Check if any of the user's roles for this resource have the required permission
        for assignment in assignments:
            for permission in assignment.role.permissions:
                if permission.name == permission_name:
                    return True

        return False
