from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QDateEdit,
    QFrame,
    QMessageBox,
)
from PyQt5.QtCore import QDate

from ui.common_styles import PAGE_STYLE


class ReportForm(QWidget):
    def __init__(self, context=None):
        super().__init__()
        self.context = context
        self.build_ui()
        self.load_report()

    def build_ui(self):
        self.setStyleSheet(PAGE_STYLE)

        root = QVBoxLayout(self)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(18)

        filter_card = QFrame()
        filter_card.setProperty("class", "card")
        filter_layout = QVBoxLayout(filter_card)
        filter_layout.setContentsMargins(22, 20, 22, 20)
        filter_layout.setSpacing(12)

        eyebrow = QLabel("BÁO CÁO")
        eyebrow.setProperty("class", "sectionEyebrow")

        title = QLabel("Bộ lọc báo cáo")
        title.setProperty("class", "sectionTitle")

        desc = QLabel("Lọc theo khoảng thời gian để xem nhanh các chỉ số vận hành chính của hệ thống.")
        desc.setProperty("class", "sectionDesc")
        desc.setWordWrap(True)

        row = QHBoxLayout()
        row.setSpacing(10)
        self.date_from = QDateEdit()
        self.date_to = QDateEdit()
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        self.date_to.setDate(QDate.currentDate())
        self.date_from.setCalendarPopup(True)
        self.date_to.setCalendarPopup(True)

        self.btn_report = QPushButton("Xem báo cáo")
        self.btn_export = QPushButton("Xuất file")
        self.btn_export.setProperty("variant", "secondary")

        row.addWidget(QLabel("Từ ngày:"))
        row.addWidget(self.date_from)
        row.addWidget(QLabel("Đến ngày:"))
        row.addWidget(self.date_to)
        row.addWidget(self.btn_report)
        row.addWidget(self.btn_export)

        filter_layout.addWidget(eyebrow)
        filter_layout.addWidget(title)
        filter_layout.addWidget(desc)
        filter_layout.addLayout(row)

        stats_row = QHBoxLayout()
        stats_row.setSpacing(14)
        self.stat_customers = self.build_stat_card("Tổng số hộ", "0")
        self.stat_revenue = self.build_stat_card("Doanh thu đã thu", "0")
        self.stat_unpaid = self.build_stat_card("Hóa đơn chưa thanh toán", "0")
        stats_row.addWidget(self.stat_customers)
        stats_row.addWidget(self.stat_revenue)
        stats_row.addWidget(self.stat_unpaid)

        chart_card = QFrame()
        chart_card.setProperty("class", "card")
        chart_layout = QVBoxLayout(chart_card)
        chart_layout.setContentsMargins(22, 20, 22, 20)
        chart_layout.setSpacing(12)

        chart_title = QLabel("Khu vực biểu đồ / thống kê mở rộng")
        chart_title.setProperty("class", "sectionTitle")

        chart_desc = QLabel(
            "Hiện tại đây là vùng placeholder để gắn biểu đồ doanh thu, sản lượng tiêu thụ hoặc tỷ lệ thanh toán trong bước phát triển tiếp theo."
        )
        chart_desc.setProperty("class", "sectionDesc")
        chart_desc.setWordWrap(True)

        chart_placeholder = QFrame()
        chart_placeholder.setProperty("class", "softCard")
        placeholder_layout = QVBoxLayout(chart_placeholder)
        placeholder_layout.setContentsMargins(24, 24, 24, 24)
        placeholder_layout.setSpacing(8)

        placeholder_title = QLabel("Biểu đồ đang chờ tích hợp")
        placeholder_title.setProperty("class", "sectionTitle")

        placeholder_desc = QLabel(
            "Có thể bổ sung biểu đồ cột doanh thu theo tháng, biểu đồ tròn trạng thái hóa đơn "
            "và so sánh hợp đồng hộ gia đình với nhà máy."
        )
        placeholder_desc.setProperty("class", "sectionDesc")
        placeholder_desc.setWordWrap(True)

        placeholder_layout.addStretch()
        placeholder_layout.addWidget(placeholder_title)
        placeholder_layout.addWidget(placeholder_desc)
        placeholder_layout.addStretch()

        chart_layout.addWidget(chart_title)
        chart_layout.addWidget(chart_desc)
        chart_layout.addWidget(chart_placeholder, 1)

        self.btn_report.clicked.connect(self.load_report)
        self.btn_export.clicked.connect(self.export_report)

        root.addWidget(filter_card)
        root.addLayout(stats_row)
        root.addWidget(chart_card, 1)

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

    def load_report(self):
        if not self.context:
            return
        summary = self.context.report_service.summary()
        self.stat_customers.value_label.setText(str(summary["customers"]))
        self.stat_revenue.value_label.setText(f"{summary['revenue']:,} VND".replace(",", "."))
        self.stat_unpaid.value_label.setText(str(summary["unpaid_invoices"]))

    def export_report(self):
        if not self.context:
            return
        summary = self.context.report_service.summary()
        path = self.context.database.db_path.parent / "report_summary.csv"
        path.write_text(
            "metric,value\n"
            f"customers,{summary['customers']}\n"
            f"invoices,{summary['invoices']}\n"
            f"unpaid_invoices,{summary['unpaid_invoices']}\n"
            f"revenue,{summary['revenue']}\n"
            f"incidents_open,{summary['incidents_open']}\n",
            encoding="utf-8",
        )
        QMessageBox.information(self, "Đã xuất file", f"Đã xuất báo cáo: {path}")
