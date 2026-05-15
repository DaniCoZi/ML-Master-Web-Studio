# app/services/email.py
import os
import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

logger = logging.getLogger(__name__)

def send_contact_email(name: str, email: str, subject: str, message: str) -> bool:
    api_key = os.environ.get("SENDGRID_API_KEY")
    from_email = os.environ.get("SENDGRID_FROM_EMAIL", "noreply@revelu.com")
    to_email = os.environ.get("CONTACT_EMAIL", from_email)

    if not api_key:
        logger.warning("SENDGRID_API_KEY no configurada.")
        return False

    body = f"""
Nuevo mensaje de contacto desde Revelu:

Nombre:   {name}
Correo:   {email}
Asunto:   {subject}

Mensaje:
{message}
    """.strip()

    mail = Mail(
        from_email=from_email,
        to_emails=to_email,
        subject=f"[Revelu Contact] {subject}",
        plain_text_content=body,
    )

    try:
        sg = SendGridAPIClient(api_key)
        response = sg.send(mail)
        logger.info("Email enviado, status: %s", response.status_code)
        return response.status_code in (200, 202)
    except Exception as e:
        logger.error("Error enviando email: %s", e)
        return False
