from app.models import ContractType


class BillingService:
    def calculate_amount(
        self,
        contract_type: ContractType,
        consumption_kwh: int,
        fixed_fee: int,
        vat_percent: float,
        base_rate: int,
        peak_multiplier: float = 1.0,
    ) -> int:
        if consumption_kwh < 0:
            raise ValueError("Sản lượng tiêu thụ không được âm.")

        if contract_type == ContractType.HOUSEHOLD:
            energy_cost = self._calculate_household_cost(consumption_kwh)
        else:
            energy_cost = int(consumption_kwh * base_rate * peak_multiplier)

        subtotal = fixed_fee + energy_cost
        total = subtotal + int(subtotal * vat_percent / 100)
        return total

    def _calculate_household_cost(self, consumption_kwh: int) -> int:
        tiers = [
            (50, 1806),
            (50, 1866),
            (100, 2167),
            (100, 2729),
            (100, 3050),
            (float("inf"), 3151),
        ]

        remaining = consumption_kwh
        total = 0

        for limit, rate in tiers:
            if remaining <= 0:
                break
            units = min(remaining, limit)
            total += int(units * rate)
            remaining -= units

        return total
