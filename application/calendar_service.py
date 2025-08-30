from icalendar import Calendar as iCalCalendar
from sqlalchemy.orm import Session
from domain.orm import Calendar, Event
from datetime import datetime

class CalendarService:
    def __init__(self, db: Session):
        self.db = db

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
