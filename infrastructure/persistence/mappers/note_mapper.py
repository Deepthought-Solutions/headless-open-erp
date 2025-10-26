"""Note mapper - converts between domain entity and ORM model."""

from domain.entities.note import Note, NoteReason
from infrastructure.persistence.models import NoteModel as NoteORM, NoteReasonModel as NoteReasonORM


class NoteReasonMapper:
    """Maps between NoteReason domain value object and NoteReason ORM."""

    @staticmethod
    def to_domain(model: NoteReasonORM) -> NoteReason:
        """Convert ORM model to domain value object."""
        if not model:
            return None

        return NoteReason(
            id=model.id,
            name=model.name
        )

    @staticmethod
    def to_model(entity: NoteReason) -> NoteReasonORM:
        """Convert domain value object to ORM model."""
        if not entity:
            return None

        return NoteReasonORM(
            id=entity.id,
            name=entity.name
        )


class NoteMapper:
    """Maps between Note domain entity and Note ORM."""

    @staticmethod
    def to_domain(model: NoteORM) -> Note:
        """Convert ORM model to domain entity."""
        if not model:
            return None

        return Note(
            id=model.id,
            note=model.note,
            created_at=model.created_at,
            author_name=model.author_name,
            lead_id=model.lead_id,
            reason=NoteReasonMapper.to_domain(model.reason) if model.reason else None
        )

    @staticmethod
    def to_model(entity: Note) -> NoteORM:
        """Convert domain entity to ORM model."""
        if not entity:
            return None

        return NoteORM(
            id=entity.id,
            note=entity.note,
            created_at=entity.created_at,
            author_name=entity.author_name,
            lead_id=entity.lead_id,
            reason_id=entity.reason.id if entity.reason else None
        )
