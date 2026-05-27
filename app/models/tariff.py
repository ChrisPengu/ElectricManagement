from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from app.models.enums import ContractType


DEFAULT_HOUSEHOLD_PRICE_TIERS: tuple[dict[str, int | None], ...] = (
    {"from_kwh": 0, "to_kwh": 50, "rate": 1806},
    {"from_kwh": 51, "to_kwh": 100, "rate": 1866},
    {"from_kwh": 101, "to_kwh": 200, "rate": 2167},
    {"from_kwh": 201, "to_kwh": 300, "rate": 2729},
    {"from_kwh": 301, "to_kwh": 400, "rate": 3050},
    {"from_kwh": 401, "to_kwh": None, "rate": 3151},
)


def default_household_price_tiers() -> list[dict[str, int | None]]:
    return [dict(tier) for tier in DEFAULT_HOUSEHOLD_PRICE_TIERS]


@dataclass(slots=True)
class TariffConfig:
    id: Optional[int]
    contract_type: ContractType
    fixed_fee: int
    vat_percent: float
    peak_multiplier: float
    base_rate: int
    formula_note: str
    updated_at: datetime
    price_tiers: list[dict[str, int | None]] = field(default_factory=default_household_price_tiers)
