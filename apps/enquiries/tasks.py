import logging
import requests
from django.conf import settings
from django.core.mail import send_mail
from django.utils.html import escape

try:
    from celery import shared_task
except ImportError:
    def shared_task(*dargs, **dkwargs):
        def decorator(fn):
            fn.delay = fn
            return fn
        if len(dargs) == 1 and callable(dargs[0]):
            fn = dargs[0]
            fn.delay = fn
            return fn
        return decorator

from apps.enquiries.models import Enquiry

logger = logging.getLogger(__name__)

@shared_task
def process_enquiry(enquiry_id: int):
    """
    Asynchronous pipeline for processing incoming corporate inquiries.
    Per page 12 & 13 of SKAD Backend Specification:
    1. Sends internal notification to designated route owners (with HTML escaping per page 19).
    2. Sends confirmation email to submitter with unique tracking reference.
    3. Pushes payload to route CRM webhook if configured.
    """
    try:
        enquiry = Enquiry.objects.select_related("route").get(id=enquiry_id)
    except Enquiry.DoesNotExist:
        logger.error(f"Enquiry ID {enquiry_id} does not exist.")
        return

    route = enquiry.route

    # Sanitize & HTML escape all user inputs per Page 19 ('escape in emails')
    safe_name = escape(enquiry.name)
    safe_email = escape(enquiry.email)
    safe_company = escape(enquiry.company or "N/A")
    safe_role = escape(enquiry.role or "N/A")
    safe_country = escape(enquiry.country)
    safe_phone = escape(enquiry.phone or "N/A")
    safe_website = escape(enquiry.company_website or "N/A")
    safe_message = escape(enquiry.message)
    safe_route_label = escape(route.label)
    safe_route_code = escape(route.code)
    safe_reference = escape(enquiry.reference)

    # 1. Send internal notification to route owners
    if route.to_emails:
        subject = f"[{enquiry.reference}] New {route.label} Enquiry: {enquiry.name}"
        message = (
            f"New enquiry received via corporate portal:\n\n"
            f"Reference: {enquiry.reference}\n"
            f"Route: {route.label} ({route.code})\n"
            f"Name: {enquiry.name}\n"
            f"Company: {enquiry.company or 'N/A'}\n"
            f"Role: {enquiry.role or 'N/A'}\n"
            f"Email: {enquiry.email}\n"
            f"Phone: {enquiry.phone or 'N/A'}\n"
            f"Country: {enquiry.country}\n"
            f"Website: {enquiry.company_website or 'N/A'}\n\n"
            f"Message:\n{enquiry.message}\n\n"
            f"View in Admin: /admin/enquiries/enquiry/{enquiry.id}/change/\n"
        )
        html_message = (
            f"<div style='font-family: sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e5e7eb; border-radius: 8px;'>"
            f"<div style='background: #0B0F19; color: #fff; padding: 16px; border-bottom: 3px solid #D4AF37;'>"
            f"<h2 style='margin:0; font-size: 16px;'>New Corporate Enquiry &bull; {safe_reference}</h2>"
            f"</div>"
            f"<div style='padding: 20px;'>"
            f"<p><strong>Route:</strong> {safe_route_label} ({safe_route_code})</p>"
            f"<p><strong>Name:</strong> {safe_name} ({safe_email})</p>"
            f"<p><strong>Company:</strong> {safe_company} &mdash; {safe_role}</p>"
            f"<p><strong>Country / Phone:</strong> {safe_country} | {safe_phone}</p>"
            f"<p><strong>Website:</strong> {safe_website}</p>"
            f"<p><strong>Message:</strong></p>"
            f"<div style='background: #f9fafb; padding: 12px; border: 1px solid #e5e7eb; border-radius: 4px; white-space: pre-wrap;'>{safe_message}</div>"
            f"</div>"
            f"</div>"
        )
        try:
            send_mail(
                subject=subject,
                message=message,
                html_message=html_message,
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@skadgroup.com"),
                recipient_list=route.to_emails,
                fail_silently=False,
            )
        except Exception as e:
            logger.warning(f"Failed to send route owner email for enquiry {enquiry.reference}: {e}")

    # 2. Send confirmation email to submitter
    confirmation_subject = f"Enquiry Confirmation - {enquiry.reference} | SKAD GROUP"
    confirmation_message = (
        f"Dear {enquiry.name},\n\n"
        f"Thank you for reaching out to SKAD GROUP regarding '{route.label}'.\n"
        f"Your enquiry has been received and routed to the appropriate department.\n\n"
        f"Tracking Reference: {enquiry.reference}\n\n"
        f"Our team will review your message and respond accordingly.\n\n"
        f"Sincerely,\n"
        f"SKAD GROUP Corporate Office\n"
        f"BUILD • CONNECT • SCALE\n"
    )
    confirmation_html = (
        f"<div style='font-family: sans-serif; max-width: 580px; margin: 0 auto; padding: 24px; border: 1px solid #e5e7eb; border-radius: 8px;'>"
        f"<div style='background: #0B0F19; color: #fff; padding: 20px; text-align: center; border-bottom: 2px solid #D4AF37;'>"
        f"<h2 style='margin:0; letter-spacing: 2px;'>SKAD GROUP</h2>"
        f"<div style='font-size: 11px; color: #D4AF37; letter-spacing: 2px; margin-top: 4px;'>BUILD &bull; CONNECT &bull; SCALE</div>"
        f"</div>"
        f"<div style='padding: 24px; line-height: 1.6; color: #374151;'>"
        f"<p>Dear {safe_name},</p>"
        f"<p>Thank you for reaching out to SKAD GROUP regarding <strong>{safe_route_label}</strong>. Your enquiry has been received and routed to our team.</p>"
        f"<div style='background: #f9fafb; border-left: 4px solid #D4AF37; padding: 12px 16px; margin: 20px 0;'>"
        f"<div style='font-size: 11px; text-transform: uppercase; color: #6b7280;'>Tracking Reference</div>"
        f"<div style='font-size: 18px; font-weight: bold; font-family: monospace; color: #0B0F19;'>{safe_reference}</div>"
        f"</div>"
        f"<p>Our executive team will review your message and connect with you shortly.</p>"
        f"<p style='margin-top: 24px;'>Sincerely,<br><strong>SKAD GROUP Corporate Office</strong></p>"
        f"</div>"
        f"</div>"
    )
    try:
        send_mail(
            subject=confirmation_subject,
            message=confirmation_message,
            html_message=confirmation_html,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@skadgroup.com"),
            recipient_list=[enquiry.email],
            fail_silently=True,
        )
    except Exception as e:
        logger.warning(f"Failed to send confirmation email for enquiry {enquiry.reference}: {e}")


    # 3. Push to CRM Webhook if configured
    if route.crm_webhook_url:
        payload = {
            "reference": enquiry.reference,
            "route_code": route.code,
            "route_label": route.label,
            "name": enquiry.name,
            "company": enquiry.company,
            "role": enquiry.role,
            "email": enquiry.email,
            "phone": enquiry.phone,
            "country": enquiry.country,
            "website": enquiry.company_website,
            "message": enquiry.message,
            "created_at": enquiry.created_at.isoformat(),
        }
        try:
            resp = requests.post(route.crm_webhook_url, json=payload, timeout=10)
            resp.raise_for_status()
        except Exception as exc:
            logger.error(f"CRM webhook push failed for {enquiry.reference}: {exc}")
