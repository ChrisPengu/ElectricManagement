from dataclasses import dataclass
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
