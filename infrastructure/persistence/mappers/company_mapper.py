"""Company mapper - converts between domain entity and ORM model."""

from domain.entities.company import Company
from infrastructure.persistence.models import CompanyModel as CompanyORM


class CompanyMapper:
    """Maps between Company domain entity and Company ORM."""

    @staticmethod
    def to_domain(model: CompanyORM) -> Company:
        """Convert ORM model to domain entity."""
        if not model:
            return None

        return Company(
            id=model.id,
            name=model.name,
            size=model.size
        )

    @staticmethod
    def to_model(entity: Company) -> CompanyORM:
        """Convert domain entity to ORM model."""
        if not entity:
            return None

        return CompanyORM(
            id=entity.id,
            name=entity.name,
            size=entity.size
        )
