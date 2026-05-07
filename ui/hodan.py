from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QFrame,
    QLabel,
    QComboBox,
    QMessageBox,
)

from app.dto.requests import CustomerCreateDTO, CustomerUpdateDTO
from ui.common_styles import PAGE_STYLE


class HoDanForm(QWidget):
    def __init__(self, context=None):
        super().__init__()
        self.context = context
        self.customers = []
        self.build_ui()
        self.load_customers()

    def build_ui(self):
        self.setStyleSheet(PAGE_STYLE)

        root = QVBoxLayout(self)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(18)

        stats_row = QHBoxLayout()
        stats_row.setSpacing(14)
        stats_row.addWidget(self.build_stat_card("Hộ đang quản lý", "125"))
        stats_row.addWidget(self.build_stat_card("Hợp đồng hộ gia đình", "118"))
        stats_row.addWidget(self.build_stat_card("Hợp đồng nhà máy", "07"))

        body_row = QHBoxLayout()
        body_row.setSpacing(18)

        card_form = QFrame()
        card_form.setProperty("class", "card")

        form_wrapper = QVBoxLayout(card_form)
        form_wrapper.setContentsMargins(22, 20, 22, 20)
        form_wrapper.setSpacing(16)

        eyebrow = QLabel("DANH MỤC HỘ DÂN")
        eyebrow.setProperty("class", "sectionEyebrow")

        title = QLabel("Cập nhật hồ sơ hộ/đơn vị sử dụng điện")
        title.setProperty("class", "sectionTitle")

        desc = QLabel("Quản lý thông tin hộ dân, đơn vị sử dụng điện, địa chỉ và dữ liệu nền cho các phân hệ công tơ, hóa đơn và sự cố.")
        desc.setProperty("class", "sectionDesc")
        desc.setWordWrap(True)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        form.setFormAlignment(Qt.AlignTop)
        form.setHorizontalSpacing(18)
        form.setVerticalSpacing(12)

        lbl_ma = QLabel("Mã hộ")
        lbl_ma.setProperty("class", "fieldLabel")

        lbl_ten = QLabel("Tên chủ hộ")
        lbl_ten.setProperty("class", "fieldLabel")

        lbl_diachi = QLabel("Địa chỉ")
        lbl_diachi.setProperty("class", "fieldLabel")

        lbl_sdt = QLabel("Số điện thoại")
        lbl_sdt.setProperty("class", "fieldLabel")

        lbl_contract = QLabel("Loại hợp đồng")
        lbl_contract.setProperty("class", "fieldLabel")

        self.txt_ma = QLineEdit()
        self.txt_ten = QLineEdit()
        self.txt_diachi = QLineEdit()
        self.txt_sdt = QLineEdit()
        self.cbo_contract = QComboBox()
        self.cbo_contract.addItems(["Hộ gia đình", "Nhà máy"])

        self.txt_ma.setPlaceholderText("VD: HD001")
        self.txt_ten.setPlaceholderText("Nhập tên chủ hộ")
        self.txt_diachi.setPlaceholderText("Nhập địa chỉ")
        self.txt_sdt.setPlaceholderText("Nhập số điện thoại")

        form.addRow(lbl_ma, self.txt_ma)
        form.addRow(lbl_ten, self.txt_ten)
        form.addRow(lbl_diachi, self.txt_diachi)
        form.addRow(lbl_sdt, self.txt_sdt)
        form.addRow(lbl_contract, self.cbo_contract)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.btn_them = QPushButton("Thêm")
        self.btn_sua = QPushButton("Sửa")
        self.btn_xoa = QPushButton("Xóa")
        self.btn_lammoi = QPushButton("Làm mới")
        self.btn_lammoi.setProperty("variant", "secondary")

        for btn in [self.btn_them, self.btn_sua, self.btn_xoa, self.btn_lammoi]:
            btn.setCursor(Qt.PointingHandCursor)

        btn_row.addWidget(self.btn_them)
        btn_row.addWidget(self.btn_sua)
        btn_row.addWidget(self.btn_xoa)
        btn_row.addWidget(self.btn_lammoi)

        form_wrapper.addWidget(eyebrow)
        form_wrapper.addWidget(title)
        form_wrapper.addWidget(desc)
        form_wrapper.addLayout(form)
        form_wrapper.addLayout(btn_row)

        card_table = QFrame()
        card_table.setProperty("class", "card")

        table_wrapper = QVBoxLayout(card_table)
        table_wrapper.setContentsMargins(22, 20, 22, 20)
        table_wrapper.setSpacing(12)

        lbl_table = QLabel("Danh sách hộ dân")
        lbl_table.setProperty("class", "sectionTitle")

        table_desc = QLabel("Khu vực dữ liệu chính, có thể mở rộng thêm tìm kiếm, lọc và chọn dòng để sửa thông tin.")
        table_desc.setProperty("class", "sectionDesc")
        table_desc.setWordWrap(True)

        filter_row = QHBoxLayout()
        filter_row.setSpacing(10)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Tìm nhanh theo mã hộ, tên chủ hộ hoặc số điện thoại")

        btn_filter = QPushButton("Lọc nhanh")
        btn_filter.setProperty("variant", "secondary")

        filter_row.addWidget(self.search_box, 1)
        filter_row.addWidget(btn_filter)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Mã hộ", "Tên chủ hộ", "Địa chỉ", "Số điện thoại", "Loại hợp đồng"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setMinimumHeight(42)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setMinimumHeight(340)
        self.table.setFocusPolicy(Qt.NoFocus)

        self.table.itemSelectionChanged.connect(self.fill_form_from_selection)
        self.btn_them.clicked.connect(self.add_customer)
        self.btn_sua.clicked.connect(self.update_customer)
        self.btn_xoa.clicked.connect(self.delete_customer)
        self.btn_lammoi.clicked.connect(self.clear_form)
        btn_filter.clicked.connect(self.load_customers)

        table_wrapper.addWidget(lbl_table)
        table_wrapper.addWidget(table_desc)
        table_wrapper.addLayout(filter_row)
        table_wrapper.addWidget(self.table)

        body_row.addWidget(card_form, 4)
        body_row.addWidget(card_table, 6)

        root.addLayout(stats_row)
        root.addLayout(body_row, 1)

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

    def load_customers(self):
        if not self.context:
            return
        keyword = self.search_box.text().strip().casefold() if hasattr(self, "search_box") else ""
        self.customers = self.context.customer_service.list_customers()
        rows = [
            customer for customer in self.customers
            if not keyword
            or keyword in customer.customer_code.casefold()
            or keyword in customer.owner_name.casefold()
            or keyword in customer.phone_number.casefold()
        ]
        self.table.setRowCount(len(rows))
        for row, customer in enumerate(rows):
            values = [
                customer.customer_code,
                customer.owner_name,
                customer.address,
                customer.phone_number,
                customer.contract_type,
            ]
            for col, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignCenter)
                self.table.setItem(row, col, item)

    def refresh_data(self):
        self.load_customers()

    def fill_form_from_selection(self):
        row = self.table.currentRow()
        if row < 0:
            return
        self.txt_ma.setText(self.table.item(row, 0).text())
        self.txt_ten.setText(self.table.item(row, 1).text())
        self.txt_diachi.setText(self.table.item(row, 2).text())
        self.txt_sdt.setText(self.table.item(row, 3).text())
        self.cbo_contract.setCurrentText(self.table.item(row, 4).text())

    def add_customer(self):
        try:
            self.context.customer_service.create_customer(
                CustomerCreateDTO(
                    customer_code=self.txt_ma.text(),
                    owner_name=self.txt_ten.text(),
                    address=self.txt_diachi.text(),
                    phone_number=self.txt_sdt.text(),
                    contract_type=self.cbo_contract.currentText(),
                )
            )
            self.load_customers()
            self.clear_form()
        except Exception as exc:
            QMessageBox.warning(self, "Không thể thêm hộ", str(exc))

    def update_customer(self):
        try:
            self.context.customer_service.update_customer(
                CustomerUpdateDTO(
                    customer_code=self.txt_ma.text(),
                    owner_name=self.txt_ten.text(),
                    address=self.txt_diachi.text(),
                    phone_number=self.txt_sdt.text(),
                    contract_type=self.cbo_contract.currentText(),
                )
            )
            self.load_customers()
        except Exception as exc:
            QMessageBox.warning(self, "Không thể cập nhật hộ", str(exc))

    def delete_customer(self):
        try:
            self.context.customer_service.delete_customer(self.txt_ma.text())
            self.load_customers()
            self.clear_form()
        except Exception as exc:
            QMessageBox.warning(self, "Không thể xóa hộ", str(exc))

    def clear_form(self):
        self.txt_ma.clear()
        self.txt_ten.clear()
        self.txt_diachi.clear()
        self.txt_sdt.clear()
        self.cbo_contract.setCurrentIndex(0)
        self.load_customers()
