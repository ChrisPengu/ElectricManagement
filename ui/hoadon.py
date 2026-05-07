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
    QDateEdit,
)

from ui.dialogs import show_info, show_warning
from ui.common_styles import PAGE_STYLE


PAID_STATUS = "Đã thanh toán"
UNPAID_STATUS = "Chưa thanh toán"


class HoaDonForm(QWidget):
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

        stats_row = QHBoxLayout()
        stats_row.setSpacing(14)
        self.stat_total = self.build_stat_card("Tong hoa don", "0")
        self.stat_paid = self.build_stat_card("Da thanh toan", "0")
        self.stat_unpaid = self.build_stat_card("Chua thanh toan", "0")
        stats_row.addWidget(self.stat_total)
        stats_row.addWidget(self.stat_paid)
        stats_row.addWidget(self.stat_unpaid)

        card = QFrame()
        card.setProperty("class", "card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(14)

        eyebrow = QLabel("QUAN LY HOA DON")
        eyebrow.setProperty("class", "sectionEyebrow")

        title = QLabel("Danh sach hoa don tien dien")
        title.setProperty("class", "sectionTitle")

        desc = QLabel(
            "Tao hoa don tu chi so cong to theo dung ky, theo doi trang thai va xuat phieu hoa don."
        )
        desc.setProperty("class", "sectionDesc")
        desc.setWordWrap(True)

        filter_row = QHBoxLayout()
        filter_row.setSpacing(10)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Tim theo ma hoa don hoac ma ho")

        self.customer_box = QComboBox()

        self.date_period = QDateEdit()
        self.date_period.setDate(QDate.currentDate())
        self.date_period.setCalendarPopup(True)
        self.date_period.setDisplayFormat("MM/yyyy")

        self.status_filter = QComboBox()
        self.status_filter.addItem("Tat ca trang thai", None)
        self.status_filter.addItem("Da thanh toan", PAID_STATUS)
        self.status_filter.addItem("Chua thanh toan", UNPAID_STATUS)

        self.btn_create = QPushButton("Tao hoa don")
        self.btn_detail = QPushButton("Xem chi tiet")
        self.btn_detail.setProperty("variant", "secondary")
        self.btn_export = QPushButton("Xuat hoa don")
        self.btn_export.setProperty("variant", "secondary")
        self.btn_refresh = QPushButton("Lam moi")
        self.btn_refresh.setProperty("variant", "secondary")

        filter_row.addWidget(self.search_box, 1)
        filter_row.addWidget(self.customer_box)
        filter_row.addWidget(self.date_period)
        filter_row.addWidget(self.status_filter)
        filter_row.addWidget(self.btn_create)
        filter_row.addWidget(self.btn_detail)
        filter_row.addWidget(self.btn_export)
        filter_row.addWidget(self.btn_refresh)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Ma HD", "Ma ho", "Ky hoa don", "So tien", "Trang thai"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setMinimumHeight(380)

        self.btn_create.clicked.connect(self.create_invoice)
        self.btn_detail.clicked.connect(self.show_invoice_detail)
        self.btn_export.clicked.connect(self.export_selected_invoice)
        self.btn_refresh.clicked.connect(self.refresh_data)
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
        card.value_label = value

        layout.addWidget(label)
        layout.addWidget(value)
        return card

    def refresh_data(self):
        self.load_customers()
        self.load_invoices()

    def load_customers(self):
        if not self.context:
            return
        current_code = self.customer_box.currentData().customer_code if self.customer_box.currentData() else None
        self.customer_box.clear()
        for customer in self.context.customer_service.list_customers():
            self.customer_box.addItem(f"{customer.customer_code} - {customer.owner_name}", customer)
            if customer.customer_code == current_code:
                self.customer_box.setCurrentIndex(self.customer_box.count() - 1)

    def load_invoices(self):
        if not self.context:
            return
        keyword = self.search_box.text().strip().casefold()
        status_value = self.status_filter.currentData()
        invoices = self.context.invoice_service.list_invoices()

        self.stat_total.value_label.setText(str(len(invoices)))
        self.stat_paid.value_label.setText(str(len([invoice for invoice in invoices if invoice.status == PAID_STATUS])))
        self.stat_unpaid.value_label.setText(str(len([invoice for invoice in invoices if invoice.status == UNPAID_STATUS])))

        if status_value:
            invoices = [invoice for invoice in invoices if invoice.status == status_value]
        if keyword:
            invoices = [
                invoice
                for invoice in invoices
                if keyword in invoice.invoice_code.casefold() or keyword in invoice.customer_code.casefold()
            ]

        self.table.setRowCount(len(invoices))
        for row, invoice in enumerate(invoices):
            values = [
                invoice.invoice_code,
                invoice.customer_code,
                invoice.billing_period,
                f"{invoice.amount:,} VND".replace(",", "."),
                invoice.status,
            ]
            for col, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col, item)

    def create_invoice(self):
        customer = self.customer_box.currentData()
        if not customer:
            show_warning(self, "Thieu du lieu", "Chua co ho dan de tao hoa don.")
            return
        try:
            period = self.date_period.date().toString("MM/yyyy")
            invoice = self.context.invoice_service.create_invoice_for_customer(
                customer.customer_code,
                period,
                self.current_user_id,
            )
            self.context.audit_log_service.record(
                self.current_user_id or 0,
                "CREATE",
                "invoices",
                invoice.invoice_code,
                "Tao hoa don tu chi so cong to.",
            )
            self.load_invoices()
            show_info(self, "Da tao hoa don", f"Da tao hoa don {invoice.invoice_code}.")
        except Exception as exc:
            show_warning(self, "Khong the tao hoa don", str(exc))

    def selected_invoice_code(self):
        row = self.table.currentRow()
        if row < 0 or self.table.item(row, 0) is None:
            return None
        return self.table.item(row, 0).text()

    def show_invoice_detail(self):
        invoice_code = self.selected_invoice_code()
        if not invoice_code:
            show_warning(self, "Chua chon hoa don", "Vui long chon mot hoa don trong bang.")
            return
        invoice = self.context.invoice_service.invoice_repository.get_by_code(invoice_code)
        if invoice is None:
            show_warning(self, "Khong tim thay", "Hoa don khong con ton tai trong database.")
            return
        show_info(
            self,
            "Chi tiet hoa don",
            "\n".join(
                [
                    f"Ma hoa don: {invoice.invoice_code}",
                    f"Ma ho: {invoice.customer_code}",
                    f"Ky: {invoice.billing_period}",
                    f"So tien: {invoice.amount:,} VND".replace(",", "."),
                    f"Trang thai: {invoice.status.value}",
                ]
            ),
        )

    def export_selected_invoice(self):
        invoice_code = self.selected_invoice_code()
        if not invoice_code:
            show_warning(self, "Chua chon hoa don", "Vui long chon mot hoa don de xuat file.")
            return
        invoice = self.context.invoice_service.invoice_repository.get_by_code(invoice_code)
        if invoice is None:
            show_warning(self, "Khong tim thay", "Hoa don khong con ton tai trong database.")
            return

        export_dir = self.context.database.db_path.parent
        export_dir.mkdir(parents=True, exist_ok=True)
        path = export_dir / f"{invoice.invoice_code}.txt"
        path.write_text(
            "HOA DON TIEN DIEN\n"
            f"Ma hoa don: {invoice.invoice_code}\n"
            f"Ma ho: {invoice.customer_code}\n"
            f"Ky: {invoice.billing_period}\n"
            f"So tien: {invoice.amount:,} VND\n".replace(",", ".")
            + f"Trang thai: {invoice.status.value}\n",
            encoding="utf-8",
        )
        show_info(self, "Da xuat file", f"Da xuat hoa don: {path}")
