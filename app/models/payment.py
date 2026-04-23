from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class Payment:
    id: Optional[int]
    invoice_code: str
    paid_amount: int
    payment_method: str
    paid_at: Optional[datetime] = None
