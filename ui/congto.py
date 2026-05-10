from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QFrame,
    QLineEdit,
    QPushButton,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QDateEdit,
)

from app.dto.requests import MeterReadingCreateDTO
from ui.common_styles import PAGE_STYLE
from ui.dialogs import show_info, show_warning


class CongToForm(QWidget):
    def __init__(self, context=None):
        super().__init__()
        self.context = context
        self.current_user_id = None
        self.build_ui()
        self.load_customers()
        self.load_readings()

    def set_current_user_id(self, user_id):
        self.current_user_id = user_id

    def build_ui(self):
        self.setStyleSheet(PAGE_STYLE)

        root = QVBoxLayout(self)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(18)

        intro_card = QFrame()
        intro_card.setProperty("class", "card")
        intro_layout = QVBoxLayout(intro_card)
        intro_layout.setContentsMargins(22, 20, 22, 20)
        intro_layout.setSpacing(10)

        eyebrow = QLabel("CHỈ SỐ CÔNG TƠ")
        eyebrow.setProperty("class", "sectionEyebrow")

        title = QLabel("Ghi nhận chỉ số điện mới theo kỳ")
        title.setProperty("class", "sectionTitle")

        desc = QLabel(
            "Giao diện này đã được tối ưu lại để chỉ tập trung vào chỉ số mới. "
            "Chỉ số cũ hoặc chỉ số tháng trước sẽ được lấy từ database ở giai đoạn tiếp theo, "
            "tránh nhập liệu lặp và hạn chế sai sót."
        )
        desc.setProperty("class", "sectionDesc")
        desc.setWordWrap(True)

        pill_row = QHBoxLayout()
        pill_row.setSpacing(10)

        pill_one = QLabel("Không nhập chỉ số cũ")
        pill_one.setProperty("class", "infoPill")

        pill_two = QLabel("Sẵn sàng đồng bộ database")
        pill_two.setProperty("class", "infoPill")

        pill_three = QLabel("Tối ưu luồng ghi số")
        pill_three.setProperty("class", "infoPill")

        pill_row.addWidget(pill_one)
        pill_row.addWidget(pill_two)
        pill_row.addWidget(pill_three)
        pill_row.addStretch()

        intro_layout.addWidget(eyebrow)
        intro_layout.addWidget(title)
        intro_layout.addWidget(desc)
        intro_layout.addLayout(pill_row)

        content_row = QHBoxLayout()
        content_row.setSpacing(18)

        input_card = QFrame()
        input_card.setProperty("class", "card")
        input_layout = QVBoxLayout(input_card)
        input_layout.setContentsMargins(22, 20, 22, 20)
        input_layout.setSpacing(16)

        input_title = QLabel("Phiếu ghi chỉ số")
        input_title.setProperty("class", "sectionTitle")

        input_desc = QLabel("Chọn hộ dân, kỳ ghi và nhập chỉ số mới của công tơ.")
        input_desc.setProperty("class", "sectionDesc")
        input_desc.setWordWrap(True)

        form = QFormLayout()
        form.setHorizontalSpacing(18)
        form.setVerticalSpacing(12)
        form.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        lbl_house = QLabel("Hộ dân")
        lbl_house.setProperty("class", "fieldLabel")

        lbl_contract = QLabel("Loại hợp đồng")
        lbl_contract.setProperty("class", "fieldLabel")

        lbl_period = QLabel("Kỳ ghi số")
        lbl_period.setProperty("class", "fieldLabel")

        lbl_new = QLabel("Chỉ số mới")
        lbl_new.setProperty("class", "fieldLabel")

        lbl_note = QLabel("Ghi chú")
        lbl_note.setProperty("class", "fieldLabel")

        self.cbo_hodan = QComboBox()
        self.cbo_hodan.currentTextChanged.connect(self.update_contract_view)

        self.cbo_contract = QComboBox()
        self.cbo_contract.addItems(["Hộ gia đình", "Nhà máy"])
        self.cbo_contract.setCurrentIndex(0)
        self.cbo_contract.setEnabled(False)

        self.date_period = QDateEdit()
        self.date_period.setDate(QDate.currentDate())
        self.date_period.setCalendarPopup(True)
        self.date_period.setDisplayFormat("MM/yyyy")

        self.txt_moi = QLineEdit()
        self.txt_moi.setPlaceholderText("Nhập chỉ số công tơ mới")

        self.txt_note = QLineEdit()
        self.txt_note.setPlaceholderText("Ví dụ: đọc số tại chỗ, đã đối chiếu với chủ hộ, cần kiểm tra lại...")

        form.addRow(lbl_house, self.cbo_hodan)
        form.addRow(lbl_contract, self.cbo_contract)
        form.addRow(lbl_period, self.date_period)
        form.addRow(lbl_new, self.txt_moi)
        form.addRow(lbl_note, self.txt_note)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.btn_save = QPushButton("Ghi nhận chỉ số")
        self.btn_refresh = QPushButton("Làm mới")
        self.btn_refresh.setProperty("variant", "secondary")

        btn_row.addWidget(self.btn_save)
        btn_row.addWidget(self.btn_refresh)
        btn_row.addStretch()

        input_layout.addWidget(input_title)
        input_layout.addWidget(input_desc)
        input_layout.addLayout(form)
        input_layout.addLayout(btn_row)

        history_card = QFrame()
        history_card.setProperty("class", "card")
        history_layout = QVBoxLayout(history_card)
        history_layout.setContentsMargins(22, 20, 22, 20)
        history_layout.setSpacing(12)

        history_title = QLabel("Lịch sử ghi số gần đây")
        history_title.setProperty("class", "sectionTitle")

        history_desc = QLabel("Danh sách minh họa cho các kỳ ghi số đã nhập ở giao diện mới.")
        history_desc.setProperty("class", "sectionDesc")
        history_desc.setWordWrap(True)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["Mã hộ", "Hộ/đơn vị dùng điện", "Loại hợp đồng", "Kỳ ghi", "Chỉ số mới"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setMinimumHeight(330)

        self.btn_save.clicked.connect(self.save_reading)
        self.btn_refresh.clicked.connect(self.refresh_data)

        history_layout.addWidget(history_title)
        history_layout.addWidget(history_desc)
        history_layout.addWidget(self.table)

        content_row.addWidget(input_card, 4)
        content_row.addWidget(history_card, 6)

        root.addWidget(intro_card)
        root.addLayout(content_row, 1)

    def load_customers(self):
        if not self.context:
            return
        self.customers = self.context.customer_service.list_customers()
        self.cbo_hodan.blockSignals(True)
        self.cbo_hodan.clear()
        for customer in self.customers:
            self.cbo_hodan.addItem(f"{customer.customer_code} - {customer.owner_name}", customer)
        self.cbo_hodan.blockSignals(False)
        self.update_contract_view()

    def update_contract_view(self):
        customer = self.cbo_hodan.currentData()
        if customer:
            self.cbo_contract.setCurrentText(customer.contract_type)

    def load_readings(self):
        if not self.context:
            return
        readings = self.context.meter_reading_service.list_recent()
        customers = {customer.customer_code: customer for customer in self.context.customer_service.list_customers()}
        self.table.setRowCount(len(readings))
        for row, reading in enumerate(readings):
            customer = customers.get(reading.customer_code)
            values = [
                reading.customer_code,
                customer.owner_name if customer else "",
                customer.contract_type if customer else "",
                reading.reading_period,
                str(reading.new_index),
            ]
            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col, item)

    def refresh_data(self):
        self.load_customers()
        self.load_readings()

    def save_reading(self):
        customer = self.cbo_hodan.currentData()
        if not customer:
            show_warning(self, "Thiếu dữ liệu", "Chưa có hộ dùng điện để ghi chỉ số.")
            return
        try:
            raw_index = self.txt_moi.text().strip()
            if not raw_index:
                raise ValueError("Vui lòng nhập chỉ số công tơ.")
            new_index = int(raw_index)
            self.context.meter_reading_service.create_reading(
                MeterReadingCreateDTO(
                    customer_code=customer.customer_code,
                    reading_period=self.date_period.date().toString("MM/yyyy"),
                    new_index=new_index,
                    note=self.txt_note.text(),
                ),
                self.current_user_id,
            )
            self.context.audit_log_service.record(
                self.current_user_id,
                "CREATE",
                "meter_readings",
                customer.customer_code,
                "Ghi nhận chỉ số công tơ.",
            )
            self.txt_moi.clear()
            self.txt_note.clear()
            self.load_readings()
            show_info(self, "Đã ghi nhận", "Đã lưu chỉ số công tơ.")
        except ValueError as exc:
            show_warning(self, "Không thể ghi chỉ số", str(exc))
