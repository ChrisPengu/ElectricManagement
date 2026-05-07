from datetime import datetime

from app.core.database import DatabaseManager
from app.models import Payment


class PaymentRepository:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def list_recent(self, limit: int = 50) -> list[Payment]:
        if self.db.backend == "mongodb":
            rows = self.db.mongo_collection("payments").find({}, sort=[("id", -1)], limit=limit)
            return [self._to_model(row) for row in rows]

        has_receipt = self.db.has_column("payments", "receipt_code")
        if self.db.backend == "sqlserver":
            if has_receipt:
                rows = self.db.fetch_all(
                    """
                    SELECT TOP (?) id, receipt_code, invoice_code, paid_amount, payment_method,
                           payer_name, collected_by_user_id, note, paid_at
                    FROM payments
                    ORDER BY paid_at DESC, id DESC
                    """,
                    (limit,),
                )
            else:
                rows = self.db.fetch_all(
                    """
                    SELECT TOP (?) id, invoice_code, paid_amount, payment_method, paid_at
                    FROM payments
                    ORDER BY paid_at DESC, id DESC
                    """,
                    (limit,),
                )
        else:
            if has_receipt:
                rows = self.db.fetch_all(
                    """
                    SELECT id, receipt_code, invoice_code, paid_amount, payment_method,
                           payer_name, collected_by_user_id, note, paid_at
                    FROM payments
                    ORDER BY paid_at DESC, id DESC
                    LIMIT ?
                    """,
                    (limit,),
                )
            else:
                rows = self.db.fetch_all(
                    """
                    SELECT id, invoice_code, paid_amount, payment_method, paid_at
                    FROM payments
                    ORDER BY paid_at DESC, id DESC
                    LIMIT ?
                    """,
                    (limit,),
                )
        return [self._to_model(row) for row in rows]

    def create(self, payment: Payment) -> Payment:
        if self.db.backend == "mongodb":
            self.db.mongo_collection("payments").insert_one(
                {
                    "id": self.db.next_sequence("payments"),
                    "receipt_code": payment.receipt_code,
                    "invoice_code": payment.invoice_code,
                    "paid_amount": payment.paid_amount,
                    "payment_method": payment.payment_method,
                    "payer_name": payment.payer_name,
                    "collected_by_user_id": payment.collected_by_user_id,
                    "note": payment.note,
                    "paid_at": datetime.now(),
                }
            )
            return self.get_by_receipt_code(payment.receipt_code) or payment

        if self.db.has_column("payments", "receipt_code"):
            self.db.execute(
                """
                INSERT INTO payments (
                    receipt_code, invoice_code, paid_amount, payment_method,
                    payer_name, collected_by_user_id, note
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payment.receipt_code,
                    payment.invoice_code,
                    payment.paid_amount,
                    payment.payment_method,
                    payment.payer_name,
                    payment.collected_by_user_id,
                    payment.note,
                ),
            )
            return self.get_by_receipt_code(payment.receipt_code) or payment

        self.db.execute(
            """
            INSERT INTO payments (invoice_code, paid_amount, payment_method)
            VALUES (?, ?, ?)
            """,
            (payment.invoice_code, payment.paid_amount, payment.payment_method),
        )
        return payment

    def get_by_receipt_code(self, receipt_code: str) -> Payment | None:
        if self.db.backend == "mongodb":
            row = self.db.mongo_collection("payments").find_one({"receipt_code": receipt_code})
            return self._to_model(row) if row else None

        if not self.db.has_column("payments", "receipt_code"):
            return None
        row = self.db.fetch_one(
            """
            SELECT id, receipt_code, invoice_code, paid_amount, payment_method,
                   payer_name, collected_by_user_id, note, paid_at
            FROM payments
            WHERE receipt_code = ?
            """,
            (receipt_code,),
        )
        return self._to_model(row) if row else None

    def _to_model(self, row: dict) -> Payment:
        paid_at = row["paid_at"]
        if isinstance(paid_at, str):
            paid_at = datetime.fromisoformat(paid_at)
        return Payment(
            id=row["id"],
            receipt_code=row.get("receipt_code") or f"BN{row['id']:03d}",
            invoice_code=row["invoice_code"],
            paid_amount=row["paid_amount"],
            payment_method=row["payment_method"],
            payer_name=row.get("payer_name", ""),
            collected_by_user_id=row.get("collected_by_user_id") or 0,
            note=row.get("note", ""),
            paid_at=paid_at,
        )
