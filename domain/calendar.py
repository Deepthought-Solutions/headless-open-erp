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

class CalendarSchema(BaseModel):
    id: int
    name: str
    created_at: datetime
    events: List[EventSchema] = []

    class Config:
        orm_mode = True
