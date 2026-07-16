import asyncio

from celery import Celery
from fastapi_mail import NameEmail

from .mail import create_message, mail

c_app = Celery()

c_app.config_from_object("src.config")


@c_app.task()
def send_email(recipients: list[dict[str, str]], subject: str, body: str) -> None:
    name_emails = [NameEmail(name=r["name"], email=r["email"]) for r in recipients]
    message = create_message(recipients=name_emails, sub=subject, body=body)

    asyncio.run(mail.send_message(message=message))
