from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class MeterReading:
    id: Optional[int]
    customer_code: str
    reading_period: str
    new_index: int
    note: str = ""
    created_at: Optional[datetime] = None
