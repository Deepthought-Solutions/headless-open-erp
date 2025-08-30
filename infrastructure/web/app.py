import logging
import sys
from typing import List
from pydantic import BaseModel
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from application.notification_service import EmailNotificationService
from application.contact_service import LeadService
from application.note_service import NoteService
from application.fingerprint_service import FingerprintService
from application.report_service import ReportService
from application.calendar_service import CalendarService
from infrastructure.mail.sender import EmailSender
from domain.contact import LeadRequest, ReportRequest, FingerprintRequest, LeadResponse, NoteCreateRequest, NoteResponse, NoteReasonResponse
from domain.calendar import CalendarSchema, EventSchema, EventCreateSchema, EventUpdateSchema
from infrastructure.web.auth import get_current_user, oauth2_scheme
from dotenv import load_dotenv
import os
from altcha import create_challenge, verify_solution
from sqlalchemy.orm import Session
from fastapi import UploadFile, File
from infrastructure.database import SessionLocal
from domain.orm import Report, Fingerprint, NoteReason, Calendar

from run_migrations import run_migrations

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout,
)
logger = logging.getLogger("api app")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger.handlers = []  # Nettoie les handlers existants
logger.addHandler(handler)

logger.propagate = False

app = FastAPI(
    title="Octobre API",
    version="v1",
    openapi_url="/api/docs/openapi.json",
    docs_url="/api/docs"
)

origins = os.environ.get('AUTHORIZED_ORIGINS', '').split(',')
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAIL_RECIPIENT = os.environ.get('MAIL_FROM')
MAIL_SENDER = os.environ.get('MAIL_TO')
ALTCHA_HMAC_KEY = os.environ.get('ALTCHA_HMAC_KEY')

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_email_sender() -> EmailSender:
    return EmailSender()

def get_email_notification_service(email_sender: EmailSender = Depends(get_email_sender)) -> EmailNotificationService:
    return EmailNotificationService(email_sender)

def get_lead_service(db: Session = Depends(get_db)) -> LeadService:
    return LeadService(db)

def get_note_service(
    db: Session = Depends(get_db),
    email_notification_service: EmailNotificationService = Depends(get_email_notification_service)
) -> NoteService:
    return NoteService(db, email_notification_service)

def get_fingerprint_service(db: Session = Depends(get_db)) -> FingerprintService:
    return FingerprintService(db)

def get_report_service(db: Session = Depends(get_db)) -> ReportService:
    return ReportService(db)

def get_calendar_service(db: Session = Depends(get_db)) -> CalendarService:
    return CalendarService(db)

def verify_altcha_solution(altcha_solution: str):
    if os.environ.get("ENV") != "pytest":
        if not ALTCHA_HMAC_KEY:
            raise HTTPException(status_code=500, detail="ALTCHA_HMAC_KEY not configured")

        is_valid, reason = verify_solution(altcha_solution, ALTCHA_HMAC_KEY)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid ALTCHA solution: {reason}")

@app.get("/altcha-challenge/")
async def altcha_challenge():
    if not ALTCHA_HMAC_KEY:
        raise HTTPException(status_code=500, detail="ALTCHA_HMAC_KEY not configured")
    challenge = create_challenge(hmac_key=ALTCHA_HMAC_KEY)
    return JSONResponse(content=challenge.to_dict())

@app.post("/lead/")
async def create_lead(
    lead_request: LeadRequest,
    lead_service: LeadService = Depends(get_lead_service),
    email_notification_service: EmailNotificationService = Depends(get_email_notification_service)
):
    logger.info("start create_lead")
    verify_altcha_solution(lead_request.altcha)

    try:
        lead_service.create_lead(lead_request.lead)
        try:
            email_notification_service.send_lead_notification_email(
                MAIL_SENDER,
                MAIL_RECIPIENT,
                lead_request.lead.model_dump()
            )
        except Exception as e:
            logger.exception("Mail notification failed")
        return JSONResponse(status_code=200, content={'message': 'Lead created successfully'})
    except Exception as e:
        logger.exception("Error creating lead")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/fingerprint/")
async def create_fingerprint(
    fingerprint_request: FingerprintRequest,
    fingerprint_service: FingerprintService = Depends(get_fingerprint_service)
):
    verify_altcha_solution(fingerprint_request.altcha)

    try:
        fingerprint_service.create_fingerprint(
            visitor_id=fingerprint_request.visitorId,
            components=fingerprint_request.components
        )
        return JSONResponse(status_code=200, content={'message': 'Fingerprint saved successfully'})
    except Exception as e:
        logger.exception("Error creating fingerprint")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/report/")
async def report_data(
    report_request: ReportRequest,
    report_service: ReportService = Depends(get_report_service)
):
    verify_altcha_solution(report_request.altcha)

    try:
        report = report_service.create_report(
            visitor_id=report_request.visitorId,
            page=report_request.page
        )
        if not report:
            return JSONResponse(status_code=200, content={'warning': 'Fingerprint not found'})
        return JSONResponse(status_code=200, content={'message': 'Report saved successfully'})
    except Exception as e:
        logger.exception("Error reporting data")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/note-reasons/", response_model=List[NoteReasonResponse], dependencies=[Depends(oauth2_scheme)])
