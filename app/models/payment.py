from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class Payment:
    id: Optional[int]
    receipt_code: str
    invoice_code: str
    paid_amount: int
    payment_method: str
    payer_name: str
    collected_by_user_id: int
    note: str = ""
    paid_at: Optional[datetime] = None
