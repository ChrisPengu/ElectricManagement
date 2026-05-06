from datetime import datetime

from app.dto.mappers import to_payment_dto
from app.dto.requests import PaymentCreateDTO
from app.dto.responses import PaymentDTO
from app.models import InvoiceStatus, Payment
from app.repositories.invoice_repository import InvoiceRepository
from app.repositories.payment_repository import PaymentRepository


class PaymentService:
    def __init__(self, payment_repository: PaymentRepository, invoice_repository: InvoiceRepository):
        self.payment_repository = payment_repository
        self.invoice_repository = invoice_repository

    def list_recent(self, limit: int = 50) -> list[PaymentDTO]:
        return [to_payment_dto(payment) for payment in self.payment_repository.list_recent(limit)]

    def create_payment(self, request: PaymentCreateDTO) -> PaymentDTO:
        invoice = self.invoice_repository.get_by_code(request.invoice_code)
        if invoice is None:
            raise ValueError("Không tìm thấy hóa đơn cần thu.")
        if invoice.status == InvoiceStatus.PAID:
            raise ValueError("Hóa đơn đã thanh toán.")
        if request.paid_amount <= 0:
            raise ValueError("Số tiền thu phải lớn hơn 0.")
        if request.paid_amount < invoice.amount:
            raise ValueError("Số tiền thu chưa đủ để tất toán hóa đơn.")

        receipt_code = request.receipt_code.strip() or self._build_receipt_code(invoice.invoice_code)
        payment = Payment(
            id=None,
            receipt_code=receipt_code,
            invoice_code=invoice.invoice_code,
            paid_amount=request.paid_amount,
            payment_method=request.payment_method.strip(),
            payer_name=request.payer_name.strip(),
            collected_by_user_id=request.collected_by_user_id,
            note=request.note.strip(),
        )
        saved = self.payment_repository.create(payment)
        self.invoice_repository.mark_paid(invoice.invoice_code)
        return to_payment_dto(saved)

    def _build_receipt_code(self, invoice_code: str) -> str:
        return f"BN-{invoice_code}-{datetime.now().strftime('%H%M%S')}"
