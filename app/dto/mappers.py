from app.dto.requests import MeterReadingCreateDTO, TariffUpsertDTO
from app.dto.responses import CustomerDTO, MeterReadingDTO, TariffConfigDTO, UserDTO
from app.models import Customer, MeterReading, TariffConfig, UserAccount


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
