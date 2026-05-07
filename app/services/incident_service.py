from datetime import date

from app.dto.mappers import to_incident_dto
from app.dto.requests import IncidentCreateDTO
from app.dto.responses import IncidentDTO
from app.models import Incident, IncidentStatus
from app.repositories.customer_repository import CustomerRepository
from app.repositories.incident_repository import IncidentRepository


class IncidentService:
    def __init__(self, incident_repository: IncidentRepository, customer_repository: CustomerRepository):
        self.incident_repository = incident_repository
        self.customer_repository = customer_repository

    def list_incidents(self) -> list[IncidentDTO]:
        return [to_incident_dto(incident) for incident in self.incident_repository.list_all()]

    def create_incident(self, request: IncidentCreateDTO, received_by_user_id: int | None = None) -> IncidentDTO:
        customer_code = request.customer_code.strip()
        if self.customer_repository.get_by_code(customer_code) is None:
            raise ValueError("Không tìm thấy hộ dùng điện.")
        if not request.description.strip():
            raise ValueError("Vui lòng nhập mô tả sự cố.")

        incident = Incident(
            id=None,
            customer_code=customer_code,
            incident_type=request.incident_type.strip(),
            priority=request.priority.strip(),
            description=request.description.strip(),
            status=IncidentStatus.RECEIVED,
            received_date=date.today(),
        )
        return to_incident_dto(self.incident_repository.create(incident, received_by_user_id))

    def update_status(self, incident_id: int, status: str) -> None:
        self.incident_repository.update_status(incident_id, IncidentStatus(status))

    def update_status_description(self, incident_id: int, status: str, description: str) -> None:
        description = description.strip()
        if not description:
            raise ValueError("Vui long nhap mo ta su co.")
        self.incident_repository.update_status_description(incident_id, IncidentStatus(status), description)
