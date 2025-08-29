import logging
import os
from sqlalchemy.orm import Session
from domain.orm import Report

logger = logging.getLogger(__name__)

class EmailNotificationService:
    def __init__(self, email_sender):
        self.email_sender = email_sender

    def send_lead_notification_email(self, sender, recipient, form_data):
        try:
            # The EmailSender will need to be updated to handle this new data structure
            self.email_sender.send_email(sender, recipient, form_data)
        except Exception as e:
            logger.exception("Error sending lead notification email")
            raise e

    def send_note_notification(self, recipients, note, author):
        try:
            sender = os.environ.get('MAIL_SENDER')
            if not sender:
                logger.error("MAIL_SENDER environment variable not set")
                return

            subject = f"A new note has been added by {author}"
            body = f"A new note has been added:\n\n{note}"

            for recipient in recipients:
                self.email_sender.send_generic_email(sender, recipient, subject, body)
        except Exception as e:
            logger.exception("Error sending note notification email")
            raise e

class ReportService:
    def __init__(self, db: Session):
        self.db = db

    def create_report(self, fingerprint: str, page: str):
        try:
            report = Report(fingerprint=fingerprint, page=page)
            self.db.add(report)
            self.db.commit()
            self.db.refresh(report)
            return report
        except Exception as e:
            logger.exception("Error creating report")
            raise e
