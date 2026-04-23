from app.core.database import DatabaseManager
from app.repositories.auth_repository import AuthRepository
from app.repositories.customer_repository import CustomerRepository
from app.repositories.tariff_repository import TariffRepository
from app.services.auth_service import AuthService
from app.services.billing_service import BillingService
from app.services.customer_service import CustomerService
from app.services.tariff_service import TariffService


class AppContext:
    def __init__(self):
        self.database = DatabaseManager()
        self.database.initialize()

        self.auth_repository = AuthRepository(self.database)
        self.customer_repository = CustomerRepository(self.database)
        self.tariff_repository = TariffRepository(self.database)

        self.auth_service = AuthService(self.auth_repository)
        self.billing_service = BillingService()
        self.customer_service = CustomerService(self.customer_repository)
        self.tariff_service = TariffService(self.tariff_repository)
