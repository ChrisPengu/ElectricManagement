from dataclasses import dataclass
from typing import Optional

from app.models.enums import ContractType


@dataclass(slots=True)
class Customer:
    id: Optional[int]
    customer_code: str
    owner_name: str
    address: str
    phone_number: str
    contract_type: ContractType
