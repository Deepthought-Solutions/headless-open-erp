import uuid
from icalendar import Calendar as iCalCalendar
from sqlalchemy.orm import Session
from domain.orm import Calendar, Event
from domain.calendar import CalendarCreateSchema, EventCreateSchema, EventUpdateSchema
from datetime import datetime

class CalendarService:
    def __init__(self, db: Session):
        self.db = db

    def create_calendar(self, calendar_data: "CalendarCreateSchema") -> Calendar:
        db_calendar = Calendar(name=calendar_data.name)
        self.db.add(db_calendar)
        self.db.commit()
        self.db.refresh(db_calendar)
        return db_calendar

    def create_calendar_from_ical(self, ical_data: str, calendar_name: str) -> Calendar:
        cal = iCalCalendar.from_ical(ical_data)

        # Create a new calendar
        db_calendar = Calendar(name=calendar_name)
        self.db.add(db_calendar)
        self.db.commit()
        self.db.refresh(db_calendar)

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
        calendar = self.db.query(Calendar).filter(Calendar.id == calendar_id).first()
        if not calendar:
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
        event = self.get_event_by_uid(event_uid)
        if not event or event.calendar_id != calendar_id:
            return None

        for key, value in event_data.model_dump(exclude_unset=True).items():
            setattr(event, key, value)

        self.db.commit()
        self.db.refresh(event)
        return event

    def delete_event(self, calendar_id: int, event_uid: str) -> bool:
        event = self.get_event_by_uid(event_uid)
        if not event or event.calendar_id != calendar_id:
            return False

        self.db.delete(event)
        self.db.commit()
        return True
