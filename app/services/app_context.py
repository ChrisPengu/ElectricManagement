from app.core.database import DatabaseManager
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.auth_repository import AuthRepository
from app.repositories.customer_repository import CustomerRepository
from app.repositories.incident_repository import IncidentRepository
from app.repositories.invoice_repository import InvoiceRepository
from app.repositories.meter_reading_repository import MeterReadingRepository
from app.repositories.payment_repository import PaymentRepository
from app.repositories.tariff_repository import TariffRepository
from app.services.audit_log_service import AuditLogService
from app.services.auth_service import AuthService
from app.services.billing_service import BillingService
from app.services.customer_service import CustomerService
from app.services.incident_service import IncidentService
from app.services.invoice_service import InvoiceService
from app.services.meter_reading_service import MeterReadingService
from app.services.payment_service import PaymentService
from app.services.report_service import ReportService
from app.services.tariff_service import TariffService


class AppContext:
    def __init__(self):
        self.database = DatabaseManager()
        self.database.initialize()

        self.auth_repository = AuthRepository(self.database)
        self.customer_repository = CustomerRepository(self.database)
        self.tariff_repository = TariffRepository(self.database)
        self.meter_reading_repository = MeterReadingRepository(self.database)
        self.invoice_repository = InvoiceRepository(self.database)
        self.payment_repository = PaymentRepository(self.database)
        self.incident_repository = IncidentRepository(self.database)
        self.audit_log_repository = AuditLogRepository(self.database)

        self.auth_service = AuthService(self.auth_repository)
        self.billing_service = BillingService()
        self.customer_service = CustomerService(self.customer_repository)
        self.tariff_service = TariffService(self.tariff_repository)
        self.meter_reading_service = MeterReadingService(
            self.meter_reading_repository,
            self.customer_repository,
        )
        self.invoice_service = InvoiceService(
            self.invoice_repository,
            self.customer_repository,
            self.meter_reading_repository,
            self.tariff_repository,
            self.billing_service,
        )
        self.payment_service = PaymentService(self.payment_repository, self.invoice_repository)
        self.incident_service = IncidentService(self.incident_repository, self.customer_repository)
        self.audit_log_service = AuditLogService(self.audit_log_repository)
        self.report_service = ReportService(self.database)
