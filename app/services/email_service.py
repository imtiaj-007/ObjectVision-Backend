import os
import httpx
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, List, Union
from pydantic import EmailStr
from jinja2 import Environment, FileSystemLoader, Template
from app.configuration.config import settings
from app.utils.logger import log


class EmailTemplate(Enum):
    OTP = "otp_email.html"
    PLAN_PURCHASE = "plan_purchase_email.html"
    TRANSACTION = "transaction_email.html"
    WELCOME = "welcome_email.html"
    PASSWORD_RESET = "password_reset_email.html"


@dataclass
class EmailRecipient:
    email: EmailStr
    name: Optional[str] = None


class EmailService:
    BREVO_API_URL: str = settings.BREVO_API_URL
    RETRY_ATTEMPTS: int = 3
    TIMEOUT_SECONDS: int = 10

    def __init__(self):
        self.api_key: str = settings.BREVO_API_KEY
        self.sender: Dict[str, str] = {
            "email": settings.EMAIL_SENDER,
            "name": settings.EMAIL_SENDER_NAME,
        }
        self.jinja_env = Environment(
            loader=FileSystemLoader(
                os.path.join(settings.BASE_DIR, "app", "templates")
            ),
            auto_reload=settings.DEBUG,
            cache_size=100,
        )
        self.jinja_env.filters.update(
            {"format_currency": self._format_currency, "format_date": self._format_date}
        )
        self._template_cache: Dict[str, Template] = {}

    @staticmethod
    def _format_currency(value: float, currency: str = "INR") -> str:
        return f"{currency} {value:,.2f}"

    @staticmethod
    def _format_date(value: datetime, format: str = "%Y-%m-%d %H:%M:%S") -> str:
        return value.strftime(format)

    def _get_template(self, template_name: str) -> Template:
        if template_name not in self._template_cache:
            self._template_cache[template_name] = self.jinja_env.get_template(
                template_name
            )
        return self._template_cache[template_name]

    def send_email(
        self,
        to_email: Union[str, EmailRecipient, List[EmailRecipient]],
        subject: str,
        template_name: Union[str, EmailTemplate],
        context: Optional[Dict[str, Any]] = {},
        cc: Optional[List[EmailRecipient]] = None,
        bcc: Optional[List[EmailRecipient]] = None,
        attachments: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        full_context = {
            "year": datetime.now().year,
            "logo_url": os.path.join(settings.BASE_DIR, "app", "public", "images", "logo.png"),
            "company_name": settings.COMPANY_NAME,
            "support_email": settings.SUPPORT_EMAIL,
            **context,
        }
        template_file = (
            template_name.value
            if isinstance(template_name, EmailTemplate)
            else template_name
        )
        html_content = self._get_template(template_file).render(full_context)

        payload = {
            "sender": self.sender,
            "to": self._prepare_recipients(to_email),
            "subject": subject,
            "htmlContent": html_content,
            **({"cc": self._prepare_recipients(cc)} if cc else {}),
            **({"bcc": self._prepare_recipients(bcc)} if bcc else {}),
            **({"attachments": attachments} if attachments else {}),
        }
        return self._send_request(headers, payload)

    def _send_request(
        self, headers: Dict[str, str], payload: Dict[str, Any], retry_count: int = 0
    ) -> Dict[str, Any]:
        try:
            with httpx.Client(timeout=self.TIMEOUT_SECONDS) as client:
                response = client.post(
                    self.BREVO_API_URL, headers=headers, json=payload
                )
                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException as e:
            if retry_count < self.RETRY_ATTEMPTS:
                return self._send_request(headers, payload, retry_count + 1)
            raise
        except httpx.HTTPStatusError as e:
            print("Brevo Error: ", e)
            log.error(f"HTTP error: {e.response.text}")
            raise
        except Exception as e:
            log.error(f"Unexpected error: {e}")
            raise

    def _prepare_recipients(
        self, recipients: Union[str, EmailRecipient, List[Union[str, EmailRecipient]]]
    ) -> List[Dict[str, str]]:
        if isinstance(recipients, str):
            return [{"email": recipients}]
        elif isinstance(recipients, EmailRecipient):
            return [{"email": recipients.email, "name": recipients.name}]
        elif isinstance(recipients, list):
            return [
                (
                    {"email": r.email, "name": r.name}
                    if isinstance(r, EmailRecipient)
                    else {"email": r}
                )
                for r in recipients
            ]
        raise ValueError("Invalid recipient format")

    def send_otp(
        self, to_email: Union[str, EmailRecipient], otp: str, expiry_minutes: int = 10
    ) -> Dict[str, Any]:
        return self.send_email(
            to_email,
            "Your Security Verification Code",
            EmailTemplate.OTP,
            {
                "otp": otp,
                "expiry_minutes": expiry_minutes,
                "generated_at": datetime.now(),
            },
        )

    def send_plan_purchase(
        self,
        to_email: Union[str, EmailRecipient],
        plan_name: str,
        amount: float,
        currency: str = "USD",
        purchase_date: Optional[datetime] = None,
        next_billing_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        return self.send_email(
            to_email,
            f"Welcome to {plan_name} Plan",
            EmailTemplate.PLAN_PURCHASE,
            {
                "plan_name": plan_name,
                "amount": amount,
                "currency": currency,
                "purchase_date": purchase_date or datetime.now(),
                "next_billing_date": next_billing_date,
            },
        )

    def send_transaction_details(
        self,
        to_email: Union[str, EmailRecipient],
        transaction_id: str,
        details: Dict[str, Any],
        transaction_date: Optional[datetime] = None,
        status: str = "completed",
    ) -> Dict[str, Any]:
        return self.send_email(
            to_email,
            f"Transaction {transaction_id} {status.title()}",
            EmailTemplate.TRANSACTION,
            {
                "transaction_id": transaction_id,
                "details": details,
                "transaction_date": transaction_date or datetime.now(),
                "status": status,
            },
        )
