from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QFrame,
    QComboBox,
    QSpinBox,
    QDoubleSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QPlainTextEdit,
    QPushButton,
    QMessageBox,
)

from app.dto.requests import TariffUpsertDTO
from app.models import ContractType
from ui.common_styles import PAGE_STYLE


class TariffForm(QWidget):
    def __init__(self, context=None):
        super().__init__()
        self.context = context
        self._loading_config = False
        self.build_ui()
        self.load_contract_config()

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

        eyebrow = QLabel("BIỂU GIÁ ĐIỆN")
        eyebrow.setProperty("class", "sectionEyebrow")

        title = QLabel("Thiết lập công thức và loại hợp đồng cung cấp điện")
        title.setProperty("class", "sectionTitle")

        desc = QLabel(
            "Phân hệ này dùng để cấu hình nhóm hợp đồng, phụ phí cơ bản, VAT và cách diễn giải công thức tính tiền điện. "
            "Hiện tại màn hình phục vụ demo giao diện, sau này có thể gắn trực tiếp với database để lưu biểu giá."
        )
        desc.setProperty("class", "sectionDesc")
        desc.setWordWrap(True)

        hint_row = QHBoxLayout()
        hint_row.setSpacing(10)

        pill_one = QLabel("Hỗ trợ 2 loại hợp đồng")
        pill_one.setProperty("class", "infoPill")

        pill_two = QLabel("Có xem trước công thức")
        pill_two.setProperty("class", "infoPill")

        pill_three = QLabel("Sẵn sàng tích hợp database")
        pill_three.setProperty("class", "infoPill")

        hint_row.addWidget(pill_one)
        hint_row.addWidget(pill_two)
        hint_row.addWidget(pill_three)
        hint_row.addStretch()

        intro_layout.addWidget(eyebrow)
        intro_layout.addWidget(title)
        intro_layout.addWidget(desc)
        intro_layout.addLayout(hint_row)

        body_row = QHBoxLayout()
        body_row.setSpacing(18)

        config_card = QFrame()
        config_card.setProperty("class", "card")
        config_layout = QVBoxLayout(config_card)
        config_layout.setContentsMargins(22, 20, 22, 20)
        config_layout.setSpacing(16)

        config_title = QLabel("Cấu hình hợp đồng")
        config_title.setProperty("class", "sectionTitle")

        config_desc = QLabel("Chọn nhóm hợp đồng và tham số nền cho công thức tính tiền điện.")
        config_desc.setProperty("class", "sectionDesc")
        config_desc.setWordWrap(True)

        form = QFormLayout()
        form.setHorizontalSpacing(18)
        form.setVerticalSpacing(12)
        form.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        lbl_contract = QLabel("Loại hợp đồng")
        lbl_contract.setProperty("class", "fieldLabel")

        lbl_fixed = QLabel("Phí cố định / kỳ")
        lbl_fixed.setProperty("class", "fieldLabel")

        lbl_vat = QLabel("VAT")
        lbl_vat.setProperty("class", "fieldLabel")

        lbl_peak = QLabel("Hệ số giờ cao điểm")
        lbl_peak.setProperty("class", "fieldLabel")

        lbl_note = QLabel("Đơn giá nhà máy")
        lbl_note.setProperty("class", "fieldLabel")

        self.cbo_contract = QComboBox()
        self.cbo_contract.addItems(["Hộ gia đình", "Nhà máy"])
        self.cbo_contract.currentTextChanged.connect(self.load_contract_config)

        self.spin_fixed_fee = QSpinBox()
        self.spin_fixed_fee.setRange(0, 5000000)
        self.spin_fixed_fee.setSingleStep(5000)
        self.spin_fixed_fee.setValue(35000)
        self.spin_fixed_fee.valueChanged.connect(self.refresh_contract_view)

        self.spin_vat = QDoubleSpinBox()
        self.spin_vat.setRange(0, 20)
        self.spin_vat.setDecimals(1)
        self.spin_vat.setSingleStep(0.5)
        self.spin_vat.setSuffix(" %")
        self.spin_vat.setValue(8.0)
        self.spin_vat.valueChanged.connect(self.refresh_contract_view)

        self.spin_peak = QDoubleSpinBox()
        self.spin_peak.setRange(1.0, 5.0)
        self.spin_peak.setDecimals(2)
        self.spin_peak.setSingleStep(0.1)
        self.spin_peak.setValue(1.35)
        self.spin_peak.valueChanged.connect(self.refresh_contract_view)

        self.spin_factory_rate = QSpinBox()
        self.spin_factory_rate.setRange(0, 100000)
        self.spin_factory_rate.setSingleStep(50)
        self.spin_factory_rate.setValue(2450)
        self.spin_factory_rate.valueChanged.connect(self.refresh_contract_view)

        form.addRow(lbl_contract, self.cbo_contract)
        form.addRow(lbl_fixed, self.spin_fixed_fee)
        form.addRow(lbl_vat, self.spin_vat)
        form.addRow(lbl_peak, self.spin_peak)
        form.addRow(lbl_note, self.spin_factory_rate)

        summary_card = QFrame()
        summary_card.setProperty("class", "softCard")
        summary_layout = QVBoxLayout(summary_card)
        summary_layout.setContentsMargins(16, 16, 16, 16)
        summary_layout.setSpacing(6)

        self.lbl_contract_badge = QLabel()
        self.lbl_contract_badge.setProperty("class", "infoPill")

        self.lbl_contract_summary = QLabel()
        self.lbl_contract_summary.setProperty("class", "sectionDesc")
        self.lbl_contract_summary.setWordWrap(True)

        summary_layout.addWidget(self.lbl_contract_badge)
        summary_layout.addWidget(self.lbl_contract_summary)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.btn_apply = QPushButton("Áp dụng cấu hình")
        self.btn_preview = QPushButton("Làm mới xem trước")
        self.btn_preview.setProperty("variant", "secondary")
        self.btn_preview.clicked.connect(self.refresh_contract_view)
        self.btn_apply.clicked.connect(self.save_config)

        btn_row.addWidget(self.btn_apply)
        btn_row.addWidget(self.btn_preview)
        btn_row.addStretch()

        config_layout.addWidget(config_title)
        config_layout.addWidget(config_desc)
        config_layout.addLayout(form)
        config_layout.addWidget(summary_card)
        config_layout.addLayout(btn_row)

        preview_column = QVBoxLayout()
        preview_column.setSpacing(18)

        formula_card = QFrame()
        formula_card.setProperty("class", "card")
        formula_layout = QVBoxLayout(formula_card)
        formula_layout.setContentsMargins(22, 20, 22, 20)
        formula_layout.setSpacing(12)

        formula_title = QLabel("Xem trước công thức")
        formula_title.setProperty("class", "sectionTitle")

        formula_desc = QLabel("Công thức sẽ thay đổi theo loại hợp đồng và tham số bạn đang chọn.")
        formula_desc.setProperty("class", "sectionDesc")
        formula_desc.setWordWrap(True)

        self.txt_formula = QPlainTextEdit()
        self.txt_formula.setReadOnly(True)
        self.txt_formula.setMinimumHeight(150)

        formula_layout.addWidget(formula_title)
        formula_layout.addWidget(formula_desc)
        formula_layout.addWidget(self.txt_formula)

        table_card = QFrame()
        table_card.setProperty("class", "card")
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(22, 20, 22, 20)
        table_layout.setSpacing(12)

        table_title = QLabel("Khung giá minh họa")
        table_title.setProperty("class", "sectionTitle")

        self.lbl_table_desc = QLabel()
        self.lbl_table_desc.setProperty("class", "sectionDesc")
        self.lbl_table_desc.setWordWrap(True)

        self.table_tariff = QTableWidget(0, 0)
        self.table_tariff.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_tariff.verticalHeader().setVisible(False)
        self.table_tariff.setAlternatingRowColors(True)
        self.table_tariff.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_tariff.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_tariff.setMinimumHeight(260)

        table_layout.addWidget(table_title)
        table_layout.addWidget(self.lbl_table_desc)
        table_layout.addWidget(self.table_tariff)

        preview_column.addWidget(formula_card)
        preview_column.addWidget(table_card, 1)

        body_row.addWidget(config_card, 4)
        body_row.addLayout(preview_column, 5)

        root.addWidget(intro_card)
        root.addLayout(body_row, 1)

    def refresh_contract_view(self):
        if self._loading_config:
            return
        contract_type = self.cbo_contract.currentText()
        fixed_fee = self.spin_fixed_fee.value()
        vat = self.spin_vat.value()
        peak_coef = self.spin_peak.value()
        factory_rate = self.spin_factory_rate.value()

        if contract_type == "Hộ gia đình":
            self.lbl_contract_badge.setText("Hợp đồng dân cư")
            self.lbl_contract_summary.setText(
                "Áp dụng cơ chế tính lũy tiến theo bậc tiêu thụ. Phù hợp với hộ dân và khu nhà ở, "
                "ưu tiên mô hình giá tăng theo sản lượng sử dụng."
            )
            self.lbl_table_desc.setText("Minh họa các bậc giá để Admin chuẩn hóa công thức cho nhóm hộ dân.")
            self.txt_formula.setPlainText(
                "Tiền điện hộ gia đình = Phí cố định + Tổng(kWh theo từng bậc x đơn giá bậc) + VAT\n\n"
                f"Phí cố định hiện tại: {fixed_fee:,} VNĐ/kỳ\n"
                f"VAT hiện tại: {vat:.1f}%\n\n"
                "Gợi ý triển khai nghiệp vụ sau này:\n"
                "- Đọc sản lượng tiêu thụ từ chênh lệch chỉ số công tơ.\n"
                "- Tự động chia sản lượng vào từng bậc.\n"
                "- Tính thuế và tổng tiền cuối kỳ."
            )
            headers = ["Từ kWh", "Đến kWh", "Đơn giá minh họa (VNĐ)"]
            rows = [
                ["0", "50", "1,806"],
                ["51", "100", "1,866"],
                ["101", "200", "2,167"],
                ["201", "300", "2,729"],
                ["301", "400", "3,050"],
                ["401", "Trở lên", "3,151"],
            ]
        else:
            self.lbl_contract_badge.setText("Hợp đồng nhà máy")
            self.lbl_contract_summary.setText(
                "Áp dụng biểu giá cho nhóm sản xuất, có thể tách đơn giá theo giờ cao điểm, bình thường và thấp điểm. "
                "Phù hợp với mô hình tiêu thụ lớn và hợp đồng doanh nghiệp."
            )
            self.lbl_table_desc.setText("Minh họa đơn giá theo khung thời gian cho hợp đồng nhà máy.")
            self.txt_formula.setPlainText(
                "Tiền điện nhà máy = Phí cố định + (kWh x đơn giá sản xuất theo khung giờ) + VAT\n\n"
                f"Phí cố định hiện tại: {fixed_fee:,} VNĐ/kỳ\n"
                f"VAT hiện tại: {vat:.1f}%\n"
                f"Đơn giá cơ sở hiện tại: {factory_rate:,} VNĐ/kWh\n"
                f"Hệ số giờ cao điểm: x{peak_coef:.2f}\n\n"
                "Gợi ý triển khai nghiệp vụ sau này:\n"
                "- Phân loại sản lượng theo ca hoặc khung giờ.\n"
                "- Nhân hệ số cho giờ cao điểm.\n"
                "- Tổng hợp về hóa đơn công nghiệp."
            )
            headers = ["Khung giờ", "Hệ số", "Đơn giá minh họa (VNĐ)"]
            rows = [
                ["Thấp điểm", "0.75", f"{int(factory_rate * 0.75):,}"],
                ["Bình thường", "1.00", f"{factory_rate:,}"],
                ["Cao điểm", f"{peak_coef:.2f}", f"{int(factory_rate * peak_coef):,}"],
            ]

        self.table_tariff.setColumnCount(len(headers))
        self.table_tariff.setHorizontalHeaderLabels(headers)
        self.table_tariff.setRowCount(len(rows))

        for row_index, row_data in enumerate(rows):
            for col_index, value in enumerate(row_data):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)
                self.table_tariff.setItem(row_index, col_index, item)

    def load_contract_config(self):
        if not self.context:
            self.refresh_contract_view()
            return
        contract_type = self.cbo_contract.currentText()
        try:
            config = self.context.tariff_service.get_config(ContractType(contract_type))
        except Exception:
            config = None
        if config:
            self._loading_config = True
            self.spin_fixed_fee.setValue(config.fixed_fee)
            self.spin_vat.setValue(config.vat_percent)
            self.spin_peak.setValue(config.peak_multiplier)
            self.spin_factory_rate.setValue(config.base_rate)
            self._loading_config = False
        self.refresh_contract_view()

    def save_config(self):
        if not self.context:
            return
        contract_type = self.cbo_contract.currentText()
        try:
            self.context.tariff_service.save_config(
                TariffUpsertDTO(
                    contract_type=contract_type,
                    fixed_fee=self.spin_fixed_fee.value(),
                    vat_percent=self.spin_vat.value(),
                    peak_multiplier=self.spin_peak.value(),
                    base_rate=self.spin_factory_rate.value(),
                    formula_note=self.txt_formula.toPlainText(),
                )
            )
            QMessageBox.information(self, "Đã lưu", "Cấu hình biểu giá đã được cập nhật.")
            self.load_contract_config()
        except Exception as exc:
            QMessageBox.warning(self, "Không thể lưu biểu giá", str(exc))
