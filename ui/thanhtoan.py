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
        root.setSpacing(18)

        info_row = QHBoxLayout()
        info_row.setSpacing(14)
        self.stat_receivable_count = self.build_stat_card("Hoa don can thu", "0")
        self.stat_receivable_amount = self.build_stat_card("Tong tien can thu", "0 VND")
        self.stat_payment_count = self.build_stat_card("Giao dich da ghi nhan", "0")
        info_row.addWidget(self.stat_receivable_count)
        info_row.addWidget(self.stat_receivable_amount)
        info_row.addWidget(self.stat_payment_count)

        card = QFrame()
        card.setProperty("class", "card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(16)

        eyebrow = QLabel("QUAN LY THU TIEN")
        eyebrow.setProperty("class", "sectionEyebrow")

        title = QLabel("Ghi nhan thu tien va cap nhat cong no")
        title.setProperty("class", "sectionTitle")

        desc = QLabel(
            "Danh sach hoa don can thu duoc lay truc tiep tu MongoDB. Khi ghi nhan thu, he thong tao bien nhan "
            "va chuyen hoa don sang trang thai da thanh toan."
        )
        desc.setProperty("class", "sectionDesc")
        desc.setWordWrap(True)

        form_row = QHBoxLayout()
        form_row.setSpacing(18)

        left_panel = QFrame()
        left_panel.setObjectName("paymentFormPanel")
        left_panel.setProperty("class", "softCard")
        left_panel.setMinimumHeight(165)
        left_form = QFormLayout(left_panel)
        left_form.setContentsMargins(16, 14, 16, 14)
        left_form.setHorizontalSpacing(12)
        left_form.setVerticalSpacing(8)

        right_panel = QFrame()
        right_panel.setObjectName("paymentFormPanel")
        right_panel.setProperty("class", "softCard")
        right_panel.setMinimumHeight(165)
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
        self.cbo_method.addItems(["Tien mat", "Chuyen khoan", "Vi dien tu"])

        self.txt_payer = QLineEdit()
        self.txt_payer.setPlaceholderText("Ten nguoi nop tien")

        self.txt_note = QLineEdit()
        self.txt_note.setPlaceholderText("Noi dung doi soat neu co")

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

        left_form.addRow(self.build_field_label("Hoa don can xu ly"), self.cbo_bill)
        left_form.addRow(self.build_field_label("So tien phai thu"), self.lbl_amount)
        left_form.addRow(self.build_field_label("Trang thai cong no"), self.lbl_status)
        right_form.addRow(self.build_field_label("Kenh thu"), self.cbo_method)
        right_form.addRow(self.build_field_label("Tai khoan ghi nhan"), self.lbl_collector)
        right_form.addRow(self.build_field_label("Nguoi nop tien"), self.txt_payer)
        right_form.addRow(self.build_field_label("Ghi chu"), self.txt_note)

        form_row.addWidget(left_panel, 1)
        form_row.addWidget(right_panel, 1)

        note_card = QFrame()
        note_card.setProperty("class", "softCard")
        note_layout = QVBoxLayout(note_card)
        note_layout.setContentsMargins(16, 16, 16, 16)
        note_layout.setSpacing(6)

        note_badge = QLabel("Nghiep vu Admin")
        note_badge.setProperty("class", "infoPill")

        note_desc = QLabel(
            "Cach dung: chon hoa don chua thanh toan, chon kenh thu, kiem tra nguoi nop tien, "
            "roi bam ghi nhan. He thong se tao bien nhan va doi hoa don sang da thanh toan."
        )
        note_desc.setProperty("class", "sectionDesc")
        note_desc.setWordWrap(True)

        note_layout.addWidget(note_badge)
        note_layout.addWidget(note_desc)

        btns = QHBoxLayout()
        btns.setSpacing(10)

        self.btn_confirm = QPushButton("Ghi nhan giao dich thu")
        self.btn_refresh = QPushButton("Lam moi")
        self.btn_refresh.setProperty("variant", "secondary")

        btns.addWidget(self.btn_confirm)
        btns.addWidget(self.btn_refresh)
        btns.addStretch()

        table_title = QLabel("Lich su giao dich gan day")
        table_title.setProperty("class", "sectionTitle")

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Bien nhan", "Hoa don", "So tien", "Kenh thu", "Nguoi nop", "Admin"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setMinimumHeight(240)

        self.btn_confirm.clicked.connect(self.confirm_payment)
        self.btn_refresh.clicked.connect(self.refresh_data)

        layout.addWidget(eyebrow)
        layout.addWidget(title)
        layout.addWidget(desc)
        layout.addLayout(form_row)
        layout.addWidget(note_card)
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
        self.lbl_status.setText(data.get("status", "Khong co hoa don can thu"))
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
            self.cbo_bill.addItem("Khong co hoa don chua thanh toan", None)
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
            show_warning(self, "Thieu du lieu", "Khong co hoa don can thu.")
            return
        try:
            payment = self.context.payment_service.create_payment(
                PaymentCreateDTO(
                    receipt_code="",
                    invoice_code=data["invoice_code"],
                    paid_amount=data["raw_amount"],
                    payment_method=self.cbo_method.currentText(),
                    payer_name=self.txt_payer.text().strip() or "Khach hang",
                    collected_by_user_id=self.current_user_id or 1,
                    note=self.txt_note.text().strip(),
                )
            )
            self.context.audit_log_service.record(
                self.current_user_id or 0,
                "CREATE",
                "payments",
                payment.receipt_code,
                "Ghi nhan giao dich thu va cap nhat hoa don.",
            )
            self.txt_note.clear()
            self.refresh_data()
            show_info(self, "Da ghi nhan", f"Da tao bien nhan {payment.receipt_code}.")
        except Exception as exc:
            show_warning(self, "Khong the ghi nhan thu", str(exc))
