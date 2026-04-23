from datetime import datetime

from app.dto.mappers import to_tariff_config_dto
from app.dto.requests import TariffUpsertDTO
from app.dto.responses import TariffConfigDTO
from app.models import ContractType, TariffConfig
from app.repositories.tariff_repository import TariffRepository


class TariffService:
    def __init__(self, tariff_repository: TariffRepository):
        self.tariff_repository = tariff_repository

    def get_config(self, contract_type: ContractType) -> TariffConfigDTO | None:
        config = self.tariff_repository.get_by_contract_type(contract_type)
        return to_tariff_config_dto(config) if config else None

    def save_config(self, request: TariffUpsertDTO) -> TariffConfigDTO:
        config = TariffConfig(
            id=None,
            contract_type=ContractType(request.contract_type),
            fixed_fee=request.fixed_fee,
            vat_percent=request.vat_percent,
            peak_multiplier=request.peak_multiplier,
            base_rate=request.base_rate,
            formula_note=request.formula_note,
            updated_at=datetime.now(),
        )
        saved = self.tariff_repository.save(config)
        return to_tariff_config_dto(saved)
