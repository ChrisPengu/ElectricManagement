from app.models import ContractType, default_household_price_tiers


class BillingService:
    def calculate_amount(
        self,
        contract_type: ContractType,
        consumption_kwh: int,
        fixed_fee: int,
        vat_percent: float,
        base_rate: int,
        peak_multiplier: float = 1.0,
        price_tiers: list[dict[str, int | None]] | None = None,
    ) -> int:
        if consumption_kwh < 0:
            raise ValueError("Sản lượng tiêu thụ không được âm.")

        if contract_type == ContractType.HOUSEHOLD:
            energy_cost = self._calculate_household_cost(consumption_kwh, price_tiers)
        else:
            energy_cost = int(consumption_kwh * base_rate * peak_multiplier)

        subtotal = fixed_fee + energy_cost
        total = subtotal + int(subtotal * vat_percent / 100)
        return total

    def _calculate_household_cost(
        self,
        consumption_kwh: int,
        price_tiers: list[dict[str, int | None]] | None = None,
    ) -> int:
        tiers = price_tiers or default_household_price_tiers()
        total = 0

        for tier in tiers:
            lower_bound = max(int(tier.get("from_kwh", 0)), 1)
            if consumption_kwh < lower_bound:
                continue

            to_kwh = tier.get("to_kwh")
            upper_bound = consumption_kwh if to_kwh is None else min(consumption_kwh, int(to_kwh))
            units = max(0, upper_bound - lower_bound + 1)
            total += int(units * int(tier.get("rate", 0)))

        return total
