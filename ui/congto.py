from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QFrame,
    QLineEdit,
    QPushButton,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QDateEdit,
)

from ui.common_styles import PAGE_STYLE


class CongToForm(QWidget):
    def __init__(self):
        super().__init__()
        self.build_ui()

    def build_ui(self):
        self.setStyleSheet(PAGE_STYLE)

        root = QVBoxLayout(self)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(18)

        intro_card = QFrame()
        intro_card.setProperty("class", "card")
        intro_layout = QVBoxLayout(intro_card)
        intro_layout.setContentsMargins(22, 20, 22, 20)
        intro_layout.setSpacing(10)

        eyebrow = QLabel("CHỈ SỐ CÔNG TƠ")
        eyebrow.setProperty("class", "sectionEyebrow")

        title = QLabel("Ghi nhận chỉ số điện mới theo kỳ")
        title.setProperty("class", "sectionTitle")

        desc = QLabel(
            "Giao diện này đã được tối ưu lại để chỉ tập trung vào chỉ số mới. "
            "Chỉ số cũ hoặc chỉ số tháng trước sẽ được lấy từ database ở giai đoạn tiếp theo, "
            "tránh nhập liệu lặp và hạn chế sai sót."
        )
        desc.setProperty("class", "sectionDesc")
        desc.setWordWrap(True)

        pill_row = QHBoxLayout()
        pill_row.setSpacing(10)

        pill_one = QLabel("Không nhập chỉ số cũ")
        pill_one.setProperty("class", "infoPill")

        pill_two = QLabel("Sẵn sàng đồng bộ database")
        pill_two.setProperty("class", "infoPill")

        pill_three = QLabel("Tối ưu luồng ghi số")
        pill_three.setProperty("class", "infoPill")

        pill_row.addWidget(pill_one)
        pill_row.addWidget(pill_two)
        pill_row.addWidget(pill_three)
        pill_row.addStretch()

        intro_layout.addWidget(eyebrow)
        intro_layout.addWidget(title)
        intro_layout.addWidget(desc)
        intro_layout.addLayout(pill_row)

        content_row = QHBoxLayout()
        content_row.setSpacing(18)

        input_card = QFrame()
        input_card.setProperty("class", "card")
        input_layout = QVBoxLayout(input_card)
        input_layout.setContentsMargins(22, 20, 22, 20)
        input_layout.setSpacing(16)

        input_title = QLabel("Phiếu ghi chỉ số")
        input_title.setProperty("class", "sectionTitle")

        input_desc = QLabel("Chọn hộ dân, kỳ ghi và nhập chỉ số mới của công tơ.")
        input_desc.setProperty("class", "sectionDesc")
        input_desc.setWordWrap(True)

        form = QFormLayout()
        form.setHorizontalSpacing(18)
        form.setVerticalSpacing(12)
        form.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        lbl_house = QLabel("Hộ dân")
        lbl_house.setProperty("class", "fieldLabel")

        lbl_contract = QLabel("Loại hợp đồng")
        lbl_contract.setProperty("class", "fieldLabel")

        lbl_period = QLabel("Kỳ ghi số")
        lbl_period.setProperty("class", "fieldLabel")

        lbl_new = QLabel("Chỉ số mới")
        lbl_new.setProperty("class", "fieldLabel")

        lbl_note = QLabel("Ghi chú")
        lbl_note.setProperty("class", "fieldLabel")

        self.cbo_hodan = QComboBox()
        self.cbo_hodan.addItems(
            [
                "HD001 - Nguyễn Văn A",
                "HD002 - Trần Thị B",
                "HD003 - Xưởng May Hòa Phát",
            ]
        )

        self.cbo_contract = QComboBox()
        self.cbo_contract.addItems(["Hộ gia đình", "Hộ gia đình", "Nhà máy"])
        self.cbo_contract.setCurrentIndex(0)

        self.date_period = QDateEdit()
        self.date_period.setDate(QDate.currentDate())
        self.date_period.setCalendarPopup(True)
        self.date_period.setDisplayFormat("MM/yyyy")

        self.txt_moi = QLineEdit()
        self.txt_moi.setPlaceholderText("Nhập chỉ số công tơ mới")

        self.txt_note = QLineEdit()
        self.txt_note.setPlaceholderText("Ví dụ: đọc số tại chỗ, khách hàng xác nhận, kiểm tra lại...")

        form.addRow(lbl_house, self.cbo_hodan)
        form.addRow(lbl_contract, self.cbo_contract)
        form.addRow(lbl_period, self.date_period)
        form.addRow(lbl_new, self.txt_moi)
        form.addRow(lbl_note, self.txt_note)

        notice_card = QFrame()
        notice_card.setProperty("class", "softCard")
        notice_layout = QVBoxLayout(notice_card)
        notice_layout.setContentsMargins(16, 16, 16, 16)
        notice_layout.setSpacing(6)

        notice_badge = QLabel("Luồng nhập mới")
        notice_badge.setProperty("class", "infoPill")

        notice_desc = QLabel(
            "Chỉ số cũ đã được loại bỏ khỏi màn hình này. Khi tích hợp database, hệ thống sẽ tự truy xuất chỉ số kỳ trước "
            "để tính ra sản lượng tiêu thụ và phục vụ bước lập hóa đơn."
        )
        notice_desc.setProperty("class", "sectionDesc")
        notice_desc.setWordWrap(True)

        notice_layout.addWidget(notice_badge)
        notice_layout.addWidget(notice_desc)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        btn_save = QPushButton("Ghi nhận chỉ số")
        btn_refresh = QPushButton("Làm mới")
        btn_refresh.setProperty("variant", "secondary")

        btn_row.addWidget(btn_save)
        btn_row.addWidget(btn_refresh)
        btn_row.addStretch()

        input_layout.addWidget(input_title)
        input_layout.addWidget(input_desc)
        input_layout.addLayout(form)
        input_layout.addWidget(notice_card)
        input_layout.addLayout(btn_row)

        history_card = QFrame()
        history_card.setProperty("class", "card")
        history_layout = QVBoxLayout(history_card)
        history_layout.setContentsMargins(22, 20, 22, 20)
        history_layout.setSpacing(12)

        history_title = QLabel("Lịch sử ghi số gần đây")
        history_title.setProperty("class", "sectionTitle")

        history_desc = QLabel("Danh sách minh họa cho các kỳ ghi số đã nhập ở giao diện mới.")
        history_desc.setProperty("class", "sectionDesc")
        history_desc.setWordWrap(True)

        self.table = QTableWidget(3, 5)
        self.table.setHorizontalHeaderLabels(
            ["Mã hộ", "Khách hàng", "Loại hợp đồng", "Kỳ ghi", "Chỉ số mới"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setMinimumHeight(330)

        demo = [
            ["HD001", "Nguyễn Văn A", "Hộ gia đình", "04/2026", "1350"],
            ["HD002", "Trần Thị B", "Hộ gia đình", "04/2026", "1105"],
            ["HD003", "Xưởng May Hòa Phát", "Nhà máy", "04/2026", "8620"],
        ]

        for row_index, row_data in enumerate(demo):
            for col_index, value in enumerate(row_data):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row_index, col_index, item)

        history_layout.addWidget(history_title)
        history_layout.addWidget(history_desc)
        history_layout.addWidget(self.table)

        content_row.addWidget(input_card, 4)
        content_row.addWidget(history_card, 6)

        root.addWidget(intro_card)
        root.addLayout(content_row, 1)
