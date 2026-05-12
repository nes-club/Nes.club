import logging
import re

from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives

log = logging.getLogger(__name__)


def send_transactional_email(recipient, subject, html, **kwargs):
    log.info(f"Sending transactional email to {recipient}")
    prepared_html = prepare_letter(html, base_url=settings.APP_HOST)
    try:
        return send_mail(
            subject=subject,
            html_message=prepared_html,
            message=re.sub(r"<[^>]+>", "", prepared_html),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
        )
    except Exception as e:
        log.error(f"Failed to send transactional email to {recipient}: {e}")
        return 0


def send_mass_email(recipient, subject, html, unsubscribe_link):
    log.info(f"Sending mass email to {recipient}")
    prepared_html = prepare_letter(html, base_url=settings.APP_HOST)
    email = EmailMultiAlternatives(
        subject=subject,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient],
        headers={
            "List-Unsubscribe": unsubscribe_link
        }
    )
    email.attach_alternative(prepared_html, "text/html")
    email.content_subtype = "html"
    return email.send(fail_silently=True)


def prepare_letter(html, base_url):
    if "<!doctype" not in html:
        html = f"<!doctype html>{html}"
    return html
