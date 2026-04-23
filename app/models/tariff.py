from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from app.models.enums import ContractType


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
