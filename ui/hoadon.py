from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QFrame,
    QLineEdit,
    QComboBox,
    QMessageBox,
)

from ui.common_styles import PAGE_STYLE


class HoaDonForm(QWidget):
    def __init__(self, context=None):
        super().__init__()
        self.context = context
        self.current_user_id = None
        self.build_ui()
        self.load_customers()
        self.load_invoices()

    def set_current_user_id(self, user_id):
        self.current_user_id = user_id

    def build_ui(self):
        self.setStyleSheet(PAGE_STYLE)

        root = QVBoxLayout(self)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(18)

        stats_row = QHBoxLayout()
        stats_row.setSpacing(14)
        stats_row.addWidget(self.build_stat_card("Hóa đơn kỳ này", "45"))
        stats_row.addWidget(self.build_stat_card("Đã thanh toán", "27"))
        stats_row.addWidget(self.build_stat_card("Chưa thanh toán", "18"))

        card = QFrame()
        card.setProperty("class", "card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(14)

        eyebrow = QLabel("QUẢN LÝ HÓA ĐƠN")
        eyebrow.setProperty("class", "sectionEyebrow")

        title = QLabel("Danh sách hóa đơn điện")
        title.setProperty("class", "sectionTitle")

        desc = QLabel("Theo dõi kỳ hóa đơn, số tiền và trạng thái thanh toán trên cùng một bảng dữ liệu.")
        desc.setProperty("class", "sectionDesc")
        desc.setWordWrap(True)

        filter_row = QHBoxLayout()
        filter_row.setSpacing(10)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Tìm theo mã hóa đơn hoặc mã hộ")

        self.customer_box = QComboBox()

        self.status_filter = QComboBox()
        self.status_filter.addItems(["Tất cả trạng thái", "Đã thanh toán", "Chưa thanh toán"])

        self.btn_create = QPushButton("Tạo hóa đơn")
        btn_detail = QPushButton("Xem chi tiết")
        btn_detail.setProperty("variant", "secondary")
        btn_print = QPushButton("In hóa đơn")
        btn_print.setProperty("variant", "secondary")

        filter_row.addWidget(self.search_box, 1)
        filter_row.addWidget(self.customer_box)
        filter_row.addWidget(self.status_filter)
        filter_row.addWidget(self.btn_create)
        filter_row.addWidget(btn_detail)
        filter_row.addWidget(btn_print)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Mã HĐ", "Mã hộ", "Kỳ hóa đơn", "Số tiền", "Trạng thái"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setMinimumHeight(380)

        self.btn_create.clicked.connect(self.create_invoice)
        self.search_box.textChanged.connect(self.load_invoices)
        self.status_filter.currentTextChanged.connect(self.load_invoices)

        layout.addWidget(eyebrow)
        layout.addWidget(title)
        layout.addWidget(desc)
        layout.addLayout(filter_row)
        layout.addWidget(self.table)

        root.addLayout(stats_row)
        root.addWidget(card, 1)

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

    def load_customers(self):
        if not self.context:
            return
        self.customer_box.clear()
        for customer in self.context.customer_service.list_customers():
            self.customer_box.addItem(f"{customer.customer_code} - {customer.owner_name}", customer)

    def load_invoices(self):
        if not self.context:
            return
        keyword = self.search_box.text().strip().casefold()
        status = self.status_filter.currentText()
        invoices = self.context.invoice_service.list_invoices()
        if status != "Tất cả trạng thái":
            invoices = [invoice for invoice in invoices if invoice.status == status]
        if keyword:
            invoices = [
                invoice for invoice in invoices
                if keyword in invoice.invoice_code.casefold() or keyword in invoice.customer_code.casefold()
            ]
        self.table.setRowCount(len(invoices))
        for row, invoice in enumerate(invoices):
            values = [
                invoice.invoice_code,
                invoice.customer_code,
                invoice.billing_period,
                f"{invoice.amount:,}".replace(",", "."),
                invoice.status,
            ]
            for col, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col, item)

    def create_invoice(self):
        customer = self.customer_box.currentData()
        if not customer:
            QMessageBox.warning(self, "Thiếu dữ liệu", "Chưa có hộ dùng điện để tạo hóa đơn.")
            return
        try:
            period = QDate.currentDate().toString("MM/yyyy")
            invoice = self.context.invoice_service.create_invoice_for_customer(
                customer.customer_code,
                period,
                self.current_user_id,
            )
            self.context.audit_log_service.record(
                self.current_user_id,
                "CREATE",
                "invoices",
                invoice.invoice_code,
                "Tạo hóa đơn từ chỉ số công tơ.",
            )
            self.load_invoices()
        except Exception as exc:
            QMessageBox.warning(self, "Không thể tạo hóa đơn", str(exc))
