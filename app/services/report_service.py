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

    def dashboard(self) -> dict:
        if self.db.backend != "mongodb":
            return {
                "monthly_revenue": [],
                "invoice_status": [],
                "contract_types": [],
                "monthly_consumption": [],
            }

        monthly_revenue = list(
            self.db.mongo_collection("payments").aggregate(
                [
                    {
                        "$lookup": {
                            "from": "invoices",
                            "localField": "invoice_code",
                            "foreignField": "invoice_code",
                            "as": "invoice",
                        }
                    },
                    {"$unwind": "$invoice"},
                    {"$group": {"_id": "$invoice.billing_period", "total": {"$sum": "$paid_amount"}}},
                    {"$sort": {"_id": 1}},
                ]
            )
        )

        invoice_status = list(
            self.db.mongo_collection("invoices").aggregate(
                [{"$group": {"_id": "$status", "total": {"$sum": 1}}}, {"$sort": {"_id": 1}}]
            )
        )

        contract_types = list(
            self.db.mongo_collection("customers").aggregate(
                [{"$group": {"_id": "$contract_type", "total": {"$sum": 1}}}, {"$sort": {"_id": 1}}]
            )
        )

        monthly_consumption = list(
            self.db.mongo_collection("invoices").aggregate(
                [
                    {"$group": {"_id": "$billing_period", "total": {"$sum": "$consumption_kwh"}}},
                    {"$sort": {"_id": 1}},
                ]
            )
        )

        return {
            "monthly_revenue": [{"label": row["_id"], "value": int(row["total"])} for row in monthly_revenue],
            "invoice_status": [{"label": row["_id"], "value": int(row["total"])} for row in invoice_status],
            "contract_types": [{"label": row["_id"], "value": int(row["total"])} for row in contract_types],
            "monthly_consumption": [{"label": row["_id"], "value": int(row["total"])} for row in monthly_consumption],
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
