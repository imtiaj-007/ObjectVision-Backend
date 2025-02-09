from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from app.tasks.celery import celery_app
from app.configuration.config import settings
from app.tasks.taskfiles.base import BaseTask
from app.services.email_service import EmailService, EmailTemplate, EmailRecipient
from app.utils.logger import log


@celery_app.task(
    bind=True,
    base=BaseTask,
    max_retries=settings.MAX_RETRIES,
    name="tasks.email.send_email",
    queue="email",
    default_retry_delay=30,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=300,
    retry_jitter=True,
)
def send_email_task(
    self,
    to_email: Union[str, Dict[str, str], List[Dict[str, str]]],
    subject: str,
    template_name: str,
    context: Dict[str, Any],
    cc: Optional[List[Dict[str, str]]] = None,
    bcc: Optional[List[Dict[str, str]]] = None,
    attachments: Optional[List[Dict[str, str]]] = None,
) -> Dict[str, Any]:
    try:
        email_service = EmailService()
        result = email_service.send_email(
            to_email, subject, template_name, context, cc, bcc, attachments
        )
        log.info(f"Email sent successfully: {result}")
        return result
    except Exception as exc:
        log.error(f"Failed to send email: {exc}")
        raise self.retry(exc=exc)


@celery_app.task(
    bind=True,
    base=BaseTask,
    max_retries=settings.MAX_RETRIES,
    name="tasks.email.send_otp",
    queue="email",
    default_retry_delay=30,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=300,
    retry_jitter=True,
)
def send_otp_email_task(
    self, to_email: Union[str, Dict[str, Any]], otp: str, expiry_minutes: int = 10
) -> Dict[str, Any]:
    try:
        email_service = EmailService()
        if isinstance(to_email, Dict):
            to_email = EmailRecipient(**to_email)
            
        result = email_service.send_otp(to_email, otp, expiry_minutes)
        log.info(f"OTP email sent successfully: {result}")
        return result
    except Exception as exc:
        log.error(f"Failed to send OTP email: {exc}")
        raise self.retry(exc=exc)


@celery_app.task(
    bind=True,
    base=BaseTask,
    max_retries=settings.MAX_RETRIES,
    name="tasks.email.send_plan_purchase",
    queue="email",
    default_retry_delay=30,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=300,
    retry_jitter=True,
)
def send_plan_purchase_email_task(
    self,
    to_email: Union[str, Dict[str, str]],
    plan_name: str,
    amount: float,
    currency: str = "INR",
    purchase_date: Optional[datetime] = None,
    next_billing_date: Optional[datetime] = None,
) -> Dict[str, Any]:
    try:
        email_service = EmailService()
        result = email_service.send_plan_purchase(
            to_email, plan_name, amount, currency, purchase_date, next_billing_date
        )
        log.info(f"Plan purchase email sent successfully: {result}")
        return result
    except Exception as exc:
        log.error(f"Failed to send plan purchase email: {exc}")
        raise self.retry(exc=exc)


@celery_app.task(
    bind=True,
    base=BaseTask,
    max_retries=settings.MAX_RETRIES,
    name="tasks.email.send_transaction_details",
    queue="email",
    default_retry_delay=30,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=300,
    retry_jitter=True,
)
def send_transaction_email_task(
    self,
    to_email: Union[str, Dict[str, str]],
    transaction_id: str,
    details: Dict[str, Any],
    transaction_date: Optional[datetime] = None,
    status: str = "completed",
) -> Dict[str, Any]:
    try:
        email_service = EmailService()
        result = email_service.send_transaction_details(
            to_email, transaction_id, details, transaction_date, status
        )
        log.info(f"Transaction email sent successfully: {result}")
        return result
    except Exception as exc:
        log.error(f"Failed to send transaction email: {exc}")
        raise self.retry(exc=exc)


@celery_app.task(
    bind=True,
    base=BaseTask,
    max_retries=settings.MAX_RETRIES,
    name="tasks.email.send_welcome",
    queue="email",
    default_retry_delay=30,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=300,
    retry_jitter=True,
)
def send_welcome_email_task(
    self,
    to_email: Union[str, Dict[str, str]],
    context: Optional[Dict[str, Any]] = {},
) -> Dict[str, Any]:
    try:
        email_service = EmailService()
        if isinstance(to_email, Dict):
            to_email = EmailRecipient(**to_email)

        result = email_service.send_email(to_email, "Welcome to Our Platform", EmailTemplate.WELCOME)
        log.info(f"Welcome email sent successfully: {result}")
        return result
    except Exception as exc:
        log.error(f"Failed to send welcome email: {exc}")
        raise self.retry(exc=exc)


@celery_app.task(
    bind=True,
    base=BaseTask,
    max_retries=settings.MAX_RETRIES,
    name="tasks.email.send_password_reset",
    queue="email",
    default_retry_delay=30,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=300,
    retry_jitter=True,
)
def send_password_reset_email_task(
    self,
    to_email: Union[str, Dict[str, str]],
    reset_token: str,
    expiry_minutes: int = 30,
) -> Dict[str, Any]:
    try:
        email_service = EmailService()
        result = email_service.send_email(
            to_email,
            "Password Reset Request",
            EmailTemplate.PASSWORD_RESET,
            {
                "reset_token": reset_token,
                "expiry_minutes": expiry_minutes,
                "generated_at": datetime.now(),
            },
        )
        log.info(f"Password reset email sent successfully: {result}")
        return result
    except Exception as exc:
        log.error(f"Failed to send password reset email: {exc}")
        raise self.retry(exc=exc)
