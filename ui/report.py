from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QDateEdit,
    QFrame,
)
from PyQt5.QtCore import QDate

from ui.common_styles import PAGE_STYLE


class ReportForm(QWidget):
    def __init__(self):
        super().__init__()
        self.build_ui()

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

        btn_report = QPushButton("Xem báo cáo")
        btn_export = QPushButton("Xuất file")
        btn_export.setProperty("variant", "secondary")

        row.addWidget(QLabel("Từ ngày:"))
        row.addWidget(self.date_from)
        row.addWidget(QLabel("Đến ngày:"))
        row.addWidget(self.date_to)
        row.addWidget(btn_report)
        row.addWidget(btn_export)

        filter_layout.addWidget(eyebrow)
        filter_layout.addWidget(title)
        filter_layout.addWidget(desc)
        filter_layout.addLayout(row)

        stats_row = QHBoxLayout()
        stats_row.setSpacing(14)
        stats_row.addWidget(self.build_stat_card("Tổng số hộ", "125"))
        stats_row.addWidget(self.build_stat_card("Doanh thu tháng này", "52.0M"))
        stats_row.addWidget(self.build_stat_card("Hóa đơn chưa thanh toán", "18"))

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

        layout.addWidget(label)
        layout.addWidget(value)
        return card
