from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class UserDTO:
    id: Optional[int]
    username: str
    role: str
    display_name: str
    is_active: bool


@dataclass(slots=True)
class CustomerDTO:
    id: Optional[int]
    customer_code: str
    owner_name: str
    address: str
    phone_number: str
    contract_type: str


@dataclass(slots=True)
class TariffConfigDTO:
    id: Optional[int]
    contract_type: str
    fixed_fee: int
    vat_percent: float
    peak_multiplier: float
    base_rate: int
    formula_note: str
    updated_at: str


@dataclass(slots=True)
class MeterReadingDTO:
    id: Optional[int]
    customer_code: str
    reading_period: str
    new_index: int
    note: str
    created_at: str


@dataclass(slots=True)
class InvoiceDTO:
    id: Optional[int]
    invoice_code: str
    customer_code: str
    billing_period: str
    amount: int
    status: str


@dataclass(slots=True)
class PaymentDTO:
    id: Optional[int]
    receipt_code: str
    invoice_code: str
    paid_amount: int
    payment_method: str
    payer_name: str
    collected_by_user_id: int
    note: str
    paid_at: str


@dataclass(slots=True)
class IncidentDTO:
    id: Optional[int]
    customer_code: str
    incident_type: str
    priority: str
    description: str
    status: str
    received_date: str