async def list_note_reasons(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        reasons = db.query(NoteReason).all()
        return reasons
    except Exception as e:
        logger.exception("Error while getting note reasons")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/leads/", response_model=List[LeadResponse], dependencies=[Depends(oauth2_scheme)])
async def list_leads(
    lead_service: LeadService = Depends(get_lead_service),
    current_user: dict = Depends(get_current_user)
):
    try:
        leads = lead_service.get_all_leads()
        return leads
    except Exception as e:
        print("error catch")
        logger.exception("Error while getting all leads")
        raise e

@app.get("/leads/{lead_id}", response_model=LeadResponse, dependencies=[Depends(oauth2_scheme)])
async def get_lead(
    lead_id: int,
    lead_service: LeadService = Depends(get_lead_service),
    current_user: dict = Depends(get_current_user)
):
    try:
        lead = lead_service.get_lead_by_id(lead_id)
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        return lead
    except Exception as e:
        logger.exception(f"Error while getting lead {lead_id}")
        # Reraise the HTTPException to ensure FastAPI handles it
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/leads/{lead_id}/notes", response_model=NoteResponse, dependencies=[Depends(oauth2_scheme)])
async def create_note_for_lead(
    lead_id: int,
    note_request: NoteCreateRequest,
    lead_service: LeadService = Depends(get_lead_service),
    note_service: NoteService = Depends(get_note_service),
    current_user: dict = Depends(get_current_user)
):
    missing_fields = []
    if not note_request.note:
        missing_fields.append("note")
    if not note_request.reason:
        missing_fields.append("reason")

    if missing_fields:
        message = f"The following fields are required: {', '.join(missing_fields)}"
        return JSONResponse(
            status_code=400,
            content={
                "error": "Bad Request",
                "message": message,
                "missing_fields": missing_fields,
            },
        )

    try:
        lead = lead_service.get_lead_by_id(lead_id)
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")

        note = note_service.create_note(lead, note_request, current_user.username)
        return note
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Error while creating note for lead {lead_id}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/leads/{lead_id}/notes", response_model=List[NoteResponse], dependencies=[Depends(oauth2_scheme)])
async def get_notes_for_lead(
    lead_id: int,
    note_service: NoteService = Depends(get_note_service),
    current_user: dict = Depends(get_current_user)
):
    try:
        notes = note_service.get_notes_by_lead_id(lead_id)
        return notes
    except Exception as e:
        logger.exception(f"Error while getting notes for lead {lead_id}")
        raise HTTPException(status_code=500, detail="Internal server error")

class NoteUpdate(BaseModel):
    notes: str

@app.put("/leads/{lead_id}/notes", response_model=LeadResponse, dependencies=[Depends(oauth2_scheme)])
async def update_lead_notes_endpoint(
    lead_id: int,
    note_update: NoteUpdate,
    lead_service: LeadService = Depends(get_lead_service),
    current_user: dict = Depends(get_current_user)
):
    try:
        lead = lead_service.update_lead_notes(lead_id, note_update.notes)
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        return lead
    except Exception as e:
        logger.exception(f"Error while updating notes for lead {lead_id}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/calendars/", response_model=CalendarSchema, dependencies=[Depends(oauth2_scheme)])
async def upload_calendar(
    file: UploadFile = File(...),
    calendar_service: CalendarService = Depends(get_calendar_service),
    current_user: dict = Depends(get_current_user)
):
    if not file.filename.endswith('.ics'):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a .ics file.")

    try:
        ical_data = await file.read()
        calendar = calendar_service.create_calendar_from_ical(ical_data.decode('utf-8'), file.filename)
        return calendar
    except Exception as e:
        logger.exception("Error while creating calendar")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/calendars/", response_model=List[CalendarSchema], dependencies=[Depends(oauth2_scheme)])
async def list_calendars(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        calendars = db.query(Calendar).all()
        return calendars
    except Exception as e:
        logger.exception("Error while getting all calendars")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/calendars/{calendar_id}", response_model=CalendarSchema, dependencies=[Depends(oauth2_scheme)])
async def get_calendar(
    calendar_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        calendar = db.query(Calendar).filter(Calendar.id == calendar_id).first()
        if not calendar:
            raise HTTPException(status_code=404, detail="Calendar not found")
        return calendar
    except Exception as e:
        logger.exception(f"Error while getting calendar {calendar_id}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/calendars/{calendar_id}/events", response_model=EventSchema, dependencies=[Depends(oauth2_scheme)])
async def create_event(
    calendar_id: int,
    event_data: EventCreateSchema,
    calendar_service: CalendarService = Depends(get_calendar_service),
    current_user: dict = Depends(get_current_user)
):
    try:
        event = calendar_service.create_event(calendar_id, event_data)
        if not event:
            raise HTTPException(status_code=404, detail="Calendar not found")
        return event
    except Exception as e:
        logger.exception(f"Error while creating event for calendar {calendar_id}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail="Internal server error")

@app.put("/calendars/{calendar_id}/events/{event_uid}", response_model=EventSchema, dependencies=[Depends(oauth2_scheme)])
async def update_event(
    calendar_id: int,
    event_uid: str,
    event_data: EventUpdateSchema,
    calendar_service: CalendarService = Depends(get_calendar_service),
    current_user: dict = Depends(get_current_user)
):
    try:
        event = calendar_service.update_event(calendar_id, event_uid, event_data)
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        return event
    except Exception as e:
        logger.exception(f"Error while updating event {event_uid}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail="Internal server error")

@app.delete("/calendars/{calendar_id}/events/{event_uid}", status_code=204, dependencies=[Depends(oauth2_scheme)])
async def delete_event(
    calendar_id: int,
    event_uid: str,
    calendar_service: CalendarService = Depends(get_calendar_service),
    current_user: dict = Depends(get_current_user)
):
    try:
        success = calendar_service.delete_event(calendar_id, event_uid)
        if not success:
            raise HTTPException(status_code=404, detail="Event not found")
        return
    except Exception as e:
        logger.exception(f"Error while deleting event {event_uid}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == '__main__':
    # Run migrations on startup, but not in the test environment
    # because they are handled by the playwright global setup.
    if os.environ.get("ENV") != "pytest":
        run_migrations()

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
