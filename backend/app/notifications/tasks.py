from app.core.celery_app import celery_app


@celery_app.task(name="enterpriseos.notifications.send_email")
def send_email_notification(
    tenant_id: str,
    user_id: str,
    subject: str,
    body: str,
) -> dict:
    """Send email notification. SMTP integration deferred to Phase 6."""
    # Phase 1b: log intent; production wires SMTP/SES in Phase 6
    return {
        "status": "queued",
        "tenant_id": tenant_id,
        "user_id": user_id,
        "subject": subject,
        "body_preview": body[:100],
    }
