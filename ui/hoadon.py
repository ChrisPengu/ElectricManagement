from PyQt5.QtCore import Qt
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
)

from ui.common_styles import PAGE_STYLE


class HoaDonForm(QWidget):
    def __init__(self):
        super().__init__()
        self.build_ui()

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

        search_box = QLineEdit()
        search_box.setPlaceholderText("Tìm theo mã hóa đơn hoặc mã hộ")

        status_filter = QComboBox()
        status_filter.addItems(["Tất cả trạng thái", "Đã thanh toán", "Chưa thanh toán"])

        btn_create = QPushButton("Tạo hóa đơn")
        btn_detail = QPushButton("Xem chi tiết")
        btn_detail.setProperty("variant", "secondary")
        btn_print = QPushButton("In hóa đơn")
        btn_print.setProperty("variant", "secondary")

        filter_row.addWidget(search_box, 1)
        filter_row.addWidget(status_filter)
        filter_row.addWidget(btn_create)
        filter_row.addWidget(btn_detail)
        filter_row.addWidget(btn_print)

        self.table = QTableWidget(4, 5)
        self.table.setHorizontalHeaderLabels(["Mã HĐ", "Mã hộ", "Kỳ hóa đơn", "Số tiền", "Trạng thái"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setMinimumHeight(380)

        demo = [
            ["HDON001", "HD001", "04/2026", "450.000", "Chưa thanh toán"],
            ["HDON002", "HD002", "04/2026", "520.000", "Đã thanh toán"],
            ["HDON003", "HD003", "04/2026", "6.250.000", "Chưa thanh toán"],
            ["HDON004", "HD001", "03/2026", "390.000", "Đã thanh toán"],
        ]

        for row_index, row_data in enumerate(demo):
            for col_index, value in enumerate(row_data):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row_index, col_index, item)

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
