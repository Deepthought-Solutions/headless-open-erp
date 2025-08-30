from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class EventSchema(BaseModel):
    uid: str
    summary: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime

    class Config:
        orm_mode = True

class EventCreateSchema(BaseModel):
    summary: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime

class EventUpdateSchema(BaseModel):
    summary: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

class CalendarSchema(BaseModel):
    id: int
    name: str
    created_at: datetime
    events: List[EventSchema] = []

    class Config:
        orm_mode = True
