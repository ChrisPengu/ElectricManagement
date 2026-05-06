from app.core.database import DatabaseManager
from app.models import ContractType, Customer


class CustomerRepository:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def list_all(self) -> list[Customer]:
        rows = self.db.fetch_all(
            """
            SELECT id, customer_code, owner_name, address, phone_number, contract_type
            FROM customers
            ORDER BY customer_code
            """
        )

        return [
            Customer(
                id=row["id"],
                customer_code=row["customer_code"],
                owner_name=row["owner_name"],
                address=row["address"],
                phone_number=row["phone_number"],
                contract_type=ContractType(row["contract_type"]),
            )
            for row in rows
        ]

    def get_by_code(self, customer_code: str) -> Customer | None:
        row = self.db.fetch_one(
            """
            SELECT id, customer_code, owner_name, address, phone_number, contract_type
            FROM customers
            WHERE customer_code = ?
            """,
            (customer_code,),
        )
        if row is None:
            return None
        return Customer(
            id=row["id"],
            customer_code=row["customer_code"],
            owner_name=row["owner_name"],
            address=row["address"],
            phone_number=row["phone_number"],
            contract_type=ContractType(row["contract_type"]),
        )

    def create(self, customer: Customer) -> Customer:
        self.db.execute(
            """
            INSERT INTO customers (customer_code, owner_name, address, phone_number, contract_type)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                customer.customer_code,
                customer.owner_name,
                customer.address,
                customer.phone_number,
                customer.contract_type.value,
            ),
        )
        return self.get_by_code(customer.customer_code) or customer

    def update(self, customer: Customer) -> Customer:
        self.db.execute(
            """
            UPDATE customers
            SET owner_name = ?, address = ?, phone_number = ?, contract_type = ?
            WHERE customer_code = ?
            """,
            (
                customer.owner_name,
                customer.address,
                customer.phone_number,
                customer.contract_type.value,
                customer.customer_code,
            ),
        )
        return self.get_by_code(customer.customer_code) or customer

    def delete(self, customer_code: str) -> None:
        self.db.execute(
            """
            DELETE FROM customers
            WHERE customer_code = ?
            """,
            (customer_code,),
        )
