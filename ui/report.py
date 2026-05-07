from PyQt5.QtCore import QDate, Qt, QRect
from PyQt5.QtGui import QColor, QFont, QPainter, QPen
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QDateEdit,
    QFrame,
)

from ui.dialogs import show_info
from ui.common_styles import PAGE_STYLE


class BarChartWidget(QWidget):
    def __init__(self, title: str, color: str = "#2f80ed"):
        super().__init__()
        self.title = title
        self.color = QColor(color)
        self.data = []
        self.value_suffix = ""
        self.setFixedHeight(205)

    def set_data(self, data: list[dict], value_suffix: str = ""):
        self.data = data
        self.value_suffix = value_suffix
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect().adjusted(18, 16, -18, -24)
        painter.setPen(QPen(QColor("#15385f")))
        title_font = QFont("Segoe UI", 11, QFont.Bold)
        painter.setFont(title_font)
        painter.drawText(
            int(rect.left()),
            int(rect.top()),
            int(rect.width()),
            24,
            Qt.AlignLeft | Qt.AlignVCenter,
            self.title,
        )

        chart_rect = QRect(rect.left(), rect.top() + 40, rect.width(), rect.height() - 64)
        painter.setPen(QPen(QColor("#d8e7f5"), 1))
        painter.drawLine(chart_rect.left(), chart_rect.bottom(), chart_rect.right(), chart_rect.bottom())

        if not self.data:
            painter.setPen(QColor("#6f849b"))
            painter.drawText(chart_rect, Qt.AlignCenter, "Chua co du lieu")
            painter.end()
            return

        max_value = max(item["value"] for item in self.data) or 1
        gap = 12
        bar_width = max(24, int((chart_rect.width() - gap * (len(self.data) - 1)) / len(self.data)))
        label_font = QFont("Segoe UI", 8)
        painter.setFont(label_font)

        for index, item in enumerate(self.data):
            x = int(chart_rect.left() + index * (bar_width + gap))
            value = item["value"]
            bar_height = int((value / max_value) * (chart_rect.height() - 42))
            y = int(chart_rect.bottom() - bar_height)
            bar_rect = QRect(x, y, bar_width, bar_height)

            painter.setPen(Qt.NoPen)
            painter.setBrush(self.color)
            painter.drawRoundedRect(bar_rect, 5, 5)

            painter.setPen(QColor("#15385f"))
            value_text = self._format_value(value)
            painter.drawText(QRect(x - 8, y - 20, bar_width + 16, 18), Qt.AlignCenter, value_text)
            painter.setPen(QColor("#6f849b"))
            painter.drawText(QRect(x - 10, chart_rect.bottom() + 8, bar_width + 20, 22), Qt.AlignCenter, item["label"])

        painter.end()

    def _format_value(self, value: int) -> str:
        if self.value_suffix == "VND":
            if value >= 1_000_000:
                return f"{value / 1_000_000:.1f}tr"
            if value >= 1_000:
                return f"{value / 1_000:.0f}k"
        return str(value)


class SummaryChartWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.invoice_status = []
        self.contract_types = []
        self.setFixedHeight(150)

    def set_data(self, invoice_status: list[dict], contract_types: list[dict]):
        self.invoice_status = invoice_status
        self.contract_types = contract_types
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(14, 14, -14, -12)

        painter.setPen(QColor("#15385f"))
        painter.setFont(QFont("Segoe UI", 11, QFont.Bold))
        painter.drawText(
            int(rect.left()),
            int(rect.top()),
            int(rect.width()),
            24,
            Qt.AlignLeft | Qt.AlignVCenter,
            "Co cau hoa don va hop dong",
        )

        left = QRect(rect.left(), rect.top() + 36, int(rect.width() / 2 - 12), rect.height() - 40)
        right = QRect(rect.left() + int(rect.width() / 2 + 12), rect.top() + 36, int(rect.width() / 2 - 12), rect.height() - 40)
        self._draw_list(painter, left, "Trang thai hoa don", self.invoice_status, QColor("#2f80ed"))
        self._draw_list(painter, right, "Loai hop dong", self.contract_types, QColor("#14a06f"))
        painter.end()

    def _draw_list(self, painter, rect, title, data, color):
        painter.setPen(QColor("#35516e"))
        painter.setFont(QFont("Segoe UI", 9, QFont.Bold))
        painter.drawText(
            int(rect.left()),
            int(rect.top()),
            int(rect.width()),
            20,
            Qt.AlignLeft | Qt.AlignVCenter,
            title,
        )

        if not data:
            painter.setPen(QColor("#6f849b"))
            painter.drawText(rect, Qt.AlignCenter, "Chua co du lieu")
            return

        total = sum(item["value"] for item in data) or 1
        y = rect.top() + 28
        painter.setFont(QFont("Segoe UI", 9))
        for index, item in enumerate(data):
            percent = item["value"] / total
            bar_width = int((rect.width() - 95) * percent)
            row_rect = QRect(int(rect.left()), int(y), int(rect.width()), 24)

            painter.setPen(QColor("#15385f"))
            painter.drawText(
                int(row_rect.left()),
                int(row_rect.top()),
                86,
                24,
                Qt.AlignLeft | Qt.AlignVCenter,
                item["label"],
            )
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor("#edf6ff"))
            painter.drawRoundedRect(QRect(row_rect.left() + 92, row_rect.top() + 5, int(rect.width() - 95), 12), 6, 6)
            painter.setBrush(color.lighter(100 + index * 20))
            painter.drawRoundedRect(QRect(row_rect.left() + 92, row_rect.top() + 5, bar_width, 12), 6, 6)
            painter.setPen(QColor("#15385f"))
            painter.drawText(row_rect, Qt.AlignRight | Qt.AlignVCenter, str(item["value"]))
            y += 28


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

        eyebrow = QLabel("BAO CAO")
        eyebrow.setProperty("class", "sectionEyebrow")

        title = QLabel("Bao cao - thong ke van hanh")
        title.setProperty("class", "sectionTitle")

        desc = QLabel("Tong hop nhanh ho dan, hoa don, doanh thu, cong no va su co dang xu ly.")
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

        self.btn_report = QPushButton("Xem bao cao")
        self.btn_export = QPushButton("Xuat file")
        self.btn_export.setProperty("variant", "secondary")

        row.addWidget(QLabel("Tu ngay:"))
        row.addWidget(self.date_from)
        row.addWidget(QLabel("Den ngay:"))
        row.addWidget(self.date_to)
        row.addWidget(self.btn_report)
        row.addWidget(self.btn_export)

        filter_layout.addWidget(eyebrow)
        filter_layout.addWidget(title)
        filter_layout.addWidget(desc)
        filter_layout.addLayout(row)

        stats_row = QHBoxLayout()
        stats_row.setSpacing(14)
        self.stat_customers = self.build_stat_card("Tong so ho", "0")
        self.stat_revenue = self.build_stat_card("Doanh thu da thu", "0")
        self.stat_unpaid = self.build_stat_card("Hoa don chua thanh toan", "0")
        stats_row.addWidget(self.stat_customers)
        stats_row.addWidget(self.stat_revenue)
        stats_row.addWidget(self.stat_unpaid)

        chart_card = QFrame()
        chart_card.setProperty("class", "card")
        chart_layout = QVBoxLayout(chart_card)
        chart_layout.setContentsMargins(22, 20, 22, 20)
        chart_layout.setSpacing(12)

        chart_title = QLabel("Bieu do thong ke")
        chart_title.setProperty("class", "sectionTitle")

        chart_desc = QLabel("Doanh thu, san luong tieu thu va co cau du lieu duoc ve truc tiep tu MongoDB.")
        chart_desc.setProperty("class", "sectionDesc")
        chart_desc.setWordWrap(True)

        chart_row_top = QHBoxLayout()
        chart_row_top.setSpacing(14)
        self.revenue_chart = BarChartWidget("Doanh thu theo ky", "#2f80ed")
        self.consumption_chart = BarChartWidget("San luong tieu thu theo ky", "#14a06f")
        chart_row_top.addWidget(self.revenue_chart)
        chart_row_top.addWidget(self.consumption_chart)

        self.summary_chart = SummaryChartWidget()

        chart_layout.addWidget(chart_title)
        chart_layout.addWidget(chart_desc)
        chart_layout.addLayout(chart_row_top)
        chart_layout.addSpacing(12)
        chart_layout.addWidget(self.summary_chart)

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
        dashboard = self.context.report_service.dashboard()
        self.stat_customers.value_label.setText(str(summary["customers"]))
        self.stat_revenue.value_label.setText(f"{summary['revenue']:,} VND".replace(",", "."))
        self.stat_unpaid.value_label.setText(str(summary["unpaid_invoices"]))

        self.revenue_chart.set_data(dashboard["monthly_revenue"], "VND")
        self.consumption_chart.set_data(dashboard["monthly_consumption"], "kWh")
        self.summary_chart.set_data(dashboard["invoice_status"], dashboard["contract_types"])

    def refresh_data(self):
        self.load_report()

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
        show_info(self, "Da xuat file", f"Da xuat bao cao: {path}")
