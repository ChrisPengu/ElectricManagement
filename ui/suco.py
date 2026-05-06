from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QFrame,
    QMessageBox,
)

from app.dto.requests import IncidentCreateDTO
from ui.common_styles import PAGE_STYLE


class SuCoForm(QWidget):
    def __init__(self, context=None):
        super().__init__()
        self.context = context
        self.current_user_id = None
        self.build_ui()
        self.load_customers()
        self.load_incidents()

    def set_current_user_id(self, user_id):
        self.current_user_id = user_id

    def build_ui(self):
        self.setStyleSheet(PAGE_STYLE)

        root = QVBoxLayout(self)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(18)

        body_row = QHBoxLayout()
        body_row.setSpacing(18)

        card_top = QFrame()
        card_top.setProperty("class", "card")
        top_layout = QVBoxLayout(card_top)
        top_layout.setContentsMargins(22, 20, 22, 20)
        top_layout.setSpacing(16)

        eyebrow = QLabel("SỰ CỐ KỸ THUẬT")
        eyebrow.setProperty("class", "sectionEyebrow")

        title = QLabel("Tiếp nhận và phân loại sự cố điện")
        title.setProperty("class", "sectionTitle")

        desc = QLabel("Ghi nhận sự cố theo hộ dân hoặc đơn vị sản xuất để hỗ trợ đội kỹ thuật xử lý nhanh hơn.")
        desc.setProperty("class", "sectionDesc")
        desc.setWordWrap(True)

        form = QFormLayout()
        form.setHorizontalSpacing(18)
        form.setVerticalSpacing(12)

        self.cbo_house = QComboBox()

        self.cbo_type = QComboBox()
        self.cbo_type.addItems(["Mất điện", "Hỏng công tơ", "Chập điện", "Khác"])

        self.cbo_priority = QComboBox()
        self.cbo_priority.addItems(["Trung bình", "Cao", "Khẩn cấp"])

        self.txt_desc = QLineEdit()
        self.txt_desc.setPlaceholderText("Mô tả ngắn sự cố")

        labels = []
        for text in ["Mã hộ", "Loại sự cố", "Mức ưu tiên", "Mô tả"]:
            lbl = QLabel(text)
            lbl.setProperty("class", "fieldLabel")
            labels.append(lbl)

        form.addRow(labels[0], self.cbo_house)
        form.addRow(labels[1], self.cbo_type)
        form.addRow(labels[2], self.cbo_priority)
        form.addRow(labels[3], self.txt_desc)

        btns = QHBoxLayout()
        btns.setSpacing(10)
        self.btn_record = QPushButton("Ghi nhận")
        self.btn_update = QPushButton("Cập nhật trạng thái")
        self.btn_update.setProperty("variant", "secondary")
        btns.addWidget(self.btn_record)
        btns.addWidget(self.btn_update)
        btns.addStretch()

        top_layout.addWidget(eyebrow)
        top_layout.addWidget(title)
        top_layout.addWidget(desc)
        top_layout.addLayout(form)
        top_layout.addLayout(btns)

        card_bottom = QFrame()
        card_bottom.setProperty("class", "card")
        bottom_layout = QVBoxLayout(card_bottom)
        bottom_layout.setContentsMargins(22, 20, 22, 20)
        bottom_layout.setSpacing(12)

        lbl2 = QLabel("Danh sách sự cố")
        lbl2.setProperty("class", "sectionTitle")

        table_desc = QLabel("Danh sách minh họa kèm mức ưu tiên và trạng thái xử lý để theo dõi trực quan hơn.")
        table_desc.setProperty("class", "sectionDesc")
        table_desc.setWordWrap(True)

        search_row = QHBoxLayout()
        search_row.setSpacing(10)

        search_box = QLineEdit()
        search_box.setPlaceholderText("Tìm theo mã hộ hoặc mô tả sự cố")

        status_filter = QComboBox()
        status_filter.addItems(["Tất cả trạng thái", "Đã tiếp nhận", "Đang xử lý", "Hoàn thành"])

        search_row.addWidget(search_box, 1)
        search_row.addWidget(status_filter)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Mã hộ", "Loại sự cố", "Ưu tiên", "Mô tả", "Trạng thái"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setMinimumHeight(350)

        self.btn_record.clicked.connect(self.record_incident)
        self.btn_update.clicked.connect(self.update_selected_status)

        bottom_layout.addWidget(lbl2)
        bottom_layout.addWidget(table_desc)
        bottom_layout.addLayout(search_row)
        bottom_layout.addWidget(self.table)

        body_row.addWidget(card_top, 4)
        body_row.addWidget(card_bottom, 6)

        root.addLayout(body_row, 1)

    def load_customers(self):
        if not self.context:
            return
        self.cbo_house.clear()
        for customer in self.context.customer_service.list_customers():
            self.cbo_house.addItem(f"{customer.customer_code} - {customer.owner_name}", customer.customer_code)

    def load_incidents(self):
        if not self.context:
            return
        incidents = self.context.incident_service.list_incidents()
        self.table.setRowCount(len(incidents))
        for row, incident in enumerate(incidents):
            values = [
                incident.customer_code,
                incident.incident_type,
                incident.priority,
                incident.description,
                incident.status,
            ]
            item_id = QTableWidgetItem(values[0])
            item_id.setData(Qt.UserRole, incident.id)
            item_id.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 0, item_id)
            for col, value in enumerate(values[1:], start=1):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col, item)

    def record_incident(self):
        customer_code = self.cbo_house.currentData()
        if not customer_code:
            QMessageBox.warning(self, "Thiếu dữ liệu", "Chưa có hộ dùng điện để ghi nhận sự cố.")
            return
        try:
            incident = self.context.incident_service.create_incident(
                IncidentCreateDTO(
                    customer_code=customer_code,
                    incident_type=self.cbo_type.currentText(),
                    priority=self.cbo_priority.currentText(),
                    description=self.txt_desc.text(),
                    status="Đã tiếp nhận",
                ),
                self.current_user_id,
            )
            self.context.audit_log_service.record(
                self.current_user_id,
                "CREATE",
                "incidents",
                str(incident.id),
                "Ghi nhận sự cố kỹ thuật.",
            )
            self.txt_desc.clear()
            self.load_incidents()
        except Exception as exc:
            QMessageBox.warning(self, "Không thể ghi nhận sự cố", str(exc))

    def update_selected_status(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Chưa chọn dòng", "Vui lòng chọn sự cố cần cập nhật.")
            return
        incident_id = self.table.item(row, 0).data(Qt.UserRole)
        try:
            self.context.incident_service.update_status(incident_id, "Đang xử lý")
            self.context.audit_log_service.record(
                self.current_user_id,
                "UPDATE",
                "incidents",
                str(incident_id),
                "Cập nhật trạng thái sự cố.",
            )
            self.load_incidents()
        except Exception as exc:
            QMessageBox.warning(self, "Không thể cập nhật", str(exc))
