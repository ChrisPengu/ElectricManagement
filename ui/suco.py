from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QFrame,
)

from ui.common_styles import PAGE_STYLE


class SuCoForm(QWidget):
    def __init__(self):
        super().__init__()
        self.build_ui()

    def build_ui(self):
        self.setStyleSheet(PAGE_STYLE)

        root = QVBoxLayout(self)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(18)

        body_row = QHBoxLayout()
        body_row.setSpacing(18)

        card_top = QFrame()
        card_top.setProperty("class", "card")
        top_layout = QVBoxLayout(card_top)
        top_layout.setContentsMargins(22, 20, 22, 20)
        top_layout.setSpacing(16)

        eyebrow = QLabel("SỰ CỐ KỸ THUẬT")
        eyebrow.setProperty("class", "sectionEyebrow")

        title = QLabel("Tiếp nhận và phân loại sự cố điện")
        title.setProperty("class", "sectionTitle")

        desc = QLabel("Ghi nhận sự cố theo hộ dân hoặc đơn vị sản xuất để hỗ trợ đội kỹ thuật xử lý nhanh hơn.")
        desc.setProperty("class", "sectionDesc")
        desc.setWordWrap(True)

        form = QFormLayout()
        form.setHorizontalSpacing(18)
        form.setVerticalSpacing(12)

        self.cbo_house = QComboBox()
        self.cbo_house.addItems(["HD001", "HD002", "HD003"])

        self.cbo_type = QComboBox()
        self.cbo_type.addItems(["Mất điện", "Hỏng công tơ", "Chập điện", "Khác"])

        self.cbo_priority = QComboBox()
        self.cbo_priority.addItems(["Trung bình", "Cao", "Khẩn cấp"])

        self.txt_desc = QLineEdit()
        self.txt_desc.setPlaceholderText("Mô tả ngắn sự cố")

        labels = []
        for text in ["Mã hộ", "Loại sự cố", "Mức ưu tiên", "Mô tả"]:
            lbl = QLabel(text)
            lbl.setProperty("class", "fieldLabel")
            labels.append(lbl)

        form.addRow(labels[0], self.cbo_house)
        form.addRow(labels[1], self.cbo_type)
        form.addRow(labels[2], self.cbo_priority)
        form.addRow(labels[3], self.txt_desc)

        btns = QHBoxLayout()
        btns.setSpacing(10)
        btn_record = QPushButton("Ghi nhận")
        btn_update = QPushButton("Cập nhật trạng thái")
        btn_update.setProperty("variant", "secondary")
        btns.addWidget(btn_record)
        btns.addWidget(btn_update)
        btns.addStretch()

        top_layout.addWidget(eyebrow)
        top_layout.addWidget(title)
        top_layout.addWidget(desc)
        top_layout.addLayout(form)
        top_layout.addLayout(btns)

        card_bottom = QFrame()
        card_bottom.setProperty("class", "card")
        bottom_layout = QVBoxLayout(card_bottom)
        bottom_layout.setContentsMargins(22, 20, 22, 20)
        bottom_layout.setSpacing(12)

        lbl2 = QLabel("Danh sách sự cố")
        lbl2.setProperty("class", "sectionTitle")

        table_desc = QLabel("Danh sách minh họa kèm mức ưu tiên và trạng thái xử lý để theo dõi trực quan hơn.")
        table_desc.setProperty("class", "sectionDesc")
        table_desc.setWordWrap(True)

        search_row = QHBoxLayout()
        search_row.setSpacing(10)

        search_box = QLineEdit()
        search_box.setPlaceholderText("Tìm theo mã hộ hoặc mô tả sự cố")

        status_filter = QComboBox()
        status_filter.addItems(["Tất cả trạng thái", "Đã tiếp nhận", "Đang xử lý", "Hoàn thành"])

        search_row.addWidget(search_box, 1)
        search_row.addWidget(status_filter)

        self.table = QTableWidget(3, 5)
        self.table.setHorizontalHeaderLabels(["Mã hộ", "Loại sự cố", "Ưu tiên", "Mô tả", "Trạng thái"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setMinimumHeight(350)

        demo = [
            ["HD001", "Mất điện", "Khẩn cấp", "Mất điện từ tối qua", "Đang xử lý"],
            ["HD002", "Hỏng công tơ", "Trung bình", "Công tơ không hiển thị", "Đã tiếp nhận"],
            ["HD003", "Chập điện", "Cao", "Có mùi khét ở tủ điện", "Hoàn thành"],
        ]

        for r, row in enumerate(demo):
            for c, val in enumerate(row):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(r, c, item)

        bottom_layout.addWidget(lbl2)
        bottom_layout.addWidget(table_desc)
        bottom_layout.addLayout(search_row)
        bottom_layout.addWidget(self.table)

        body_row.addWidget(card_top, 4)
        body_row.addWidget(card_bottom, 6)

        root.addLayout(body_row, 1)
