from datetime import date

from app.core.database import DatabaseManager
from app.models import Incident, IncidentStatus


class IncidentRepository:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def list_all(self) -> list[Incident]:
        if self.db.backend == "mongodb":
            rows = self.db.mongo_collection("incidents").find({}, sort=[("id", -1)])
            return [self._to_model(row) for row in rows]

        rows = self.db.fetch_all(
            """
            SELECT id, customer_code, incident_type, priority, description, status, received_date
            FROM incidents
            ORDER BY id DESC
            """
        )
        return [self._to_model(row) for row in rows]

    def create(self, incident: Incident, received_by_user_id: int | None = None) -> Incident:
        if self.db.backend == "mongodb":
            self.db.mongo_collection("incidents").insert_one(
                {
                    "id": self.db.next_sequence("incidents"),
                    "customer_code": incident.customer_code,
                    "incident_type": incident.incident_type,
                    "priority": incident.priority,
                    "description": incident.description,
                    "status": incident.status.value,
                    "received_by_user_id": received_by_user_id,
                    "received_date": incident.received_date.isoformat() if incident.received_date else None,
                }
            )
            return self.list_all()[0]

        self.db.execute(
            """
            INSERT INTO incidents (
                customer_code, incident_type, priority, description,
                status, received_by_user_id, received_date
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                incident.customer_code,
                incident.incident_type,
                incident.priority,
                incident.description,
                incident.status.value,
                received_by_user_id,
                incident.received_date.isoformat() if incident.received_date else None,
            ),
        )
        return self.list_all()[0]

    def update_status(self, incident_id: int, status: IncidentStatus) -> None:
        if self.db.backend == "mongodb":
            self.db.mongo_collection("incidents").update_one(
                {"id": incident_id},
                {"$set": {"status": status.value}},
            )
            return

        self.db.execute(
            """
            UPDATE incidents
            SET status = ?
            WHERE id = ?
            """,
            (status.value, incident_id),
        )

    def update_status_description(self, incident_id: int, status: IncidentStatus, description: str) -> None:
        if self.db.backend == "mongodb":
            self.db.mongo_collection("incidents").update_one(
                {"id": incident_id},
                {"$set": {"status": status.value, "description": description}},
            )
            return

        self.db.execute(
            """
            UPDATE incidents
            SET status = ?, description = ?
            WHERE id = ?
            """,
            (status.value, description, incident_id),
        )

    def _to_model(self, row: dict) -> Incident:
        received_date = row["received_date"]
        if isinstance(received_date, str):
            received_date = date.fromisoformat(received_date)
        return Incident(
            id=row.get("id"),
            customer_code=row["customer_code"],
            incident_type=row["incident_type"],
            priority=row["priority"],
            description=row["description"],
            status=IncidentStatus(row["status"]),
            received_date=received_date,
        )
