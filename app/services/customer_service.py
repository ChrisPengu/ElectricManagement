from app.dto.mappers import to_customer_dto
from app.dto.requests import CustomerCreateDTO, CustomerUpdateDTO
from app.dto.responses import CustomerDTO
from app.models import ContractType, Customer
from app.repositories.customer_repository import CustomerRepository


class CustomerService:
    def __init__(self, customer_repository: CustomerRepository):
        self.customer_repository = customer_repository

    def list_customers(self) -> list[CustomerDTO]:
        return [to_customer_dto(customer) for customer in self.customer_repository.list_all()]

    def create_customer(self, request: CustomerCreateDTO) -> CustomerDTO:
        self._validate_customer_fields(
            request.customer_code,
            request.owner_name,
            request.address,
            request.phone_number,
        )
        if self.customer_repository.get_by_code(request.customer_code):
            raise ValueError("Mã hộ đã tồn tại.")

        customer = Customer(
            id=None,
            customer_code=request.customer_code.strip(),
            owner_name=request.owner_name.strip(),
            address=request.address.strip(),
            phone_number=request.phone_number.strip(),
            contract_type=ContractType(request.contract_type),
        )
        return to_customer_dto(self.customer_repository.create(customer))

    def update_customer(self, request: CustomerUpdateDTO) -> CustomerDTO:
        self._validate_customer_fields(
            request.customer_code,
            request.owner_name,
            request.address,
            request.phone_number,
        )
        if self.customer_repository.get_by_code(request.customer_code) is None:
            raise ValueError("Không tìm thấy hộ cần cập nhật.")

        customer = Customer(
            id=None,
            customer_code=request.customer_code.strip(),
            owner_name=request.owner_name.strip(),
            address=request.address.strip(),
            phone_number=request.phone_number.strip(),
            contract_type=ContractType(request.contract_type),
        )
        return to_customer_dto(self.customer_repository.update(customer))

    def delete_customer(self, customer_code: str) -> None:
        if not customer_code.strip():
            raise ValueError("Chưa chọn hộ cần xóa.")
        self.customer_repository.delete(customer_code.strip())

    def _validate_customer_fields(self, customer_code: str, owner_name: str, address: str, phone_number: str) -> None:
        if not customer_code.strip() or not owner_name.strip() or not address.strip() or not phone_number.strip():
            raise ValueError("Vui lòng nhập đầy đủ thông tin hộ.")
