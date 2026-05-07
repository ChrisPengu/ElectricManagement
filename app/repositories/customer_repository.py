from app.core.database import DatabaseManager
from app.models import ContractType, Customer


class CustomerRepository:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def list_all(self) -> list[Customer]:
        if self.db.backend == "mongodb":
            rows = self.db.mongo_collection("customers").find({}, sort=[("customer_code", 1)])
            return [self._to_model(row) for row in rows]

        rows = self.db.fetch_all(
            """
            SELECT id, customer_code, owner_name, address, phone_number, contract_type
            FROM customers
            ORDER BY customer_code
            """
        )

        return [self._to_model(row) for row in rows]

    def get_by_code(self, customer_code: str) -> Customer | None:
        if self.db.backend == "mongodb":
            row = self.db.mongo_collection("customers").find_one({"customer_code": customer_code})
            return self._to_model(row) if row else None

        row = self.db.fetch_one(
            """
            SELECT id, customer_code, owner_name, address, phone_number, contract_type
            FROM customers
            WHERE customer_code = ?
            """,
            (customer_code,),
        )
        return self._to_model(row) if row else None

    def create(self, customer: Customer) -> Customer:
        if self.db.backend == "mongodb":
            self.db.mongo_collection("customers").insert_one(
                {
                    "id": self.db.next_sequence("customers"),
                    "customer_code": customer.customer_code,
                    "owner_name": customer.owner_name,
                    "address": customer.address,
                    "phone_number": customer.phone_number,
                    "contract_type": customer.contract_type.value,
                }
            )
            return self.get_by_code(customer.customer_code) or customer

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
        if self.db.backend == "mongodb":
            self.db.mongo_collection("customers").update_one(
                {"customer_code": customer.customer_code},
                {
                    "$set": {
                        "owner_name": customer.owner_name,
                        "address": customer.address,
                        "phone_number": customer.phone_number,
                        "contract_type": customer.contract_type.value,
                    }
                },
            )
            return self.get_by_code(customer.customer_code) or customer

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
        if self.db.backend == "mongodb":
            self.db.mongo_collection("customers").delete_one({"customer_code": customer_code})
            return

        self.db.execute(
            """
            DELETE FROM customers
            WHERE customer_code = ?
            """,
            (customer_code,),
        )

    def _to_model(self, row: dict) -> Customer:
        return Customer(
            id=row.get("id"),
            customer_code=row["customer_code"],
            owner_name=row["owner_name"],
            address=row["address"],
            phone_number=row["phone_number"],
            contract_type=ContractType(row["contract_type"]),
        )
