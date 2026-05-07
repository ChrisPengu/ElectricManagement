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
    QPlainTextEdit,
)

from app.dto.requests import IncidentCreateDTO
from ui.common_styles import PAGE_STYLE
from ui.dialogs import show_info, show_warning


STATUS_RECEIVED = "Đã tiếp nhận"
STATUS_PROCESSING = "Đang xử lý"
STATUS_DONE = "Hoàn thành"


class SuCoForm(QWidget):
    def __init__(self, context=None):
        super().__init__()
        self.context = context
        self.current_user_id = None
        self.build_ui()
        self.refresh_data()

    def set_current_user_id(self, user_id):
        self.current_user_id = user_id

    def build_ui(self):
        self.setStyleSheet(PAGE_STYLE)

        root = QVBoxLayout(self)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(18)

        body_row = QHBoxLayout()
        body_row.setSpacing(18)

        form_card = QFrame()
        form_card.setProperty("class", "card")
        form_layout = QVBoxLayout(form_card)
        form_layout.setContentsMargins(22, 20, 22, 20)
        form_layout.setSpacing(14)

        eyebrow = QLabel("SU CO KY THUAT")
        eyebrow.setProperty("class", "sectionEyebrow")

        title = QLabel("Tiep nhan va cap nhat su co dien")
        title.setProperty("class", "sectionTitle")

        desc = QLabel("Chon mot dong trong bang de sua mo ta hoac cap nhat trang thai xu ly.")
        desc.setProperty("class", "sectionDesc")
        desc.setWordWrap(True)

        form = QFormLayout()
        form.setHorizontalSpacing(18)
        form.setVerticalSpacing(12)

        self.cbo_house = QComboBox()
        self.cbo_type = QComboBox()
        self.cbo_type.addItems(["Mat dien", "Hong cong to", "Chap dien", "Qua tai duong day", "Khac"])

        self.cbo_priority = QComboBox()
        self.cbo_priority.addItems(["Trung binh", "Cao", "Khan cap"])

        self.cbo_status = QComboBox()
        self.cbo_status.addItem("Da tiep nhan", STATUS_RECEIVED)
        self.cbo_status.addItem("Dang xu ly", STATUS_PROCESSING)
        self.cbo_status.addItem("Hoan thanh", STATUS_DONE)

        self.txt_desc = QPlainTextEdit()
        self.txt_desc.setPlaceholderText("Nhap mo ta su co, vi tri, hien tuong va ghi chu xu ly...")
        self.txt_desc.setMinimumHeight(110)

        form.addRow(self.build_field_label("Ho dan / don vi"), self.cbo_house)
        form.addRow(self.build_field_label("Loai su co"), self.cbo_type)
        form.addRow(self.build_field_label("Muc uu tien"), self.cbo_priority)
        form.addRow(self.build_field_label("Trang thai"), self.cbo_status)
        form.addRow(self.build_field_label("Mo ta su co"), self.txt_desc)

        btns = QHBoxLayout()
        btns.setSpacing(10)
        self.btn_record = QPushButton("Ghi nhan moi")
        self.btn_update = QPushButton("Cap nhat su co")
        self.btn_update.setProperty("variant", "secondary")
        self.btn_clear = QPushButton("Xoa form")
        self.btn_clear.setProperty("variant", "secondary")
        btns.addWidget(self.btn_record)
        btns.addWidget(self.btn_update)
        btns.addWidget(self.btn_clear)
        btns.addStretch()

        form_layout.addWidget(eyebrow)
        form_layout.addWidget(title)
        form_layout.addWidget(desc)
        form_layout.addLayout(form)
        form_layout.addLayout(btns)

        list_card = QFrame()
        list_card.setProperty("class", "card")
        list_layout = QVBoxLayout(list_card)
        list_layout.setContentsMargins(22, 20, 22, 20)
        list_layout.setSpacing(12)

        list_title = QLabel("Danh sach su co")
        list_title.setProperty("class", "sectionTitle")

        list_desc = QLabel("Loc, chon va cap nhat trang thai su co theo tien do xu ly thuc te.")
        list_desc.setProperty("class", "sectionDesc")
        list_desc.setWordWrap(True)

        search_row = QHBoxLayout()
        search_row.setSpacing(10)
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Tim theo ma ho, loai su co hoac mo ta")
        self.status_filter = QComboBox()
        self.status_filter.addItem("Tat ca trang thai", None)
        self.status_filter.addItem("Da tiep nhan", STATUS_RECEIVED)
        self.status_filter.addItem("Dang xu ly", STATUS_PROCESSING)
        self.status_filter.addItem("Hoan thanh", STATUS_DONE)
        search_row.addWidget(self.search_box, 1)
        search_row.addWidget(self.status_filter)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Ma ho", "Loai su co", "Uu tien", "Mo ta", "Trang thai"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setMinimumHeight(390)

        self.btn_record.clicked.connect(self.record_incident)
        self.btn_update.clicked.connect(self.update_selected_incident)
        self.btn_clear.clicked.connect(self.clear_form)
        self.table.itemSelectionChanged.connect(self.fill_form_from_selection)
        self.search_box.textChanged.connect(self.load_incidents)
        self.status_filter.currentTextChanged.connect(self.load_incidents)

        list_layout.addWidget(list_title)
        list_layout.addWidget(list_desc)
        list_layout.addLayout(search_row)
        list_layout.addWidget(self.table)

        body_row.addWidget(form_card, 4)
        body_row.addWidget(list_card, 7)
        root.addLayout(body_row, 1)

    def build_field_label(self, text):
        label = QLabel(text)
        label.setProperty("class", "fieldLabel")
        return label

    def load_customers(self):
        if not self.context:
            return
        current_code = self.cbo_house.currentData()
        self.cbo_house.clear()
        for customer in self.context.customer_service.list_customers():
            self.cbo_house.addItem(f"{customer.customer_code} - {customer.owner_name}", customer.customer_code)
            if customer.customer_code == current_code:
                self.cbo_house.setCurrentIndex(self.cbo_house.count() - 1)

    def load_incidents(self):
        if not self.context:
            return
        keyword = self.search_box.text().strip().casefold()
        status = self.status_filter.currentData()
        incidents = self.context.incident_service.list_incidents()
        if status:
            incidents = [incident for incident in incidents if incident.status == status]
        if keyword:
            incidents = [
                incident
                for incident in incidents
                if keyword in incident.customer_code.casefold()
                or keyword in incident.incident_type.casefold()
                or keyword in incident.description.casefold()
            ]

        self.table.setRowCount(len(incidents))
        for row, incident in enumerate(incidents):
            values = [
                incident.customer_code,
                incident.incident_type,
                incident.priority,
                incident.description,
                incident.status,
            ]
            for col, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter if col != 3 else Qt.AlignVCenter | Qt.AlignLeft)
                if col == 0:
                    item.setData(Qt.UserRole, incident.id)
                self.table.setItem(row, col, item)

    def refresh_data(self):
        self.load_customers()
        self.load_incidents()

    def selected_incident_id(self):
        row = self.table.currentRow()
        if row < 0 or self.table.item(row, 0) is None:
            return None
        return self.table.item(row, 0).data(Qt.UserRole)

    def fill_form_from_selection(self):
        row = self.table.currentRow()
        if row < 0:
            return
        customer_code = self.table.item(row, 0).text()
        for index in range(self.cbo_house.count()):
            if self.cbo_house.itemData(index) == customer_code:
                self.cbo_house.setCurrentIndex(index)
                break
        self.cbo_type.setCurrentText(self.table.item(row, 1).text())
        self.cbo_priority.setCurrentText(self.table.item(row, 2).text())
        self.set_status_value(self.table.item(row, 4).text())
        self.txt_desc.setPlainText(self.table.item(row, 3).text())

    def set_status_value(self, status):
        for index in range(self.cbo_status.count()):
            if self.cbo_status.itemData(index) == status:
                self.cbo_status.setCurrentIndex(index)
                return

    def record_incident(self):
        customer_code = self.cbo_house.currentData()
        if not customer_code:
            show_warning(self, "Thieu du lieu", "Chua co ho dan de ghi nhan su co.")
            return
        try:
            incident = self.context.incident_service.create_incident(
                IncidentCreateDTO(
                    customer_code=customer_code,
                    incident_type=self.cbo_type.currentText(),
                    priority=self.cbo_priority.currentText(),
                    description=self.txt_desc.toPlainText(),
                    status=STATUS_RECEIVED,
                ),
                self.current_user_id,
            )
            self.context.audit_log_service.record(
                self.current_user_id or 0,
                "CREATE",
                "incidents",
                str(incident.id),
                "Ghi nhan su co ky thuat.",
            )
            self.clear_form()
            self.load_incidents()
            show_info(self, "Da ghi nhan", "Da them su co moi.")
        except Exception as exc:
            show_warning(self, "Khong the ghi nhan su co", str(exc))

    def update_selected_incident(self):
        incident_id = self.selected_incident_id()
        if incident_id is None:
            show_warning(self, "Chua chon dong", "Vui long chon su co can cap nhat trong bang.")
            return
        try:
            status = self.cbo_status.currentData()
            description = self.txt_desc.toPlainText()
            self.context.incident_service.update_status_description(incident_id, status, description)
            self.context.audit_log_service.record(
                self.current_user_id or 0,
                "UPDATE",
                "incidents",
                str(incident_id),
                "Cap nhat trang thai va mo ta su co.",
            )
            self.load_incidents()
            show_info(self, "Da cap nhat", "Da cap nhat trang thai va mo ta su co.")
        except Exception as exc:
            show_warning(self, "Khong the cap nhat", str(exc))

    def clear_form(self):
        self.cbo_type.setCurrentIndex(0)
        self.cbo_priority.setCurrentIndex(0)
        self.cbo_status.setCurrentIndex(0)
        self.txt_desc.clear()
