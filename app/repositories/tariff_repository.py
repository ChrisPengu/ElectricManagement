import json
from datetime import datetime

from app.core.database import DatabaseManager
from app.models import ContractType, TariffConfig, default_household_price_tiers


class TariffRepository:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def get_by_contract_type(self, contract_type: ContractType) -> TariffConfig | None:
        if self.db.backend == "mongodb":
            row = self.db.mongo_collection("tariff_configs").find_one({"contract_type": contract_type.value})
            return self._to_model(row) if row else None

        row = self.db.fetch_one(
            """
            SELECT id, contract_type, fixed_fee, vat_percent, peak_multiplier, base_rate,
                   formula_note, price_tiers, updated_at
            FROM tariff_configs
            WHERE contract_type = ?
            """,
            (contract_type.value,),
        )

        if row is None:
            return None

        return self._to_model(row)

    def save(self, config: TariffConfig) -> TariffConfig:
        price_tiers_json = self._serialize_price_tiers(config.price_tiers)
        if self.db.backend == "mongodb":
            existing = self.get_by_contract_type(config.contract_type)
            payload = {
                "contract_type": config.contract_type.value,
                "fixed_fee": config.fixed_fee,
                "vat_percent": config.vat_percent,
                "peak_multiplier": config.peak_multiplier,
                "base_rate": config.base_rate,
                "formula_note": config.formula_note,
                "price_tiers": [dict(tier) for tier in config.price_tiers],
                "updated_at": config.updated_at,
            }
            if existing is None:
                payload["id"] = self.db.next_sequence("tariff_configs")
            self.db.mongo_collection("tariff_configs").update_one(
                {"contract_type": config.contract_type.value},
                {"$set": payload},
                upsert=True,
            )
            return self.get_by_contract_type(config.contract_type) or config

        if self.db.backend == "sqlserver":
            self.db.execute(
                """
                MERGE tariff_configs AS target
                USING (
                    SELECT
                        ? AS contract_type,
                        ? AS fixed_fee,
                        ? AS vat_percent,
                        ? AS peak_multiplier,
                        ? AS base_rate,
                        ? AS formula_note,
                        ? AS price_tiers,
                        ? AS updated_at
                ) AS source
                ON target.contract_type = source.contract_type
                WHEN MATCHED THEN
                    UPDATE SET
                        fixed_fee = source.fixed_fee,
                        vat_percent = source.vat_percent,
                        peak_multiplier = source.peak_multiplier,
                        base_rate = source.base_rate,
                        formula_note = source.formula_note,
                        price_tiers = source.price_tiers,
                        updated_at = source.updated_at
                WHEN NOT MATCHED THEN
                    INSERT (
                        contract_type, fixed_fee, vat_percent, peak_multiplier, base_rate,
                        formula_note, price_tiers, updated_at
                    )
                    VALUES (
                        source.contract_type,
                        source.fixed_fee,
                        source.vat_percent,
                        source.peak_multiplier,
                        source.base_rate,
                        source.formula_note,
                        source.price_tiers,
                        source.updated_at
                    );
                """,
                (
                    config.contract_type.value,
                    config.fixed_fee,
                    config.vat_percent,
                    config.peak_multiplier,
                    config.base_rate,
                    config.formula_note,
                    price_tiers_json,
                    config.updated_at.isoformat(sep=" ", timespec="seconds"),
                ),
            )
        else:
            self.db.execute(
                """
                INSERT INTO tariff_configs (
                    contract_type, fixed_fee, vat_percent, peak_multiplier, base_rate,
                    formula_note, price_tiers, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(contract_type) DO UPDATE SET
                    fixed_fee = excluded.fixed_fee,
                    vat_percent = excluded.vat_percent,
                    peak_multiplier = excluded.peak_multiplier,
                    base_rate = excluded.base_rate,
                    formula_note = excluded.formula_note,
                    price_tiers = excluded.price_tiers,
                    updated_at = excluded.updated_at
                """,
                (
                    config.contract_type.value,
                    config.fixed_fee,
                    config.vat_percent,
                    config.peak_multiplier,
                    config.base_rate,
                    config.formula_note,
                    price_tiers_json,
                    config.updated_at.isoformat(sep=" ", timespec="seconds"),
                ),
            )

        return self.get_by_contract_type(config.contract_type) or config

    def _to_model(self, row: dict) -> TariffConfig:
        updated_at = row["updated_at"]
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)
        contract_type = ContractType(row["contract_type"])
        price_tiers = self._deserialize_price_tiers(
            row.get("price_tiers"),
            use_default=contract_type == ContractType.HOUSEHOLD,
        )
        return TariffConfig(
            id=row.get("id"),
            contract_type=contract_type,
            fixed_fee=row["fixed_fee"],
            vat_percent=row["vat_percent"],
            peak_multiplier=row["peak_multiplier"],
            base_rate=row["base_rate"],
            formula_note=row["formula_note"],
            updated_at=updated_at,
            price_tiers=price_tiers,
        )

    def _serialize_price_tiers(self, price_tiers: list[dict[str, int | None]]) -> str:
        return json.dumps(price_tiers or [], ensure_ascii=True)

    def _deserialize_price_tiers(self, value, use_default: bool) -> list[dict[str, int | None]]:
        if isinstance(value, list):
            tiers = value
        elif value:
            try:
                tiers = json.loads(value)
            except (TypeError, ValueError):
                tiers = []
        else:
            tiers = []

        normalized = []
        for tier in tiers:
            if not isinstance(tier, dict):
                continue
            try:
                from_kwh = int(tier.get("from_kwh", 0))
                to_value = tier.get("to_kwh")
                to_kwh = None if to_value in (None, "") else int(to_value)
                rate = int(tier.get("rate", 0))
            except (TypeError, ValueError):
                continue
            normalized.append({"from_kwh": from_kwh, "to_kwh": to_kwh, "rate": rate})

        if normalized:
            return normalized
        return default_household_price_tiers() if use_default else []
