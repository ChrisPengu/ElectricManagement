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

from app.dto.requests import MeterReadingCreateDTO, MeterReadingUpdateDTO
from ui.common_styles import PAGE_STYLE
from ui.dialogs import show_info, show_warning


class CongToForm(QWidget):
    def __init__(self, context=None):
        super().__init__()
        self.context = context
        self.current_user_id = None
        self.customers = []
        self.editing_key = None
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

        title = QLabel("Ghi nhận và sửa chỉ số điện theo kỳ")
        title.setProperty("class", "sectionTitle")

        desc = QLabel(
            "Chọn hộ dân, kỳ ghi sổ và nhập chỉ số mới. Nếu nhập sai, chọn dòng trong lịch sử "
            "rồi bấm Sửa chỉ số để nạp lại lên form."
        )
        desc.setProperty("class", "sectionDesc")
        desc.setWordWrap(True)

        pill_row = QHBoxLayout()
        pill_row.setSpacing(10)
        for text in ["Kiểm tra tháng trước", "Kiểm tra tháng sau khi sửa", "Có nhật ký thao tác"]:
            pill = QLabel(text)
            pill.setProperty("class", "infoPill")
            pill_row.addWidget(pill)
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

        input_desc = QLabel("Dữ liệu sửa sẽ ghi đè vào đúng mã hộ và kỳ ghi sổ đang chọn.")
        input_desc.setProperty("class", "sectionDesc")
        input_desc.setWordWrap(True)

        form = QFormLayout()
        form.setHorizontalSpacing(18)
        form.setVerticalSpacing(12)
        form.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)

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
        self.txt_note.setPlaceholderText("Ghi chú đối soát nếu có")

        form.addRow(self.build_field_label("Hộ dân"), self.cbo_hodan)
        form.addRow(self.build_field_label("Loại hợp đồng"), self.cbo_contract)
        form.addRow(self.build_field_label("Kỳ ghi sổ"), self.date_period)
        form.addRow(self.build_field_label("Chỉ số mới"), self.txt_moi)
        form.addRow(self.build_field_label("Ghi chú"), self.txt_note)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.btn_save = QPushButton("Ghi nhận chỉ số")
        self.btn_edit_selected = QPushButton("Sửa chỉ số")
        self.btn_edit_selected.setProperty("variant", "secondary")
        self.btn_cancel_edit = QPushButton("Hủy sửa")
        self.btn_cancel_edit.setProperty("variant", "secondary")
        self.btn_refresh = QPushButton("Làm mới")
        self.btn_refresh.setProperty("variant", "secondary")

        btn_row.addWidget(self.btn_save)
        btn_row.addWidget(self.btn_edit_selected)
        btn_row.addWidget(self.btn_cancel_edit)
        btn_row.addWidget(self.btn_refresh)
        btn_row.addStretch()

        self.edit_hint = QLabel("Đang thêm mới chỉ số.")
        self.edit_hint.setProperty("class", "sectionDesc")

        input_layout.addWidget(input_title)
        input_layout.addWidget(input_desc)
        input_layout.addLayout(form)
        input_layout.addWidget(self.edit_hint)
        input_layout.addLayout(btn_row)

        history_card = QFrame()
        history_card.setProperty("class", "card")
        history_layout = QVBoxLayout(history_card)
        history_layout.setContentsMargins(22, 20, 22, 20)
        history_layout.setSpacing(12)

        history_title = QLabel("Lịch sử ghi sổ gần đây")
        history_title.setProperty("class", "sectionTitle")

        history_desc = QLabel("Chọn một dòng để sửa khi phát hiện nhập sai chỉ số công tơ.")
        history_desc.setProperty("class", "sectionDesc")
        history_desc.setWordWrap(True)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(
            ["Mã hộ", "Hộ dân / Đơn vị", "Loại hợp đồng", "Kỳ ghi", "Chỉ số mới", "Ghi chú"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setMinimumHeight(380)

        self.btn_save.clicked.connect(self.save_reading)
        self.btn_edit_selected.clicked.connect(self.start_edit_selected)
        self.btn_cancel_edit.clicked.connect(self.cancel_edit)
        self.btn_refresh.clicked.connect(self.refresh_data)
        self.table.doubleClicked.connect(self.start_edit_selected)

        history_layout.addWidget(history_title)
        history_layout.addWidget(history_desc)
        history_layout.addWidget(self.table)

        content_row.addWidget(input_card, 4)
        content_row.addWidget(history_card, 7)

        root.addWidget(intro_card)
        root.addLayout(content_row, 1)

    def build_field_label(self, text):
        label = QLabel(text)
        label.setProperty("class", "fieldLabel")
        return label

    def load_customers(self):
        if not self.context:
            return
        current_code = self.cbo_hodan.currentData().customer_code if self.cbo_hodan.currentData() else None
        self.customers = self.context.customer_service.list_customers()
        self.cbo_hodan.blockSignals(True)
        self.cbo_hodan.clear()
        for customer in self.customers:
            self.cbo_hodan.addItem(f"{customer.customer_code} - {customer.owner_name}", customer)
            if customer.customer_code == current_code:
                self.cbo_hodan.setCurrentIndex(self.cbo_hodan.count() - 1)
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
                reading.note,
            ]
            for col, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col, item)

    def refresh_data(self):
        self.load_customers()
        self.load_readings()

    def selected_reading_key(self):
        row = self.table.currentRow()
        if row < 0 or self.table.item(row, 0) is None or self.table.item(row, 3) is None:
            return None
        return self.table.item(row, 0).text(), self.table.item(row, 3).text()

    def start_edit_selected(self):
        key = self.selected_reading_key()
        if not key:
            show_warning(self, "Chưa chọn chỉ số", "Vui lòng chọn một dòng trong bảng lịch sử.")
            return

        customer_code, reading_period = key
        row = self.table.currentRow()
        index_text = self.table.item(row, 4).text() if self.table.item(row, 4) else ""
        note_text = self.table.item(row, 5).text() if self.table.item(row, 5) else ""

        self.select_customer(customer_code)
        date = QDate.fromString(reading_period, "MM/yyyy")
        if date.isValid():
            self.date_period.setDate(date)
        self.txt_moi.setText(index_text)
        self.txt_note.setText(note_text)
        self.editing_key = key
        self.btn_save.setText("Lưu chỉ số đã sửa")
        self.cbo_hodan.setEnabled(False)
        self.date_period.setEnabled(False)
        self.edit_hint.setText(f"Đang sửa chỉ số: {customer_code} - kỳ {reading_period}.")

    def select_customer(self, customer_code):
        for index in range(self.cbo_hodan.count()):
            customer = self.cbo_hodan.itemData(index)
            if customer and customer.customer_code == customer_code:
                self.cbo_hodan.setCurrentIndex(index)
                break

    def cancel_edit(self):
        self.editing_key = None
        self.btn_save.setText("Ghi nhận chỉ số")
        self.cbo_hodan.setEnabled(True)
        self.date_period.setEnabled(True)
        self.edit_hint.setText("Đang thêm mới chỉ số.")
        self.txt_moi.clear()
        self.txt_note.clear()

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
            period = self.date_period.date().toString("MM/yyyy")
            note = self.txt_note.text().strip()

            if self.editing_key:
                original_customer_code, original_period = self.editing_key
                result = self.context.meter_reading_service.update_reading(
                    MeterReadingUpdateDTO(
                        customer_code=original_customer_code,
                        reading_period=original_period,
                        new_index=new_index,
                        note=note,
                    ),
                    self.current_user_id,
                )
                self.context.audit_log_service.record(
                    self.current_user_id or 0,
                    "UPDATE",
                    "meter_readings",
                    f"{result.customer_code}-{result.reading_period}",
                    "Sửa chỉ số công tơ do nhập sai.",
                )
                message = "Đã cập nhật chỉ số công tơ. Nếu hóa đơn kỳ này đã lập, cần kiểm tra lại hóa đơn."
            else:
                result = self.context.meter_reading_service.create_reading(
                    MeterReadingCreateDTO(
                        customer_code=customer.customer_code,
                        reading_period=period,
                        new_index=new_index,
                        note=note,
                    ),
                    self.current_user_id,
                )
                self.context.audit_log_service.record(
                    self.current_user_id or 0,
                    "CREATE",
                    "meter_readings",
                    f"{result.customer_code}-{result.reading_period}",
                    "Ghi nhận chỉ số công tơ.",
                )
                message = "Đã lưu chỉ số công tơ."

            self.cancel_edit()
            self.load_readings()
            show_info(self, "Đã ghi nhận", message)
        except ValueError as exc:
            show_warning(self, "Không thể ghi chỉ số", str(exc))
