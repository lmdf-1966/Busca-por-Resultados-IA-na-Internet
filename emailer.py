
import os, smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

def send_mail(subject: str, body: str) -> bool:
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER")
    pw   = os.getenv("SMTP_PASS")
    mail_from = os.getenv("MAIL_FROM", user or "")
    mail_to   = os.getenv("MAIL_TO", "")

    if not (host and user and pw and mail_from and mail_to):
        return False

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = formataddr(("IA Digest Agent", mail_from))
    msg["To"] = mail_to

    with smtplib.SMTP(host, port) as s:
        s.starttls()
        s.login(user, pw)
        s.send_message(msg)
    return True
