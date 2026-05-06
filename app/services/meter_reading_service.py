from app.dto.mappers import to_meter_reading_dto
from app.dto.requests import MeterReadingCreateDTO
from app.dto.responses import MeterReadingDTO
from app.models import MeterReading
from app.repositories.customer_repository import CustomerRepository
from app.repositories.meter_reading_repository import MeterReadingRepository


class MeterReadingService:
    def __init__(
        self,
        meter_reading_repository: MeterReadingRepository,
        customer_repository: CustomerRepository,
    ):
        self.meter_reading_repository = meter_reading_repository
        self.customer_repository = customer_repository

    def list_recent(self, limit: int = 50) -> list[MeterReadingDTO]:
        return [to_meter_reading_dto(reading) for reading in self.meter_reading_repository.list_recent(limit)]

    def get_latest_index(self, customer_code: str) -> int:
        latest = self.meter_reading_repository.get_latest_for_customer(customer_code)
        return latest.new_index if latest else 0

    def create_reading(self, request: MeterReadingCreateDTO, recorded_by_user_id: int | None = None) -> MeterReadingDTO:
        customer_code = request.customer_code.strip()
        if self.customer_repository.get_by_code(customer_code) is None:
            raise ValueError("Không tìm thấy hộ dùng điện.")
        if not request.reading_period.strip():
            raise ValueError("Vui lòng chọn kỳ ghi số.")
        if request.new_index < 0:
            raise ValueError("Chỉ số mới không được âm.")
        if self.meter_reading_repository.get_for_customer_period(customer_code, request.reading_period):
            raise ValueError("Hộ này đã có chỉ số cho kỳ đã chọn.")

        previous_index = self.get_latest_index(customer_code)
        if request.new_index < previous_index:
            raise ValueError("Chỉ số mới không được nhỏ hơn chỉ số gần nhất.")

        reading = MeterReading(
            id=None,
            customer_code=customer_code,
            reading_period=request.reading_period.strip(),
            new_index=request.new_index,
            note=request.note.strip(),
        )
        return to_meter_reading_dto(self.meter_reading_repository.create(reading, recorded_by_user_id))
