from app.core.database import DatabaseManager
from app.models import IncidentStatus, InvoiceStatus


class ReportService:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def summary(self) -> dict[str, int]:
        if self.db.backend == "mongodb":
            return {
                "customers": self.db.mongo_collection("customers").count_documents({}),
                "invoices": self.db.mongo_collection("invoices").count_documents({}),
                "unpaid_invoices": self.db.mongo_collection("invoices").count_documents(
                    {"status": {"$ne": InvoiceStatus.PAID.value}}
                ),
                "revenue": self._sum_mongodb_paid_amount(),
                "incidents_open": self.db.mongo_collection("incidents").count_documents(
                    {"status": {"$ne": IncidentStatus.DONE.value}}
                ),
            }

        return {
            "customers": self._count("customers"),
            "invoices": self._count("invoices"),
            "unpaid_invoices": self._count("invoices", "status <> ?", (InvoiceStatus.PAID.value,)),
            "revenue": self._sum_paid_amount(),
            "incidents_open": self._count("incidents", "status <> ?", (IncidentStatus.DONE.value,)),
        }

    def _count(self, table: str, where: str | None = None, params: tuple = ()) -> int:
        query = f"SELECT COUNT(*) AS total FROM {table}"
        if where:
            query += f" WHERE {where}"
        row = self.db.fetch_one(query, params)
        return int(row["total"] or 0) if row else 0

    def _sum_paid_amount(self) -> int:
        row = self.db.fetch_one("SELECT COALESCE(SUM(paid_amount), 0) AS total FROM payments")
        return int(row["total"] or 0) if row else 0

    def _sum_mongodb_paid_amount(self) -> int:
        rows = self.db.mongo_collection("payments").aggregate(
            [{"$group": {"_id": None, "total": {"$sum": "$paid_amount"}}}]
        )
        row = next(rows, None)
        return int(row["total"]) if row else 0
