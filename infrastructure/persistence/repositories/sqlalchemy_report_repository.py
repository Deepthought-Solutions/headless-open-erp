"""SQLAlchemy implementation of ReportRepository."""

from typing import List, Optional
from sqlalchemy.orm import Session

from domain.repositories.report_repository import ReportRepository
from domain.entities.report import Report
from infrastructure.persistence.models import ReportModel as ReportORM
from infrastructure.persistence.mappers.report_mapper import ReportMapper


class SqlAlchemyReportRepository(ReportRepository):
    """Concrete repository implementation using SQLAlchemy."""

    def __init__(self, session: Session):
        self._session = session

    def save(self, report: Report) -> Report:
        """Persist a new report."""
        model = ReportMapper.to_model(report)
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return ReportMapper.to_domain(model)

    def find_by_id(self, report_id: int) -> Optional[Report]:
        """Find report by ID."""
        model = self._session.query(ReportORM).filter(
            ReportORM.id == report_id
        ).one_or_none()

        return ReportMapper.to_domain(model) if model else None

    def find_by_visitor_id(self, visitor_id: str) -> List[Report]:
        """Find all reports for a visitor."""
        models = self._session.query(ReportORM).filter(
            ReportORM.visitorId == visitor_id
        ).all()

        return [ReportMapper.to_domain(m) for m in models]
