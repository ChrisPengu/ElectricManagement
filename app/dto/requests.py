from dataclasses import dataclass


@dataclass(slots=True)
class LoginRequestDTO:
    username: str
    password: str


@dataclass(slots=True)
class CustomerCreateDTO:
    customer_code: str
    owner_name: str
    address: str
    phone_number: str
    contract_type: str


@dataclass(slots=True)
class CustomerUpdateDTO:
    customer_code: str
    owner_name: str
    address: str
    phone_number: str
    contract_type: str


@dataclass(slots=True)
class TariffUpsertDTO:
    contract_type: str
    fixed_fee: int
    vat_percent: float
    peak_multiplier: float
    base_rate: int
    formula_note: str


@dataclass(slots=True)
class MeterReadingCreateDTO:
    customer_code: str
    reading_period: str
    new_index: int
    note: str = ""


@dataclass(slots=True)
class InvoiceCreateDTO:
    invoice_code: str
    customer_code: str
    billing_period: str
    amount: int
    status: str


@dataclass(slots=True)
class PaymentCreateDTO:
    invoice_code: str
    paid_amount: int
    payment_method: str


@dataclass(slots=True)
class IncidentCreateDTO:
    customer_code: str
    incident_type: str
    priority: str
    description: str
    status: str
