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
            return self._dashboard_sql()

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

        top_consumers = list(
            self.db.mongo_collection("invoices").aggregate(
                [
                    {
                        "$group": {
                            "_id": "$customer_code",
                            "total_kwh": {"$sum": {"$ifNull": ["$consumption_kwh", 0]}},
                            "total_amount": {"$sum": "$amount"},
                            "invoice_count": {"$sum": 1},
                        }
                    },
                    {"$sort": {"total_kwh": -1}},
                    {"$limit": 5},
                    {
                        "$lookup": {
                            "from": "customers",
                            "localField": "_id",
                            "foreignField": "customer_code",
                            "as": "customer",
                        }
                    },
                    {"$unwind": {"path": "$customer", "preserveNullAndEmptyArrays": True}},
                ]
            )
        )

        return {
            "monthly_revenue": [{"label": row["_id"], "value": int(row["total"])} for row in monthly_revenue],
            "invoice_status": [{"label": row["_id"], "value": int(row["total"])} for row in invoice_status],
            "contract_types": [{"label": row["_id"], "value": int(row["total"])} for row in contract_types],
            "monthly_consumption": [{"label": row["_id"], "value": int(row["total"])} for row in monthly_consumption],
            "top_consumers": [self._format_top_consumer(row) for row in top_consumers],
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

    def _top_consumers_sql(self) -> list[dict]:
        if self.db.backend == "sqlserver":
            rows = self.db.fetch_all(
                """
                SELECT TOP 5
                    i.customer_code,
                    COALESCE(c.owner_name, '') AS owner_name,
                    COALESCE(c.contract_type, '') AS contract_type,
                    COALESCE(SUM(i.consumption_kwh), 0) AS total_kwh,
                    COALESCE(SUM(i.amount), 0) AS total_amount,
                    COUNT(*) AS invoice_count
                FROM invoices i
                LEFT JOIN customers c ON c.customer_code = i.customer_code
                GROUP BY i.customer_code, c.owner_name, c.contract_type
                ORDER BY total_kwh DESC
                """
            )
        else:
            rows = self.db.fetch_all(
                """
                SELECT
                    i.customer_code,
                    COALESCE(c.owner_name, '') AS owner_name,
                    COALESCE(c.contract_type, '') AS contract_type,
                    COALESCE(SUM(i.consumption_kwh), 0) AS total_kwh,
                    COALESCE(SUM(i.amount), 0) AS total_amount,
                    COUNT(*) AS invoice_count
                FROM invoices i
                LEFT JOIN customers c ON c.customer_code = i.customer_code
                GROUP BY i.customer_code, c.owner_name, c.contract_type
                ORDER BY total_kwh DESC
                LIMIT 5
                """
            )
        return [
            {
                "customer_code": row["customer_code"],
                "owner_name": row["owner_name"],
                "contract_type": row["contract_type"],
                "total_kwh": int(row["total_kwh"] or 0),
                "total_amount": int(row["total_amount"] or 0),
                "invoice_count": int(row["invoice_count"] or 0),
            }
            for row in rows
        ]

    def _dashboard_sql(self) -> dict:
        monthly_revenue = self.db.fetch_all(
            """
            SELECT i.billing_period AS label, COALESCE(SUM(p.paid_amount), 0) AS value
            FROM payments p
            INNER JOIN invoices i ON i.invoice_code = p.invoice_code
            GROUP BY i.billing_period
            ORDER BY i.billing_period
            """
        )
        invoice_status = self.db.fetch_all(
            """
            SELECT status AS label, COUNT(*) AS value
            FROM invoices
            GROUP BY status
            ORDER BY status
            """
        )
        contract_types = self.db.fetch_all(
            """
            SELECT contract_type AS label, COUNT(*) AS value
            FROM customers
            GROUP BY contract_type
            ORDER BY contract_type
            """
        )
        monthly_consumption = self.db.fetch_all(
            """
            SELECT billing_period AS label, COALESCE(SUM(consumption_kwh), 0) AS value
            FROM invoices
            GROUP BY billing_period
            ORDER BY billing_period
            """
        )

        return {
            "monthly_revenue": self._format_series_rows(monthly_revenue),
            "invoice_status": self._format_series_rows(invoice_status),
            "contract_types": self._format_series_rows(contract_types),
            "monthly_consumption": self._format_series_rows(monthly_consumption),
            "top_consumers": self._top_consumers_sql(),
        }

    def _format_series_rows(self, rows: list[dict]) -> list[dict]:
        return [{"label": row["label"], "value": int(row["value"] or 0)} for row in rows]

    def _format_top_consumer(self, row: dict) -> dict:
        customer = row.get("customer") or {}
        return {
            "customer_code": row["_id"],
            "owner_name": customer.get("owner_name", ""),
            "contract_type": customer.get("contract_type", ""),
            "total_kwh": int(row.get("total_kwh") or 0),
            "total_amount": int(row.get("total_amount") or 0),
            "invoice_count": int(row.get("invoice_count") or 0),
        }
