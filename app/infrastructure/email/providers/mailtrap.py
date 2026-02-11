import smtplib
from asyncio import to_thread
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings
from app.infrastructure.email.base import EmailService


class MailtrapEmailService(EmailService):
    def __init__(self):
        self.smtp_user = settings.MAILTRAP_USER
        self.smtp_password = settings.MAILTRAP_SMTP_PASSWORD
        self.smtp_host = settings.MAILTRAP_SMTP_HOST
        self.smtp_port = settings.MAILTRAP_SMTP_PORT

        if not self.smtp_user or not self.smtp_password:
            raise ValueError("Mailtrap credentials are not configured")

    async def send(
        self,
        to: str,
        subject: str,
        body: str,
        html: str | None = None,
    ) -> None:
        msg = MIMEMultipart()
        msg["From"] = f"{settings.MAIL_FROM_NAME} <{settings.MAIL_FROM_EMAIL}>"
        msg["To"] = to
        msg["Subject"] = subject

        if html:
            msg.attach(MIMEText(html, "html"))
        else:
            msg.attach(MIMEText(body, "plain"))

        def send_email():
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

        await to_thread(send_email)
