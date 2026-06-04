from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from app.models.enums import InvoiceStatus


@dataclass(slots=True)
class Invoice:
    id: Optional[int]
    invoice_code: str
    customer_code: str
    billing_period: str
    amount: int
    status: InvoiceStatus
    consumption_kwh: int = 0
    fixed_fee: int = 0
    vat_amount: int = 0
    issued_by_user_id: Optional[int] = None
    issued_at: Optional[datetime] = None
