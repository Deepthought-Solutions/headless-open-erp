import uuid
from datetime import datetime
from icalendar import Calendar as iCalCalendar
from sqlalchemy.orm import Session
from application.rbac_service import RbacService
from domain.calendar import EventCreateSchema, EventUpdateSchema
from domain.orm import Calendar, Event


class CalendarService:
    def __init__(self, db: Session, rbac_service: RbacService):
        self.db = db
        self.rbac_service = rbac_service

    def get_calendars_for_user(self, user_sub: str) -> list[Calendar]:
        """Fetches all calendars a user has access to."""
        from domain.orm import UserRoleAssignment

        assignments = self.db.query(UserRoleAssignment).filter_by(
            user_sub=user_sub,
            resource_name="calendar"
        ).all()

        calendar_ids = {assignment.resource_id for assignment in assignments}

        if not calendar_ids:
            return []

        return self.db.query(Calendar).filter(Calendar.id.in_(calendar_ids)).all()

    def create_calendar_from_ical(self, ical_data: str, calendar_name: str, creator_id: str) -> Calendar:
        cal = iCalCalendar.from_ical(ical_data)

        # Create a new calendar
        db_calendar = Calendar(name=calendar_name, creator_id=creator_id)
        self.db.add(db_calendar)
        self.db.commit()
        self.db.refresh(db_calendar)

        # Grant owner role to the creator
        self.rbac_service.grant_role_to_user_for_resource(
            user_sub=creator_id,
            role_name="owner",
            resource_name="calendar",
            resource_id=db_calendar.id
        )

        for component in cal.walk():
            if component.name == "VEVENT":
                start_time = component.get('dtstart').dt
                end_time = component.get('dtend').dt

                # Ensure start_time and end_time are timezone-aware
                if isinstance(start_time, datetime) and start_time.tzinfo is None:
                    start_time = start_time.astimezone()
                if isinstance(end_time, datetime) and end_time.tzinfo is None:
                    end_time = end_time.astimezone()

                event = Event(
                    uid=component.get('uid'),
                    summary=component.get('summary'),
                    description=component.get('description'),
                    start_time=start_time,
                    end_time=end_time,
                    calendar_id=db_calendar.id
                )
                self.db.add(event)

        self.db.commit()
        return db_calendar

    def create_event(self, calendar_id: int, event_data: EventCreateSchema) -> Event:
        # The permission check is now done in the route dependency.
        # We can assume the user has write access here.
        calendar = self.db.query(Calendar).filter(Calendar.id == calendar_id).first()
        if not calendar:
            # This case should ideally not be hit if permission check is correct.
            return None

        new_event = Event(
            uid=str(uuid.uuid4()),
            summary=event_data.summary,
            description=event_data.description,
            start_time=event_data.start_time,
            end_time=event_data.end_time,
            calendar_id=calendar_id
        )
        self.db.add(new_event)
        self.db.commit()
        self.db.refresh(new_event)
        return new_event

    def get_event_by_uid(self, event_uid: str) -> Event:
        return self.db.query(Event).filter(Event.uid == event_uid).first()

    def update_event(self, calendar_id: int, event_uid: str, event_data: EventUpdateSchema) -> Event:
        # The permission check is now done in the route dependency.
        event = self.get_event_by_uid(event_uid)
        if not event or event.calendar_id != calendar_id:
            return None

        for key, value in event_data.model_dump(exclude_unset=True).items():
            setattr(event, key, value)

        self.db.commit()
        self.db.refresh(event)
        return event

    def delete_event(self, calendar_id: int, event_uid: str) -> bool:
        # The permission check is now done in the route dependency.
        event = self.get_event_by_uid(event_uid)
        if not event or event.calendar_id != calendar_id:
            return False

        self.db.delete(event)
        self.db.commit()
        return True
