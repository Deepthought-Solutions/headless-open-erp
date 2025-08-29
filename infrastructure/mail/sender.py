import smtplib
from email.mime.text import MIMEText
import os
import ssl

class EmailSender:
    def send_email(self, sender, recipient, form_data):
        if os.environ.get("ENV") != "pytest":
            body = ""
            for key, value in form_data.items():
                if key == 'concern' and isinstance(value, list):
                    body += f"{key.capitalize()}: {', '.join(value)}\\n"
                else:
                    body += f"{key.capitalize()}: {value}\\n"

            msg = MIMEText(body)
            msg["Subject"] = "New Contact Form Submission"
            msg["From"] = sender
            msg["To"] = recipient
            print("Connecting to " + os.environ.get("SMTP_HOST"))
            
            server = smtplib.SMTP_SSL(os.environ.get("SMTP_HOST"), int(os.environ.get("SMTP_PORT")), context=ssl._create_unverified_context())
            server.login(os.environ.get("SMTP_USER"), os.environ.get("SMTP_PASS"))
            server.send_message(msg)

    def send_generic_email(self, sender, recipient, subject, body):
        if os.environ.get("ENV") != "pytest":
            msg = MIMEText(body)
            msg["Subject"] = subject
            msg["From"] = sender
            msg["To"] = recipient

            server = smtplib.SMTP_SSL(os.environ.get("SMTP_HOST"), int(os.environ.get("SMTP_PORT")), context=ssl._create_unverified_context())
            server.login(os.environ.get("SMTP_USER"), os.environ.get("SMTP_PASS"))
            server.send_message(msg)
