from datetime import datetime

from app.dto.mappers import to_invoice_dto
from app.dto.responses import InvoiceDTO
from app.models import ContractType, Invoice, InvoiceStatus
from app.repositories.customer_repository import CustomerRepository
from app.repositories.invoice_repository import InvoiceRepository
from app.repositories.meter_reading_repository import MeterReadingRepository
from app.repositories.tariff_repository import TariffRepository
from app.services.billing_service import BillingService


class InvoiceService:
    def __init__(
        self,
        invoice_repository: InvoiceRepository,
        customer_repository: CustomerRepository,
        meter_reading_repository: MeterReadingRepository,
        tariff_repository: TariffRepository,
        billing_service: BillingService,
    ):
        self.invoice_repository = invoice_repository
        self.customer_repository = customer_repository
        self.meter_reading_repository = meter_reading_repository
        self.tariff_repository = tariff_repository
        self.billing_service = billing_service

    def list_invoices(self) -> list[InvoiceDTO]:
        return [to_invoice_dto(invoice) for invoice in self.invoice_repository.list_all()]

    def list_unpaid(self) -> list[InvoiceDTO]:
        return [to_invoice_dto(invoice) for invoice in self.invoice_repository.list_unpaid()]

    def create_invoice_for_customer(
        self,
        customer_code: str,
        billing_period: str,
        issued_by_user_id: int | None = None,
    ) -> InvoiceDTO:
        customer = self.customer_repository.get_by_code(customer_code)
        if customer is None:
            raise ValueError("Không tìm thấy hộ dùng điện.")
        if self.invoice_repository.exists_for_customer_period(customer_code, billing_period):
            raise ValueError("Hóa đơn cho kỳ này đã tồn tại.")

        reading = self.meter_reading_repository.get_for_customer_period(customer_code, billing_period)
        if reading is None:
            raise ValueError("Chưa có chỉ số công tơ cho kỳ này.")

        previous = self.meter_reading_repository.get_previous_for_reading(reading)
        previous_index = previous.new_index if previous else 0
        consumption = max(reading.new_index - previous_index, 0)

        tariff = self.tariff_repository.get_by_contract_type(customer.contract_type)
        if tariff is None:
            raise ValueError("Chưa có cấu hình biểu giá cho loại hợp đồng.")

        amount = self.billing_service.calculate_amount(
            contract_type=customer.contract_type,
            consumption_kwh=consumption,
            fixed_fee=tariff.fixed_fee,
            vat_percent=tariff.vat_percent,
            base_rate=tariff.base_rate,
            peak_multiplier=tariff.peak_multiplier if customer.contract_type == ContractType.FACTORY else 1.0,
        )
        subtotal_without_vat = int(amount / (1 + tariff.vat_percent / 100)) if tariff.vat_percent else amount
        vat_amount = amount - subtotal_without_vat
        invoice_code = self._build_invoice_code(customer_code, billing_period)
        invoice = Invoice(
            id=None,
            invoice_code=invoice_code,
            customer_code=customer_code,
            billing_period=billing_period,
            amount=amount,
            status=InvoiceStatus.UNPAID,
        )
        saved = self.invoice_repository.create(
            invoice,
            consumption_kwh=consumption,
            fixed_fee=tariff.fixed_fee,
            vat_amount=vat_amount,
            issued_by_user_id=issued_by_user_id,
        )
        return to_invoice_dto(saved)

    def mark_paid(self, invoice_code: str) -> None:
        if self.invoice_repository.get_by_code(invoice_code) is None:
            raise ValueError("Không tìm thấy hóa đơn.")
        self.invoice_repository.mark_paid(invoice_code)

    def _build_invoice_code(self, customer_code: str, billing_period: str) -> str:
        period_code = billing_period.replace("/", "")
        suffix = datetime.now().strftime("%H%M%S")
        return f"HDON-{customer_code}-{period_code}-{suffix}"
