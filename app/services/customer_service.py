from app.dto.mappers import to_customer_dto
from app.dto.responses import CustomerDTO
from app.repositories.customer_repository import CustomerRepository


class CustomerService:
    def __init__(self, customer_repository: CustomerRepository):
        self.customer_repository = customer_repository

    def list_customers(self) -> list[CustomerDTO]:
        return [to_customer_dto(customer) for customer in self.customer_repository.list_all()]
