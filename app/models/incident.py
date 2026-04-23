from dataclasses import dataclass
from datetime import date
from typing import Optional

from app.models.enums import IncidentStatus


@dataclass(slots=True)
class Incident:
    id: Optional[int]
    customer_code: str
    incident_type: str
    priority: str
    description: str
    status: IncidentStatus
    received_date: Optional[date] = None
