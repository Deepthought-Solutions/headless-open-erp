"""SQLAlchemy implementation of CompanyRepository."""

from typing import Optional
from sqlalchemy.orm import Session

from domain.repositories.company_repository import CompanyRepository
from domain.entities.company import Company
from infrastructure.persistence.models import CompanyModel as CompanyORM
from infrastructure.persistence.mappers.company_mapper import CompanyMapper


class SqlAlchemyCompanyRepository(CompanyRepository):
    """Concrete repository implementation using SQLAlchemy."""

    def __init__(self, session: Session):
        self._session = session

    def save(self, company: Company) -> Company:
        """Persist a new or updated company."""
        existing_model = self._session.query(CompanyORM).filter(
            CompanyORM.id == company.id
        ).one_or_none() if company.id else None

        if existing_model:
            # Update existing
            existing_model.name = company.name
            existing_model.size = company.size
            model = existing_model
        else:
            model = CompanyMapper.to_model(company)
            self._session.add(model)

        self._session.commit()
        self._session.refresh(model)
        return CompanyMapper.to_domain(model)

    def find_by_name(self, name: str) -> Optional[Company]:
        """Find company by name."""
        model = self._session.query(CompanyORM).filter(
            CompanyORM.name == name
        ).one_or_none()

        return CompanyMapper.to_domain(model) if model else None

    def find_by_id(self, company_id: int) -> Optional[Company]:
        """Find company by ID."""
        model = self._session.query(CompanyORM).filter(
            CompanyORM.id == company_id
        ).one_or_none()

        return CompanyMapper.to_domain(model) if model else None

    def update(self, company: Company) -> Company:
        """Update existing company."""
        return self.save(company)
