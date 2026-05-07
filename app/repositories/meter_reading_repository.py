from datetime import datetime

from app.core.database import DatabaseManager
from app.models import MeterReading


class MeterReadingRepository:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def list_recent(self, limit: int = 50) -> list[MeterReading]:
        if self.db.backend == "mongodb":
            rows = self.db.mongo_collection("meter_readings").find({}, sort=[("id", -1)], limit=limit)
            return [self._to_model(row) for row in rows]

        if self.db.backend == "sqlserver":
            rows = self.db.fetch_all(
                """
                SELECT TOP (?) id, customer_code, reading_period, new_index, note, created_at
                FROM meter_readings
                ORDER BY created_at DESC, id DESC
                """,
                (limit,),
            )
        else:
            rows = self.db.fetch_all(
                """
                SELECT id, customer_code, reading_period, new_index, note, created_at
                FROM meter_readings
                ORDER BY created_at DESC, id DESC
                LIMIT ?
                """,
                (limit,),
            )
        return [self._to_model(row) for row in rows]

    def get_latest_for_customer(self, customer_code: str) -> MeterReading | None:
        if self.db.backend == "mongodb":
            row = self.db.mongo_collection("meter_readings").find_one(
                {"customer_code": customer_code},
                sort=[("id", -1)],
            )
            return self._to_model(row) if row else None

        if self.db.backend == "sqlserver":
            query = """
                SELECT TOP 1 id, customer_code, reading_period, new_index, note, created_at
                FROM meter_readings
                WHERE customer_code = ?
                ORDER BY created_at DESC, id DESC
                """
        else:
            query = """
                SELECT id, customer_code, reading_period, new_index, note, created_at
                FROM meter_readings
                WHERE customer_code = ?
                ORDER BY created_at DESC, id DESC
                LIMIT 1
                """
        row = self.db.fetch_one(query, (customer_code,))
        return self._to_model(row) if row else None

    def get_previous_for_reading(self, reading: MeterReading) -> MeterReading | None:
        if reading.id is None:
            return None
        if self.db.backend == "mongodb":
            row = self.db.mongo_collection("meter_readings").find_one(
                {"customer_code": reading.customer_code, "id": {"$lt": reading.id}},
                sort=[("id", -1)],
            )
            return self._to_model(row) if row else None

        if self.db.backend == "sqlserver":
            query = """
                SELECT TOP 1 id, customer_code, reading_period, new_index, note, created_at
                FROM meter_readings
                WHERE customer_code = ? AND id < ?
                ORDER BY id DESC
                """
        else:
            query = """
                SELECT id, customer_code, reading_period, new_index, note, created_at
                FROM meter_readings
                WHERE customer_code = ? AND id < ?
                ORDER BY id DESC
                LIMIT 1
                """
        row = self.db.fetch_one(query, (reading.customer_code, reading.id))
        return self._to_model(row) if row else None

    def get_for_customer_period(self, customer_code: str, reading_period: str) -> MeterReading | None:
        if self.db.backend == "mongodb":
            row = self.db.mongo_collection("meter_readings").find_one(
                {"customer_code": customer_code, "reading_period": reading_period}
            )
            return self._to_model(row) if row else None

        row = self.db.fetch_one(
            """
            SELECT id, customer_code, reading_period, new_index, note, created_at
            FROM meter_readings
            WHERE customer_code = ? AND reading_period = ?
            """,
            (customer_code, reading_period),
        )
        return self._to_model(row) if row else None

    def create(self, reading: MeterReading, recorded_by_user_id: int | None = None) -> MeterReading:
        if self.db.backend == "mongodb":
            now = datetime.now()
            self.db.mongo_collection("meter_readings").insert_one(
                {
                    "id": self.db.next_sequence("meter_readings"),
                    "customer_code": reading.customer_code,
                    "reading_period": reading.reading_period,
                    "new_index": reading.new_index,
                    "note": reading.note,
                    "recorded_by_user_id": recorded_by_user_id,
                    "created_at": now,
                }
            )
            return self.get_for_customer_period(reading.customer_code, reading.reading_period) or reading

        if self.db.has_column("meter_readings", "recorded_by_user_id"):
            self.db.execute(
                """
                INSERT INTO meter_readings (customer_code, reading_period, new_index, note, recorded_by_user_id)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    reading.customer_code,
                    reading.reading_period,
                    reading.new_index,
                    reading.note,
                    recorded_by_user_id,
                ),
            )
        else:
            self.db.execute(
                """
                INSERT INTO meter_readings (customer_code, reading_period, new_index, note)
                VALUES (?, ?, ?, ?)
                """,
                (reading.customer_code, reading.reading_period, reading.new_index, reading.note),
            )
        return self.get_for_customer_period(reading.customer_code, reading.reading_period) or reading

    def _to_model(self, row: dict) -> MeterReading:
        created_at = row["created_at"]
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        return MeterReading(
            id=row["id"],
            customer_code=row["customer_code"],
            reading_period=row["reading_period"],
            new_index=row["new_index"],
            note=row["note"],
            created_at=created_at,
        )
