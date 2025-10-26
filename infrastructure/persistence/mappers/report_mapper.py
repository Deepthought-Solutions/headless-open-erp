"""Report mapper - converts between domain entity and ORM model."""

from domain.entities.report import Report
from infrastructure.persistence.models import ReportModel as ReportORM


class ReportMapper:
    """Maps between Report domain entity and Report ORM."""

    @staticmethod
    def to_domain(model: ReportORM) -> Report:
        """Convert ORM model to domain entity."""
        if not model:
            return None

        return Report(
            id=model.id,
            visitor_id=model.visitorId,
            page=model.page,
            created_at=model.created_at
        )

    @staticmethod
    def to_model(entity: Report) -> ReportORM:
        """Convert domain entity to ORM model."""
        if not entity:
            return None

        return ReportORM(
            id=entity.id,
            visitorId=entity.visitor_id,
            page=entity.page,
            created_at=entity.created_at
        )
