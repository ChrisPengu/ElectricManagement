from PyQt5.QtCore import QDate, Qt, QRect
from PyQt5.QtGui import QColor, QFont, QPainter, QPen, QBrush, QLinearGradient
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QDateEdit,
    QFrame,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
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
        self.setFixedHeight(245)

    def set_data(self, data: list[dict], value_suffix: str = ""):
        self.data = data
        self.value_suffix = value_suffix
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect().adjusted(18, 16, -18, -16)
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

        chart_rect = QRect(
            int(rect.left() + 46),
            int(rect.top() + 44),
            int(rect.width() - 50),
            int(rect.height() - 76),
        )

        if not self.data:
            painter.setPen(QColor("#6f849b"))
            painter.drawText(chart_rect, Qt.AlignCenter, "Chưa có dữ liệu")
            painter.end()
            return

        visible_data = self.data[-6:]
        max_value = max(item["value"] for item in visible_data) or 1
        nice_max = self._nice_axis_max(max_value)

        painter.setFont(QFont("Segoe UI", 8))
        for tick in range(5):
            ratio = tick / 4
            y = int(chart_rect.bottom() - chart_rect.height() * ratio)
            value = int(nice_max * ratio)
            painter.setPen(QPen(QColor("#edf3f9"), 1))
            painter.drawLine(chart_rect.left(), y, chart_rect.right(), y)
            painter.setPen(QColor("#7a8fa6"))
            painter.drawText(
                QRect(int(rect.left()), y - 9, 40, 18),
                Qt.AlignRight | Qt.AlignVCenter,
                self._format_axis_value(value),
            )

        painter.setPen(QPen(QColor("#cddbea"), 1))
        painter.drawLine(chart_rect.left(), chart_rect.bottom(), chart_rect.right(), chart_rect.bottom())

        gap = 16
        bar_width = max(26, int((chart_rect.width() - gap * (len(visible_data) - 1)) / len(visible_data)))
        label_font = QFont("Segoe UI", 8)
        painter.setFont(label_font)

        for index, item in enumerate(visible_data):
            x = int(chart_rect.left() + index * (bar_width + gap))
            value = item["value"]
            bar_height = int((value / nice_max) * (chart_rect.height() - 12))
            y = int(chart_rect.bottom() - bar_height)
            bar_rect = QRect(x, y, bar_width, bar_height)

            gradient = QLinearGradient(0, y, 0, chart_rect.bottom())
            gradient.setColorAt(0, self.color.lighter(112))
            gradient.setColorAt(1, self.color.darker(108))
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(gradient))
            painter.drawRoundedRect(bar_rect, 6, 6)

            painter.setPen(QColor("#15385f"))
            value_text = self._format_value(value)
            painter.drawText(QRect(x - 8, y - 20, bar_width + 16, 18), Qt.AlignCenter, value_text)
            painter.setPen(QColor("#6f849b"))
            label = str(item["label"])
            painter.drawText(QRect(x - 12, chart_rect.bottom() + 8, bar_width + 24, 22), Qt.AlignCenter, label)

        painter.end()

    def _format_value(self, value: int) -> str:
        if self.value_suffix == "VND":
            if value >= 1_000_000:
                return f"{value / 1_000_000:.1f}tr"
            if value >= 1_000:
                return f"{value / 1_000:.0f}k"
        if self.value_suffix == "kWh":
            if value >= 1_000:
                return f"{value / 1_000:.1f}k"
        return str(value)

    def _format_axis_value(self, value: int) -> str:
        if value == 0:
            return "0"
        return self._format_value(value)

    def _nice_axis_max(self, value: int) -> int:
        target = max(1, int(value * 1.15))
        if target <= 10:
            return 10
        magnitude = 10 ** (len(str(int(target))) - 1)
        for step in [1, 2, 5, 10]:
            candidate = step * magnitude
            if candidate >= target:
                return candidate
        return target


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
            "Cơ cấu hóa đơn và hợp đồng",
        )

        left = QRect(rect.left(), rect.top() + 36, int(rect.width() / 2 - 12), rect.height() - 40)
        right = QRect(rect.left() + int(rect.width() / 2 + 12), rect.top() + 36, int(rect.width() / 2 - 12), rect.height() - 40)
        self._draw_list(painter, left, "Trạng thái hóa đơn", self.invoice_status, QColor("#2f80ed"))
        self._draw_list(painter, right, "Loại hợp đồng", self.contract_types, QColor("#14a06f"))
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
            painter.drawText(rect, Qt.AlignCenter, "Chưa có dữ liệu")
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

        eyebrow = QLabel("BÁO CÁO")
        eyebrow.setProperty("class", "sectionEyebrow")

        title = QLabel("Báo cáo - thống kê vận hành")
        title.setProperty("class", "sectionTitle")

        desc = QLabel("Tổng hợp nhanh hộ dân, hóa đơn, doanh thu, công nợ và sự cố đang xử lý.")
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

        chart_title = QLabel("Biểu đồ thống kê")
        chart_title.setProperty("class", "sectionTitle")

        chart_desc = QLabel("Doanh thu, sản lượng tiêu thụ và cơ cấu dữ liệu được vẽ trực tiếp từ backend đang dùng.")
        chart_desc.setProperty("class", "sectionDesc")
        chart_desc.setWordWrap(True)

        chart_row_top = QHBoxLayout()
        chart_row_top.setSpacing(14)
        self.revenue_chart = BarChartWidget("Doanh thu theo kỳ", "#2f80ed")
        self.consumption_chart = BarChartWidget("Sản lượng tiêu thụ theo kỳ", "#14a06f")
        chart_row_top.addWidget(self.revenue_chart)
        chart_row_top.addWidget(self.consumption_chart)

        self.summary_chart = SummaryChartWidget()

        top_title = QLabel("Top hộ tiêu thụ điện cao nhất")
        top_title.setProperty("class", "sectionTitle")

        self.top_consumers_table = QTableWidget(0, 6)
        self.top_consumers_table.setHorizontalHeaderLabels(
            ["#", "Mã hộ", "Chủ hộ / Đơn vị", "Loại HĐ", "Tổng kWh", "Tổng tiền"]
        )
        self.top_consumers_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.top_consumers_table.verticalHeader().setVisible(False)
        self.top_consumers_table.setAlternatingRowColors(True)
        self.top_consumers_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.top_consumers_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.top_consumers_table.setMinimumHeight(180)

        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(14)
        top_table_layout = QVBoxLayout()
        top_table_layout.setSpacing(8)
        top_table_layout.addWidget(top_title)
        top_table_layout.addWidget(self.top_consumers_table)
        bottom_row.addWidget(self.summary_chart, 1)
        bottom_row.addLayout(top_table_layout, 1)

        chart_layout.addWidget(chart_title)
        chart_layout.addWidget(chart_desc)
        chart_layout.addLayout(chart_row_top)
        chart_layout.addSpacing(12)
        chart_layout.addLayout(bottom_row)

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
        self.load_top_consumers(dashboard.get("top_consumers", []))

    def load_top_consumers(self, rows):
        self.top_consumers_table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            values = [
                row_index + 1,
                row.get("customer_code", ""),
                row.get("owner_name", ""),
                row.get("contract_type", ""),
                f"{row.get('total_kwh', 0):,} kWh".replace(",", "."),
                f"{row.get('total_amount', 0):,} VND".replace(",", "."),
            ]
            for col_index, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                self.top_consumers_table.setItem(row_index, col_index, item)

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
        show_info(self, "Đã xuất file", f"Đã xuất báo cáo: {path}")
