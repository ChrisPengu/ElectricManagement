from datetime import datetime
from html import escape

from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QTextDocument
from PyQt5.QtPrintSupport import QPrinter
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
    QDialog,
    QTextBrowser,
)

from app.models import ContractType, InvoiceStatus
from ui.dialogs import show_info, show_warning
from ui.common_styles import PAGE_STYLE


PAID_STATUS = InvoiceStatus.PAID.value
UNPAID_STATUS = InvoiceStatus.UNPAID.value


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

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(
            ["Ma HD", "Ma ho", "Ky hoa don", "San luong", "Phi co dinh", "Tong tien", "Trang thai"]
        )
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
                f"{invoice.consumption_kwh:,} kWh".replace(",", "."),
                f"{invoice.fixed_fee:,} VND".replace(",", "."),
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
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Chi tiet hoa don {invoice.invoice_code}")
        dialog.resize(840, 700)
        dialog.setStyleSheet(
            PAGE_STYLE
            + """
            QTextBrowser {
                background: #ffffff;
                border: 1px solid #d8e4f2;
                border-radius: 16px;
                padding: 8px;
            }
            """
        )

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)

        browser = QTextBrowser()
        browser.setHtml(self.build_invoice_html(invoice))
        layout.addWidget(browser, 1)

        button_row = QHBoxLayout()
        button_row.addStretch()
        btn_close = QPushButton("Dong")
        btn_close.clicked.connect(dialog.accept)
        button_row.addWidget(btn_close)
        layout.addLayout(button_row)

        dialog.exec_()

    def export_selected_invoice(self):
        invoice_code = self.selected_invoice_code()
        if not invoice_code:
            show_warning(self, "Chua chon hoa don", "Vui long chon mot hoa don de xuat file.")
            return
        invoice = self.context.invoice_service.invoice_repository.get_by_code(invoice_code)
        if invoice is None:
            show_warning(self, "Khong tim thay", "Hoa don khong con ton tai trong database.")
            return

        self.export_invoice(invoice)

    def export_invoice(self, invoice):
        export_dir = self.context.database.db_path.parent
        export_dir.mkdir(parents=True, exist_ok=True)
        path = export_dir / f"{invoice.invoice_code}.pdf"
        self.write_invoice_pdf(invoice, path)
        show_info(self, "Da xuat file", f"Da xuat hoa don PDF: {path}")

    def write_invoice_pdf(self, invoice, path):
        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(str(path))
        printer.setPageSize(QPrinter.A4)
        printer.setPageMargins(12, 12, 12, 12, QPrinter.Millimeter)

        document = QTextDocument()
        document.setHtml(self.build_invoice_html(invoice, standalone=True))
        document.print_(printer)

    def build_invoice_html(self, invoice, standalone=False):
        customer = self.context.customer_repository.get_by_code(invoice.customer_code) if self.context else None
        tariff = (
            self.context.tariff_repository.get_by_contract_type(customer.contract_type)
            if self.context and customer
            else None
        )

        subtotal = max(invoice.amount - invoice.vat_amount, 0)
        if subtotal == 0 and tariff and tariff.vat_percent:
            subtotal = int(invoice.amount / (1 + tariff.vat_percent / 100))
        vat_amount = invoice.vat_amount or max(invoice.amount - subtotal, 0)
        fixed_fee = invoice.fixed_fee
        energy_cost = max(subtotal - fixed_fee, 0)
        vat_percent = tariff.vat_percent if tariff else (vat_amount * 100 / subtotal if subtotal else 0)
        contract_type = customer.contract_type.value if customer else "Chua xac dinh"
        owner_name = customer.owner_name if customer else "Chua cap nhat"
        address = customer.address if customer else "Chua cap nhat"
        phone_number = customer.phone_number if customer else "Chua cap nhat"
        issued_at = self.format_datetime(invoice.issued_at) or datetime.now().strftime("%d/%m/%Y %H:%M")
        status_class = "paid" if invoice.status == InvoiceStatus.PAID else "unpaid"

        breakdown_rows = self.build_breakdown_rows(invoice, customer, tariff, energy_cost)
        breakdown_html = "".join(
            "<tr>"
            f"<td>{escape(row['label'])}</td>"
            f"<td class='right'>{escape(row['quantity'])}</td>"
            f"<td class='right'>{escape(row['rate'])}</td>"
            f"<td class='right strong'>{escape(row['amount'])}</td>"
            "</tr>"
            for row in breakdown_rows
        )

        styles = """
        <style>
            body {
                margin: 0;
                background: #eef4fb;
                color: #15324d;
                font-family: "Segoe UI", Arial, sans-serif;
                font-size: 13px;
            }
            .invoice {
                max-width: 860px;
                margin: 0 auto;
                background: #ffffff;
                border: 1px solid #d8e4f2;
                border-radius: 18px;
                overflow: hidden;
            }
            .topbar {
                height: 8px;
                background: #2f80ed;
            }
            .header {
                display: flex;
                justify-content: space-between;
                gap: 24px;
                padding: 26px 30px 18px;
                border-bottom: 1px solid #e4edf7;
            }
            .eyebrow {
                color: #4c75a1;
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 1px;
                text-transform: uppercase;
            }
            h1 {
                margin: 6px 0;
                color: #12385f;
                font-size: 28px;
                letter-spacing: 0;
            }
            .muted {
                color: #6f849b;
            }
            .codebox {
                min-width: 230px;
                padding: 16px;
                background: #f6fbff;
                border: 1px solid #d8e7f5;
                border-radius: 14px;
                text-align: right;
            }
            .codebox strong {
                display: block;
                margin: 6px 0 10px;
                color: #12385f;
                font-size: 16px;
            }
            .status {
                display: inline-block;
                padding: 7px 10px;
                border-radius: 999px;
                font-weight: 700;
            }
            .paid {
                color: #176c3a;
                background: #e8f7ee;
                border: 1px solid #bfe7cd;
            }
            .unpaid {
                color: #9a5a10;
                background: #fff4df;
                border: 1px solid #f0d09c;
            }
            .section {
                padding: 20px 30px;
                border-bottom: 1px solid #eaf1f8;
            }
            .grid {
                display: grid;
                grid-template-columns: repeat(2, minmax(0, 1fr));
                gap: 12px 20px;
            }
            .field {
                padding: 12px 14px;
                background: #f8fbfe;
                border: 1px solid #e0ebf6;
                border-radius: 12px;
            }
            .label {
                display: block;
                color: #6f849b;
                font-size: 11px;
                font-weight: 700;
                text-transform: uppercase;
            }
            .value {
                display: block;
                margin-top: 4px;
                color: #173c62;
                font-weight: 700;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 12px;
            }
            th {
                background: #eef5fb;
                color: #163d66;
                padding: 11px 10px;
                text-align: left;
                font-size: 12px;
            }
            td {
                border-bottom: 1px solid #edf2f8;
                padding: 11px 10px;
            }
            .right {
                text-align: right;
            }
            .strong {
                font-weight: 700;
                color: #12385f;
            }
            .totals {
                margin-left: auto;
                max-width: 390px;
            }
            .total-row {
                display: flex;
                justify-content: space-between;
                padding: 9px 0;
                border-bottom: 1px solid #edf2f8;
            }
            .grand {
                margin-top: 8px;
                padding: 14px 16px;
                background: #143d68;
                color: white;
                border-radius: 14px;
                font-size: 18px;
                font-weight: 800;
            }
            .note {
                padding: 16px 30px 26px;
                color: #6f849b;
                font-size: 12px;
            }
            @media print {
                body { background: #ffffff; }
                .invoice { border: none; border-radius: 0; }
            }
        </style>
        """

        body = f"""
        <div class="invoice">
            <div class="topbar"></div>
            <div class="header">
                <div>
                    <div class="eyebrow">Ban quan ly dien khu dan cu</div>
                    <h1>Hoa don tien dien</h1>
                    <div class="muted">Ky hoa don {escape(invoice.billing_period)} - ngay lap {escape(issued_at)}</div>
                </div>
                <div class="codebox">
                    <span class="label">Ma hoa don</span>
                    <strong>{escape(invoice.invoice_code)}</strong>
                    <span class="status {status_class}">{escape(invoice.status.value)}</span>
                </div>
            </div>

            <div class="section">
                <div class="grid">
                    <div class="field"><span class="label">Ma khach hang</span><span class="value">{escape(invoice.customer_code)}</span></div>
                    <div class="field"><span class="label">Ten chu ho / don vi</span><span class="value">{escape(owner_name)}</span></div>
                    <div class="field"><span class="label">Dia chi su dung dien</span><span class="value">{escape(address)}</span></div>
                    <div class="field"><span class="label">Dien thoai</span><span class="value">{escape(phone_number)}</span></div>
                    <div class="field"><span class="label">Loai hop dong</span><span class="value">{escape(contract_type)}</span></div>
                    <div class="field"><span class="label">San luong tieu thu</span><span class="value">{escape(self.format_kwh(invoice.consumption_kwh))}</span></div>
                </div>
            </div>

            <div class="section">
                <div class="eyebrow">Bang tinh tien dien</div>
                <table>
                    <thead>
                        <tr>
                            <th>Noi dung</th>
                            <th class="right">San luong</th>
                            <th class="right">Don gia</th>
                            <th class="right">Thanh tien</th>
                        </tr>
                    </thead>
                    <tbody>{breakdown_html}</tbody>
                </table>
            </div>

            <div class="section">
                <div class="totals">
                    <div class="total-row"><span>Tien dien truoc phi</span><strong>{escape(self.format_money(energy_cost))}</strong></div>
                    <div class="total-row"><span>Phi co dinh</span><strong>{escape(self.format_money(fixed_fee))}</strong></div>
                    <div class="total-row"><span>VAT ({vat_percent:.1f}%)</span><strong>{escape(self.format_money(vat_amount))}</strong></div>
                    <div class="grand">
                        <span>Tong thanh toan</span>
                        <span style="float:right">{escape(self.format_money(invoice.amount))}</span>
                    </div>
                </div>
            </div>

            <div class="note">
                Vui long thanh toan dung han theo ky hoa don. Hoa don duoc tao tu chi so cong to va cau hinh bieu gia dang ap dung trong he thong.
            </div>
        </div>
        """

        if not standalone:
            return styles + body
        return f"<!doctype html><html><head><meta charset='utf-8'><title>{escape(invoice.invoice_code)}</title>{styles}</head><body>{body}</body></html>"

    def build_breakdown_rows(self, invoice, customer, tariff, fallback_energy_cost):
        if not tariff or not customer:
            return [
                {
                    "label": "Dien nang tieu thu",
                    "quantity": self.format_kwh(invoice.consumption_kwh),
                    "rate": "Theo du lieu hoa don",
                    "amount": self.format_money(fallback_energy_cost),
                }
            ]

        if customer.contract_type == ContractType.HOUSEHOLD:
            return self.build_household_breakdown(invoice.consumption_kwh, tariff.price_tiers, fallback_energy_cost)

        effective_rate = int(tariff.base_rate * tariff.peak_multiplier)
        amount = fallback_energy_cost or int(invoice.consumption_kwh * effective_rate)
        return [
            {
                "label": f"San xuat: {self.format_money(tariff.base_rate)}/kWh x he so {tariff.peak_multiplier:.2f}",
                "quantity": self.format_kwh(invoice.consumption_kwh),
                "rate": f"{self.format_money(effective_rate)}/kWh",
                "amount": self.format_money(amount or fallback_energy_cost),
            }
        ]

    def build_household_breakdown(self, consumption_kwh, price_tiers, expected_energy_cost=0):
        rows = []
        calculated_total = 0
        for tier in price_tiers or []:
            lower_bound = max(int(tier.get("from_kwh", 0)), 1)
            if consumption_kwh < lower_bound:
                continue
            to_kwh = tier.get("to_kwh")
            upper_bound = consumption_kwh if to_kwh is None else min(consumption_kwh, int(to_kwh))
            units = max(0, upper_bound - lower_bound + 1)
            if units <= 0:
                continue
            rate = int(tier.get("rate", 0))
            if to_kwh is None:
                tier_label = f"Bac {lower_bound} kWh tro len"
            else:
                tier_label = f"Bac {lower_bound}-{int(to_kwh)} kWh"
            amount = units * rate
            calculated_total += amount
            rows.append(
                {
                    "label": tier_label,
                    "quantity": self.format_kwh(units),
                    "rate": f"{self.format_money(rate)}/kWh",
                    "amount": self.format_money(amount),
                }
            )
        adjustment = int(expected_energy_cost or 0) - calculated_total
        if rows and adjustment:
            rows.append(
                {
                    "label": "Dieu chinh theo tong hoa don da luu",
                    "quantity": "",
                    "rate": "",
                    "amount": self.format_money(adjustment),
                }
            )
        if rows:
            return rows
        return [
            {
                "label": "Dien nang sinh hoat",
                "quantity": self.format_kwh(consumption_kwh),
                "rate": "Theo bieu gia",
                "amount": self.format_money(0),
            }
        ]

    def format_money(self, amount):
        return f"{int(amount or 0):,} VND".replace(",", ".")

    def format_kwh(self, value):
        return f"{int(value or 0):,} kWh".replace(",", ".")

    def format_datetime(self, value):
        if not value:
            return ""
        if isinstance(value, datetime):
            return value.strftime("%d/%m/%Y %H:%M")
        return str(value)
