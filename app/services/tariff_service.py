from datetime import datetime

from app.dto.mappers import to_tariff_config_dto
from app.dto.requests import TariffUpsertDTO
from app.dto.responses import TariffConfigDTO
from app.models import ContractType, TariffConfig, default_household_price_tiers
from app.repositories.tariff_repository import TariffRepository


class TariffService:
    def __init__(self, tariff_repository: TariffRepository):
        self.tariff_repository = tariff_repository

    def get_config(self, contract_type: ContractType) -> TariffConfigDTO | None:
        config = self.tariff_repository.get_by_contract_type(contract_type)
        return to_tariff_config_dto(config) if config else None

    def save_config(self, request: TariffUpsertDTO) -> TariffConfigDTO:
        contract_type = ContractType(request.contract_type)
        price_tiers = (
            self._normalize_price_tiers(request.price_tiers)
            if contract_type == ContractType.HOUSEHOLD
            else []
        )
        config = TariffConfig(
            id=None,
            contract_type=contract_type,
            fixed_fee=request.fixed_fee,
            vat_percent=request.vat_percent,
            peak_multiplier=request.peak_multiplier,
            base_rate=request.base_rate,
            formula_note=request.formula_note,
            updated_at=datetime.now(),
            price_tiers=price_tiers,
        )
        saved = self.tariff_repository.save(config)
        return to_tariff_config_dto(saved)

    def _normalize_price_tiers(self, price_tiers: list[dict] | None) -> list[dict[str, int | None]]:
        tiers = price_tiers or default_household_price_tiers()
        normalized = []
        expected_from = None

        for index, tier in enumerate(tiers):
            try:
                from_kwh = int(tier.get("from_kwh", 0))
                to_value = tier.get("to_kwh")
                to_kwh = None if to_value in (None, "") else int(to_value)
                rate = int(tier.get("rate", 0))
            except (AttributeError, TypeError, ValueError) as exc:
                raise ValueError("Khung gia phai nhap bang so hop le.") from exc

            lower_bound = max(from_kwh, 1)
            if index == 0 and from_kwh not in (0, 1):
                raise ValueError("Bac gia dau tien phai bat dau tu 0 hoac 1 kWh.")
            if expected_from is not None and from_kwh != expected_from:
                raise ValueError("Cac bac gia phai lien tiep, khong duoc bo trong khoang kWh.")
            if rate <= 0:
                raise ValueError("Don gia moi bac phai lon hon 0.")
            if to_kwh is None:
                if index != len(tiers) - 1:
                    raise ValueError("Chi bac gia cuoi cung duoc de trong cot den kWh.")
            else:
                if to_kwh < lower_bound:
                    raise ValueError("Cot den kWh phai lon hon hoac bang cot tu kWh.")
                expected_from = to_kwh + 1

            normalized.append({"from_kwh": from_kwh, "to_kwh": to_kwh, "rate": rate})

        if not normalized:
            raise ValueError("Can co it nhat mot bac gia.")
        if normalized[-1]["to_kwh"] is not None:
            raise ValueError("Bac gia cuoi cung can de trong cot den kWh de ap dung cho phan vuot muc.")

        return normalized
