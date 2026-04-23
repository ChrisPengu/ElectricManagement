from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QFrame,
)

from ui.common_styles import PAGE_STYLE


class ThanhToanForm(QWidget):
    def __init__(self):
        super().__init__()
        self.bill_data = {
            "HDON001 - HD001": {"amount": "450.000 VNĐ", "status": "Chưa thanh toán", "method": "Tiền mặt"},
            "HDON003 - HD003": {"amount": "6.250.000 VNĐ", "status": "Chưa thanh toán", "method": "Chuyển khoản"},
        }
        self.build_ui()
        self.update_bill_info()

    def build_ui(self):
        self.setStyleSheet(PAGE_STYLE)

        root = QVBoxLayout(self)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(18)

        info_row = QHBoxLayout()
        info_row.setSpacing(14)
        info_row.addWidget(self.build_stat_card("Hóa đơn chờ xử lý", "18"))
        info_row.addWidget(self.build_stat_card("Khách hàng doanh nghiệp", "03"))
        info_row.addWidget(self.build_stat_card("Đã thu hôm nay", "12"))

        card = QFrame()
        card.setProperty("class", "card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(16)

        eyebrow = QLabel("THANH TOÁN")
        eyebrow.setProperty("class", "sectionEyebrow")

        title = QLabel("Xác nhận thanh toán hóa đơn")
        title.setProperty("class", "sectionTitle")

        desc = QLabel("Kiểm tra nhanh số tiền, trạng thái và phương thức thu trước khi xác nhận thanh toán.")
        desc.setProperty("class", "sectionDesc")
        desc.setWordWrap(True)

        form = QFormLayout()
        form.setHorizontalSpacing(18)
        form.setVerticalSpacing(12)

        lbl_bill = QLabel("Chọn hóa đơn")
        lbl_bill.setProperty("class", "fieldLabel")

        lbl_amount = QLabel("Số tiền")
        lbl_amount.setProperty("class", "fieldLabel")

        lbl_status = QLabel("Trạng thái")
        lbl_status.setProperty("class", "fieldLabel")

        lbl_method = QLabel("Phương thức dự kiến")
        lbl_method.setProperty("class", "fieldLabel")

        self.cbo_bill = QComboBox()
        self.cbo_bill.addItems(list(self.bill_data.keys()))
        self.cbo_bill.currentTextChanged.connect(self.update_bill_info)

        self.lbl_amount = QLabel()
        self.lbl_amount.setProperty("class", "valueBox")

        self.lbl_status = QLabel()
        self.lbl_status.setProperty("class", "valueBox")

        self.lbl_method = QLabel()
        self.lbl_method.setProperty("class", "valueBox")

        form.addRow(lbl_bill, self.cbo_bill)
        form.addRow(lbl_amount, self.lbl_amount)
        form.addRow(lbl_status, self.lbl_status)
        form.addRow(lbl_method, self.lbl_method)

        note_card = QFrame()
        note_card.setProperty("class", "softCard")
        note_layout = QVBoxLayout(note_card)
        note_layout.setContentsMargins(16, 16, 16, 16)
        note_layout.setSpacing(6)

        note_badge = QLabel("Gợi ý xử lý")
        note_badge.setProperty("class", "infoPill")

        note_desc = QLabel(
            "Sau khi tích hợp database, thao tác xác nhận thanh toán nên cập nhật trực tiếp trạng thái hóa đơn, "
            "lưu biên nhận và ghi nhận lịch sử giao dịch theo từng nhân viên."
        )
        note_desc.setProperty("class", "sectionDesc")
        note_desc.setWordWrap(True)

        note_layout.addWidget(note_badge)
        note_layout.addWidget(note_desc)

        btns = QHBoxLayout()
        btns.setSpacing(10)

        btn_confirm = QPushButton("Xác nhận thanh toán")
        btn_refresh = QPushButton("Làm mới")
        btn_refresh.setProperty("variant", "secondary")

        btns.addWidget(btn_confirm)
        btns.addWidget(btn_refresh)
        btns.addStretch()

        layout.addWidget(eyebrow)
        layout.addWidget(title)
        layout.addWidget(desc)
        layout.addLayout(form)
        layout.addWidget(note_card)
        layout.addLayout(btns)

        root.addLayout(info_row)
        root.addWidget(card)
        root.addStretch()

    def build_stat_card(self, label_text, value_text):
        card = QFrame()
        card.setProperty("class", "softCard")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(2)

        label = QLabel(label_text)
        label.setProperty("class", "metricLabel")

        value = QLabel(value_text)
        value.setProperty("class", "metricValue")

        layout.addWidget(label)
        layout.addWidget(value)
        return card

    def update_bill_info(self):
        data = self.bill_data.get(self.cbo_bill.currentText(), {})
        self.lbl_amount.setText(data.get("amount", "0 VNĐ"))
        self.lbl_status.setText(data.get("status", "Chưa xác định"))
        self.lbl_method.setText(data.get("method", "Chưa chọn"))
