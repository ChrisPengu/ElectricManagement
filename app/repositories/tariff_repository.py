from datetime import datetime

from app.core.database import DatabaseManager
from app.models import ContractType, TariffConfig


class TariffRepository:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def get_by_contract_type(self, contract_type: ContractType) -> TariffConfig | None:
        row = self.db.fetch_one(
            """
            SELECT id, contract_type, fixed_fee, vat_percent, peak_multiplier, base_rate, formula_note, updated_at
            FROM tariff_configs
            WHERE contract_type = ?
            """,
            (contract_type.value,),
        )

        if row is None:
            return None

        updated_at = row["updated_at"]
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)

        return TariffConfig(
            id=row["id"],
            contract_type=ContractType(row["contract_type"]),
            fixed_fee=row["fixed_fee"],
            vat_percent=row["vat_percent"],
            peak_multiplier=row["peak_multiplier"],
            base_rate=row["base_rate"],
            formula_note=row["formula_note"],
            updated_at=updated_at,
        )

    def save(self, config: TariffConfig) -> TariffConfig:
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
                        updated_at = source.updated_at
                WHEN NOT MATCHED THEN
                    INSERT (contract_type, fixed_fee, vat_percent, peak_multiplier, base_rate, formula_note, updated_at)
                    VALUES (
                        source.contract_type,
                        source.fixed_fee,
                        source.vat_percent,
                        source.peak_multiplier,
                        source.base_rate,
                        source.formula_note,
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
                    config.updated_at.isoformat(sep=" ", timespec="seconds"),
                ),
            )
        else:
            self.db.execute(
                """
                INSERT INTO tariff_configs (
                    contract_type, fixed_fee, vat_percent, peak_multiplier, base_rate, formula_note, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(contract_type) DO UPDATE SET
                    fixed_fee = excluded.fixed_fee,
                    vat_percent = excluded.vat_percent,
                    peak_multiplier = excluded.peak_multiplier,
                    base_rate = excluded.base_rate,
                    formula_note = excluded.formula_note,
                    updated_at = excluded.updated_at
                """,
                (
                    config.contract_type.value,
                    config.fixed_fee,
                    config.vat_percent,
                    config.peak_multiplier,
                    config.base_rate,
                    config.formula_note,
                    config.updated_at.isoformat(sep=" ", timespec="seconds"),
                ),
            )

        return self.get_by_contract_type(config.contract_type) or config
