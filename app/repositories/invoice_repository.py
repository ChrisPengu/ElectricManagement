from app.core.database import DatabaseManager
from app.models import Invoice, InvoiceStatus


class InvoiceRepository:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def list_all(self) -> list[Invoice]:
        if self.db.backend == "mongodb":
            rows = self.db.mongo_collection("invoices").find({}, sort=[("id", -1)])
            return [self._to_model(row) for row in rows]

        rows = self.db.fetch_all(
            """
            SELECT id, invoice_code, customer_code, billing_period, amount, status
            FROM invoices
            ORDER BY id DESC
            """
        )
        return [self._to_model(row) for row in rows]

    def list_unpaid(self) -> list[Invoice]:
        if self.db.backend == "mongodb":
            rows = self.db.mongo_collection("invoices").find(
                {"status": {"$ne": InvoiceStatus.PAID.value}},
                sort=[("id", -1)],
            )
            return [self._to_model(row) for row in rows]

        rows = self.db.fetch_all(
            """
            SELECT id, invoice_code, customer_code, billing_period, amount, status
            FROM invoices
            WHERE status <> ?
            ORDER BY id DESC
            """,
            (InvoiceStatus.PAID.value,),
        )
        return [self._to_model(row) for row in rows]

    def get_by_code(self, invoice_code: str) -> Invoice | None:
        if self.db.backend == "mongodb":
            row = self.db.mongo_collection("invoices").find_one({"invoice_code": invoice_code})
            return self._to_model(row) if row else None

        row = self.db.fetch_one(
            """
            SELECT id, invoice_code, customer_code, billing_period, amount, status
            FROM invoices
            WHERE invoice_code = ?
            """,
            (invoice_code,),
        )
        return self._to_model(row) if row else None

    def exists_for_customer_period(self, customer_code: str, billing_period: str) -> bool:
        if self.db.backend == "mongodb":
            return self.db.mongo_collection("invoices").count_documents(
                {"customer_code": customer_code, "billing_period": billing_period},
                limit=1,
            ) > 0

        row = self.db.fetch_one(
            """
            SELECT id
            FROM invoices
            WHERE customer_code = ? AND billing_period = ?
            """,
            (customer_code, billing_period),
        )
        return row is not None

    def create(
        self,
        invoice: Invoice,
        consumption_kwh: int = 0,
        fixed_fee: int = 0,
        vat_amount: int = 0,
        issued_by_user_id: int | None = None,
    ) -> Invoice:
        if self.db.backend == "mongodb":
            self.db.mongo_collection("invoices").insert_one(
                {
                    "id": self.db.next_sequence("invoices"),
                    "invoice_code": invoice.invoice_code,
                    "customer_code": invoice.customer_code,
                    "billing_period": invoice.billing_period,
                    "consumption_kwh": consumption_kwh,
                    "fixed_fee": fixed_fee,
                    "vat_amount": vat_amount,
                    "amount": invoice.amount,
                    "status": invoice.status.value,
                    "issued_by_user_id": issued_by_user_id,
                }
            )
            return self.get_by_code(invoice.invoice_code) or invoice

        if self.db.has_column("invoices", "consumption_kwh"):
            self.db.execute(
                """
                INSERT INTO invoices (
                    invoice_code, customer_code, billing_period, consumption_kwh,
                    fixed_fee, vat_amount, amount, status, issued_by_user_id
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    invoice.invoice_code,
                    invoice.customer_code,
                    invoice.billing_period,
                    consumption_kwh,
                    fixed_fee,
                    vat_amount,
                    invoice.amount,
                    invoice.status.value,
                    issued_by_user_id,
                ),
            )
        else:
            self.db.execute(
                """
                INSERT INTO invoices (invoice_code, customer_code, billing_period, amount, status)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    invoice.invoice_code,
                    invoice.customer_code,
                    invoice.billing_period,
                    invoice.amount,
                    invoice.status.value,
                ),
            )
        return self.get_by_code(invoice.invoice_code) or invoice

    def mark_paid(self, invoice_code: str) -> None:
        if self.db.backend == "mongodb":
            self.db.mongo_collection("invoices").update_one(
                {"invoice_code": invoice_code},
                {"$set": {"status": InvoiceStatus.PAID.value}},
            )
            return

        self.db.execute(
            """
            UPDATE invoices
            SET status = ?
            WHERE invoice_code = ?
            """,
            (InvoiceStatus.PAID.value, invoice_code),
        )

    def _to_model(self, row: dict) -> Invoice:
        return Invoice(
            id=row.get("id"),
            invoice_code=row["invoice_code"],
            customer_code=row["customer_code"],
            billing_period=row["billing_period"],
            amount=row["amount"],
            status=InvoiceStatus(row["status"]),
        )
