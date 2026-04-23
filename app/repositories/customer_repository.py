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
