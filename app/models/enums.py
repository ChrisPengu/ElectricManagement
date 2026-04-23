from enum import StrEnum


class ContractType(StrEnum):
    HOUSEHOLD = "Hộ gia đình"
    FACTORY = "Nhà máy"


class InvoiceStatus(StrEnum):
    UNPAID = "Chưa thanh toán"
    PAID = "Đã thanh toán"


class IncidentStatus(StrEnum):
    RECEIVED = "Đã tiếp nhận"
    PROCESSING = "Đang xử lý"
    DONE = "Hoàn thành"
