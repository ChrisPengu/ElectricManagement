"""Compatibility layer for older imports.

Prefer importing from `app.models` or from the specific model module.
"""

from app.models.customer import Customer
from app.models.enums import ContractType, IncidentStatus, InvoiceStatus
from app.models.incident import Incident
from app.models.invoice import Invoice
from app.models.meter_reading import MeterReading
from app.models.payment import Payment
from app.models.tariff import TariffConfig
from app.models.user import UserAccount

__all__ = [
    "ContractType",
    "InvoiceStatus",
    "IncidentStatus",
    "UserAccount",
    "Customer",
    "TariffConfig",
    "MeterReading",
    "Invoice",
    "Payment",
    "Incident",
]
