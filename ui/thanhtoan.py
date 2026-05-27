from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QFrame,
    QLineEdit,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)

from app.dto.requests import PaymentCreateDTO
from ui.dialogs import show_info, show_warning
from ui.common_styles import PAGE_STYLE


PAYMENT_STYLE = """
    QFrame#paymentFormPanel QComboBox,
    QFrame#paymentFormPanel QLineEdit {
        padding: 5px 10px;
        min-height: 18px;
        border-radius: 10px;
    }

    QFrame#paymentFormPanel QLabel[class="valueBox"] {
        padding: 5px 10px;
        min-height: 18px;
        border-radius: 10px;
    }
"""


class ThanhToanForm(QWidget):
    def __init__(self, context=None):
        super().__init__()
        self.context = context
        self.current_user_id = None
        self.receivable_data = {}
        self.build_ui()
        self.refresh_data()

    def set_current_user_id(self, user_id):
        self.current_user_id = user_id

    def build_ui(self):
        self.setStyleSheet(PAGE_STYLE + PAYMENT_STYLE)

        root = QVBoxLayout(self)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(14)

        info_row = QHBoxLayout()
        info_row.setSpacing(14)
        self.stat_receivable_count = self.build_stat_card("Hóa đơn cần thu", "0")
        self.stat_receivable_amount = self.build_stat_card("Tổng tiền cần thu", "0 VND")
        self.stat_payment_count = self.build_stat_card("Giao dịch đã ghi nhận", "0")
        info_row.addWidget(self.stat_receivable_count)
        info_row.addWidget(self.stat_receivable_amount)
        info_row.addWidget(self.stat_payment_count)

        card = QFrame()
        card.setProperty("class", "card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(12)

        eyebrow = QLabel("QUẢN LÝ THU TIỀN")
        eyebrow.setProperty("class", "sectionEyebrow")

        title = QLabel("Ghi nhận thu tiền và cập nhật công nợ")
        title.setProperty("class", "sectionTitle")

        desc = QLabel(
            "Danh sách hóa đơn cần thu được lấy trực tiếp từ backend đang dùng. Khi ghi nhận thu, hệ thống tạo biên nhận "
            "và chuyển hóa đơn sang trạng thái đã thanh toán."
        )
        desc.setProperty("class", "sectionDesc")
        desc.setWordWrap(True)

        form_row = QHBoxLayout()
        form_row.setSpacing(18)

        left_panel = QFrame()
        left_panel.setObjectName("paymentFormPanel")
        left_panel.setProperty("class", "softCard")
        left_panel.setMinimumHeight(190)
        left_form = QFormLayout(left_panel)
        left_form.setContentsMargins(16, 14, 16, 14)
        left_form.setHorizontalSpacing(12)
        left_form.setVerticalSpacing(8)

        right_panel = QFrame()
        right_panel.setObjectName("paymentFormPanel")
        right_panel.setProperty("class", "softCard")
        right_panel.setMinimumHeight(205)
        right_form = QFormLayout(right_panel)
        right_form.setContentsMargins(16, 14, 16, 14)
        right_form.setHorizontalSpacing(12)
        right_form.setVerticalSpacing(8)

        self.cbo_bill = QComboBox()
        self.cbo_bill.currentTextChanged.connect(self.update_receivable_info)

        self.lbl_amount = QLabel()
        self.lbl_amount.setProperty("class", "valueBox")
        self.lbl_amount.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        self.lbl_status = QLabel()
        self.lbl_status.setProperty("class", "valueBox")
        self.lbl_status.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        self.lbl_collector = QLabel()
        self.lbl_collector.setProperty("class", "valueBox")
        self.lbl_collector.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        self.cbo_method = QComboBox()
        self.cbo_method.addItems(["Tiền mặt", "Chuyển khoản", "Ví điện tử"])

        self.txt_payer = QLineEdit()
        self.txt_payer.setPlaceholderText("Tên người nộp tiền")

        self.txt_note = QLineEdit()
        self.txt_note.setPlaceholderText("Nội dung đối soát nếu có")

        for field in [
            self.cbo_bill,
            self.lbl_amount,
            self.lbl_status,
            self.cbo_method,
            self.lbl_collector,
            self.txt_payer,
            self.txt_note,
        ]:
            field.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            field.setFixedHeight(34)

        left_form.addRow(self.build_field_label("Hóa đơn cần xử lý"), self.cbo_bill)
        left_form.addRow(self.build_field_label("Số tiền phải thu"), self.lbl_amount)
        left_form.addRow(self.build_field_label("Trạng thái công nợ"), self.lbl_status)
        right_form.addRow(self.build_field_label("Kênh thu"), self.cbo_method)
        right_form.addRow(self.build_field_label("Tài khoản ghi nhận"), self.lbl_collector)
        right_form.addRow(self.build_field_label("Người nộp tiền"), self.txt_payer)
        right_form.addRow(self.build_field_label("Ghi chú"), self.txt_note)

        form_row.addWidget(left_panel, 1)
        form_row.addWidget(right_panel, 1)

        note_card = QFrame()
        note_card.setProperty("class", "softCard")
        note_layout = QVBoxLayout(note_card)
        note_layout.setContentsMargins(16, 16, 16, 16)
        note_layout.setSpacing(6)

        note_badge = QLabel("Nghiệp vụ Admin")
        note_badge.setProperty("class", "infoPill")

        note_desc = QLabel(
            "Cách dùng: chọn hóa đơn chưa thanh toán, chọn kênh thu, kiểm tra người nộp tiền, "
            "rồi bấm ghi nhận. Hệ thống sẽ tạo biên nhận và đổi hóa đơn sang đã thanh toán."
        )
        note_desc.setProperty("class", "sectionDesc")
        note_desc.setWordWrap(True)

        note_layout.addWidget(note_badge)
        note_layout.addWidget(note_desc)

        btns = QHBoxLayout()
        btns.setSpacing(10)

        self.btn_confirm = QPushButton("Ghi nhận giao dịch thu")
        self.btn_refresh = QPushButton("Làm mới")
        self.btn_refresh.setProperty("variant", "secondary")

        btns.addWidget(self.btn_confirm)
        btns.addWidget(self.btn_refresh)
        btns.addStretch()

        table_title = QLabel("Lịch sử giao dịch gần đây")
        table_title.setProperty("class", "sectionTitle")

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Biên nhận", "Hóa đơn", "Số tiền", "Kênh thu", "Người nộp", "Admin"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setMinimumHeight(300)

        self.btn_confirm.clicked.connect(self.confirm_payment)
        self.btn_refresh.clicked.connect(self.refresh_data)

        layout.addWidget(eyebrow)
        layout.addWidget(title)
        layout.addWidget(desc)
        layout.addLayout(form_row)
        layout.addLayout(btns)
        layout.addSpacing(8)
        layout.addWidget(table_title)
        layout.addWidget(self.table)

        root.addLayout(info_row)
        root.addWidget(card, 1)

    def build_field_label(self, text):
        label = QLabel(text)
        label.setProperty("class", "fieldLabel")
        return label

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
        card.value_label = value

        layout.addWidget(label)
        layout.addWidget(value)
        return card

    def refresh_data(self):
        self.load_receivables()
        self.load_payments()

    def update_receivable_info(self):
        data = self.cbo_bill.currentData() or {}
        self.lbl_amount.setText(data.get("amount", "0 VND"))
        self.lbl_status.setText(data.get("status", "Không có hóa đơn cần thu"))
        self.lbl_collector.setText(data.get("collector", "Admin"))
        self.txt_payer.setText(data.get("payer_name", ""))

    def load_receivables(self):
        if not self.context:
            return
        self.receivable_data = {}
        customers = {customer.customer_code: customer for customer in self.context.customer_service.list_customers()}
        unpaid_invoices = self.context.invoice_service.list_unpaid()
        total_amount = 0

        for invoice in unpaid_invoices:
            customer = customers.get(invoice.customer_code)
            key = f"{invoice.invoice_code} - {invoice.customer_code}"
            total_amount += invoice.amount
            self.receivable_data[key] = {
                "amount": f"{invoice.amount:,} VND".replace(",", "."),
                "raw_amount": invoice.amount,
                "invoice_code": invoice.invoice_code,
                "status": invoice.status,
                "payer_name": customer.owner_name if customer else "",
                "collector": "Admin",
            }

        self.stat_receivable_count.value_label.setText(str(len(unpaid_invoices)))
        self.stat_receivable_amount.value_label.setText(f"{total_amount:,} VND".replace(",", "."))

        self.cbo_bill.blockSignals(True)
        self.cbo_bill.clear()
        if self.receivable_data:
            for key, data in self.receivable_data.items():
                self.cbo_bill.addItem(key, data)
            self.cbo_bill.setEnabled(True)
            self.btn_confirm.setEnabled(True)
        else:
            self.cbo_bill.addItem("Không có hóa đơn chưa thanh toán", None)
            self.cbo_bill.setEnabled(False)
            self.btn_confirm.setEnabled(False)
        self.cbo_bill.blockSignals(False)
        self.update_receivable_info()

    def load_payments(self):
        if not self.context:
            return
        payments = self.context.payment_service.list_recent()
        self.stat_payment_count.value_label.setText(str(len(payments)))
        self.table.setRowCount(len(payments))
        for row, payment in enumerate(payments):
            values = [
                payment.receipt_code,
                payment.invoice_code,
                f"{payment.paid_amount:,} VND".replace(",", "."),
                payment.payment_method,
                payment.payer_name,
                str(payment.collected_by_user_id),
            ]
            for col, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col, item)

    def confirm_payment(self):
        data = self.cbo_bill.currentData()
        if not data:
            show_warning(self, "Thiếu dữ liệu", "Không có hóa đơn cần thu.")
            return
        try:
            payment = self.context.payment_service.create_payment(
                PaymentCreateDTO(
                    receipt_code="",
                    invoice_code=data["invoice_code"],
                    paid_amount=data["raw_amount"],
                    payment_method=self.cbo_method.currentText(),
                    payer_name=self.txt_payer.text().strip() or "Khách hàng",
                    collected_by_user_id=self.current_user_id or 1,
                    note=self.txt_note.text().strip(),
                )
            )
            self.context.audit_log_service.record(
                self.current_user_id or 0,
                "CREATE",
                "payments",
                payment.receipt_code,
                "Ghi nhận giao dịch thu và cập nhật hóa đơn.",
            )
            self.txt_note.clear()
            self.refresh_data()
            show_info(self, "Đã ghi nhận", f"Đã tạo biên nhận {payment.receipt_code}.")
        except Exception as exc:
            show_warning(self, "Không thể ghi nhận thu", str(exc))
