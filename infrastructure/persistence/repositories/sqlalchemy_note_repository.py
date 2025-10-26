"""SQLAlchemy implementation of NoteRepository."""

from typing import List, Optional
from sqlalchemy.orm import Session, joinedload

from domain.repositories.note_repository import NoteRepository
from domain.entities.note import Note, NoteReason
from infrastructure.persistence.models import NoteModel as NoteORM, NoteReasonModel as NoteReasonORM
from infrastructure.persistence.mappers.note_mapper import NoteMapper, NoteReasonMapper


class SqlAlchemyNoteRepository(NoteRepository):
    """Concrete repository implementation using SQLAlchemy."""

    def __init__(self, session: Session):
        self._session = session

    def save(self, note: Note) -> Note:
        """Persist a new note."""
        model = NoteMapper.to_model(note)
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)

        # Load the reason relationship
        self._session.refresh(model, ['reason'])

        return NoteMapper.to_domain(model)

    def find_by_id(self, note_id: int) -> Optional[Note]:
        """Find note by ID."""
        model = self._session.query(NoteORM).options(
            joinedload(NoteORM.reason)
        ).filter(
            NoteORM.id == note_id
        ).one_or_none()

        return NoteMapper.to_domain(model) if model else None

    def find_by_lead_id(self, lead_id: int) -> List[Note]:
        """Find all notes for a lead."""
        models = self._session.query(NoteORM).options(
            joinedload(NoteORM.reason)
        ).filter(
            NoteORM.lead_id == lead_id
        ).all()

        return [NoteMapper.to_domain(m) for m in models]

    def find_reason_by_name(self, name: str) -> Optional[NoteReason]:
        """Find note reason by name."""
        model = self._session.query(NoteReasonORM).filter(
            NoteReasonORM.name == name
        ).one_or_none()

        return NoteReasonMapper.to_domain(model) if model else None

    def get_all_reasons(self) -> List[NoteReason]:
        """Get all available note reasons."""
        models = self._session.query(NoteReasonORM).all()
        return [NoteReasonMapper.to_domain(m) for m in models]
