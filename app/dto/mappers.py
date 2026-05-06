from app.dto.requests import MeterReadingCreateDTO, TariffUpsertDTO
from app.dto.responses import (
    CustomerDTO,
    IncidentDTO,
    InvoiceDTO,
    MeterReadingDTO,
    PaymentDTO,
    TariffConfigDTO,
    UserDTO,
)
from app.models import Customer, Incident, Invoice, MeterReading, Payment, TariffConfig, UserAccount


def to_user_dto(user: UserAccount) -> UserDTO:
    return UserDTO(
        id=user.id,
        username=user.username,
        role=user.role,
        display_name=user.display_name,
        is_active=user.is_active,
    )


def to_customer_dto(customer: Customer) -> CustomerDTO:
    return CustomerDTO(
        id=customer.id,
        customer_code=customer.customer_code,
        owner_name=customer.owner_name,
        address=customer.address,
        phone_number=customer.phone_number,
        contract_type=customer.contract_type.value,
    )


def to_tariff_config_dto(config: TariffConfig) -> TariffConfigDTO:
    return TariffConfigDTO(
        id=config.id,
        contract_type=config.contract_type.value,
        fixed_fee=config.fixed_fee,
        vat_percent=config.vat_percent,
        peak_multiplier=config.peak_multiplier,
        base_rate=config.base_rate,
        formula_note=config.formula_note,
        updated_at=config.updated_at.isoformat(sep=" ", timespec="seconds"),
    )


def tariff_upsert_dto_to_payload(dto: TariffUpsertDTO) -> dict:
    return {
        "contract_type": dto.contract_type,
        "fixed_fee": dto.fixed_fee,
        "vat_percent": dto.vat_percent,
        "peak_multiplier": dto.peak_multiplier,
        "base_rate": dto.base_rate,
        "formula_note": dto.formula_note,
    }


def meter_reading_create_dto_to_payload(dto: MeterReadingCreateDTO) -> dict:
    return {
        "customer_code": dto.customer_code,
        "reading_period": dto.reading_period,
        "new_index": dto.new_index,
        "note": dto.note,
    }


def to_meter_reading_dto(reading: MeterReading) -> MeterReadingDTO:
    return MeterReadingDTO(
        id=reading.id,
        customer_code=reading.customer_code,
        reading_period=reading.reading_period,
        new_index=reading.new_index,
        note=reading.note,
        created_at=reading.created_at.isoformat(sep=" ", timespec="seconds") if reading.created_at else "",
    )


def to_payment_dto(payment: Payment) -> PaymentDTO:
    return PaymentDTO(
        id=payment.id,
        receipt_code=payment.receipt_code,
        invoice_code=payment.invoice_code,
        paid_amount=payment.paid_amount,
        payment_method=payment.payment_method,
        payer_name=payment.payer_name,
        collected_by_user_id=payment.collected_by_user_id,
        note=payment.note,
        paid_at=payment.paid_at.isoformat(sep=" ", timespec="seconds") if payment.paid_at else "",
    )


def to_invoice_dto(invoice: Invoice) -> InvoiceDTO:
    return InvoiceDTO(
        id=invoice.id,
        invoice_code=invoice.invoice_code,
        customer_code=invoice.customer_code,
        billing_period=invoice.billing_period,
        amount=invoice.amount,
        status=invoice.status.value,
    )


def to_incident_dto(incident: Incident) -> IncidentDTO:
    return IncidentDTO(
        id=incident.id,
        customer_code=incident.customer_code,
        incident_type=incident.incident_type,
        priority=incident.priority,
        description=incident.description,
        status=incident.status.value,
        received_date=incident.received_date.isoformat() if incident.received_date else "",
    )
