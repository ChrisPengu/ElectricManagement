from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QFrame,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)

from ui.common_styles import PAGE_STYLE


class ThanhToanForm(QWidget):
    def __init__(self):
        super().__init__()
        self.receivable_data = {
            "HDON001 - HD001": {
                "amount": "450.000 VND",
                "status": "Chua thu",
                "method": "Tien mat",
                "collector": "Admin",
            },
            "HDON003 - HD003": {
                "amount": "6.250.000 VND",
                "status": "Cho doi soat",
                "method": "Chuyen khoan",
                "collector": "Admin",
            },
        }
        self.build_ui()
        self.update_receivable_info()

    def build_ui(self):
        self.setStyleSheet(PAGE_STYLE)

        root = QVBoxLayout(self)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(18)

        info_row = QHBoxLayout()
        info_row.setSpacing(14)
        info_row.addWidget(self.build_stat_card("Hoa don can thu", "18"))
        info_row.addWidget(self.build_stat_card("Cho doi soat", "04"))
        info_row.addWidget(self.build_stat_card("Da ghi nhan hom nay", "12"))

        card = QFrame()
        card.setProperty("class", "card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(16)

        eyebrow = QLabel("QUAN LY THU TIEN")
        eyebrow.setProperty("class", "sectionEyebrow")

        title = QLabel("Ghi nhan thu tien va doi soat cong no")
        title.setProperty("class", "sectionTitle")

        desc = QLabel(
            "Admin khong thuc hien thanh toan thay nguoi dung; man hinh nay dung de ghi nhan giao dich thu tien, "
            "cap nhat trang thai hoa don va theo doi doi soat."
        )
        desc.setProperty("class", "sectionDesc")
        desc.setWordWrap(True)

        form = QFormLayout()
        form.setHorizontalSpacing(18)
        form.setVerticalSpacing(12)

        lbl_bill = QLabel("Hoa don can xu ly")
        lbl_bill.setProperty("class", "fieldLabel")

        lbl_amount = QLabel("So tien phai thu")
        lbl_amount.setProperty("class", "fieldLabel")

        lbl_status = QLabel("Trang thai cong no")
        lbl_status.setProperty("class", "fieldLabel")

        lbl_method = QLabel("Kenh thu/doi soat")
        lbl_method.setProperty("class", "fieldLabel")

        lbl_collector = QLabel("Tai khoan ghi nhan")
        lbl_collector.setProperty("class", "fieldLabel")

        self.cbo_bill = QComboBox()
        self.cbo_bill.addItems(list(self.receivable_data.keys()))
        self.cbo_bill.currentTextChanged.connect(self.update_receivable_info)

        self.lbl_amount = QLabel()
        self.lbl_amount.setProperty("class", "valueBox")

        self.lbl_status = QLabel()
        self.lbl_status.setProperty("class", "valueBox")

        self.lbl_method = QLabel()
        self.lbl_method.setProperty("class", "valueBox")

        self.lbl_collector = QLabel()
        self.lbl_collector.setProperty("class", "valueBox")

        form.addRow(lbl_bill, self.cbo_bill)
        form.addRow(lbl_amount, self.lbl_amount)
        form.addRow(lbl_status, self.lbl_status)
        form.addRow(lbl_method, self.lbl_method)
        form.addRow(lbl_collector, self.lbl_collector)

        note_card = QFrame()
        note_card.setProperty("class", "softCard")
        note_layout = QVBoxLayout(note_card)
        note_layout.setContentsMargins(16, 16, 16, 16)
        note_layout.setSpacing(6)

        note_badge = QLabel("Nghiep vu Admin")
        note_badge.setProperty("class", "infoPill")

        note_desc = QLabel(
            "Khi tich hop SQL Server, nut ghi nhan se tao ban ghi thu tien, gan admin_collected_by, "
            "cap nhat trang thai hoa don va luu audit log. Khach hang/ho dan chi la doi tuong cua hoa don."
        )
        note_desc.setProperty("class", "sectionDesc")
        note_desc.setWordWrap(True)

        note_layout.addWidget(note_badge)
        note_layout.addWidget(note_desc)

        btns = QHBoxLayout()
        btns.setSpacing(10)

        btn_confirm = QPushButton("Ghi nhan giao dich thu")
        btn_reconcile = QPushButton("Danh dau da doi soat")
        btn_reconcile.setProperty("variant", "secondary")
        btn_refresh = QPushButton("Lam moi")
        btn_refresh.setProperty("variant", "secondary")

        btns.addWidget(btn_confirm)
        btns.addWidget(btn_reconcile)
        btns.addWidget(btn_refresh)
        btns.addStretch()

        table_title = QLabel("Lich su giao dich gan day")
        table_title.setProperty("class", "sectionTitle")

        self.table = QTableWidget(3, 5)
        self.table.setHorizontalHeaderLabels(["Bien nhan", "Hoa don", "So tien", "Kenh thu", "Admin ghi nhan"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setMinimumHeight(190)

        demo_rows = [
            ["BN001", "HDON002", "520.000", "Tien mat", "Admin"],
            ["BN002", "HDON004", "390.000", "Chuyen khoan", "Admin"],
            ["BN003", "HDON005", "1.240.000", "Chuyen khoan", "Admin"],
        ]
        for row_index, row_data in enumerate(demo_rows):
            for col_index, value in enumerate(row_data):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row_index, col_index, item)

        layout.addWidget(eyebrow)
        layout.addWidget(title)
        layout.addWidget(desc)
        layout.addLayout(form)
        layout.addWidget(note_card)
        layout.addLayout(btns)
        layout.addSpacing(8)
        layout.addWidget(table_title)
        layout.addWidget(self.table)

        root.addLayout(info_row)
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

    def update_receivable_info(self):
        data = self.receivable_data.get(self.cbo_bill.currentText(), {})
        self.lbl_amount.setText(data.get("amount", "0 VND"))
        self.lbl_status.setText(data.get("status", "Chua xac dinh"))
        self.lbl_method.setText(data.get("method", "Chua chon"))
        self.lbl_collector.setText(data.get("collector", "Admin"))
