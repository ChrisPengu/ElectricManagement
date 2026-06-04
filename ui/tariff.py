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
    QAbstractItemView,
)

from app.dto.requests import TariffUpsertDTO
from app.models import ContractType, default_household_price_tiers
from ui.common_styles import PAGE_STYLE


class TariffForm(QWidget):
    def __init__(self, context=None):
        super().__init__()
        self.context = context
        self._loading_config = False
        self.price_tiers = default_household_price_tiers()
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

        title = QLabel("Thiết lập công thức và khung giá tiền điện")
        title.setProperty("class", "sectionTitle")

        desc = QLabel(
            "Admin có thể cập nhật phí cố định, VAT, đơn giá nhà máy và các bậc giá hộ gia đình. "
            "Hóa đơn tạo mới sẽ dùng cấu hình đang có trong database."
        )
        desc.setProperty("class", "sectionDesc")
        desc.setWordWrap(True)

        hint_row = QHBoxLayout()
        hint_row.setSpacing(10)
        for text in ["Lưu trực tiếp vào database", "Sửa bảng bậc giá", "Hóa đơn mới áp dụng cấu hình mới"]:
            pill = QLabel(text)
            pill.setProperty("class", "infoPill")
            hint_row.addWidget(pill)
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

        config_desc = QLabel("Chọn nhóm hợp đồng và điều chỉnh tham số tính tiền điện.")
        config_desc.setProperty("class", "sectionDesc")
        config_desc.setWordWrap(True)

        form = QFormLayout()
        form.setHorizontalSpacing(18)
        form.setVerticalSpacing(12)
        form.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.cbo_contract = QComboBox()
        self.cbo_contract.addItem("Hộ gia đình", ContractType.HOUSEHOLD)
        self.cbo_contract.addItem("Nhà máy", ContractType.FACTORY)
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

        form.addRow(self.build_field_label("Loại hợp đồng"), self.cbo_contract)
        form.addRow(self.build_field_label("Phí cố định / kỳ"), self.spin_fixed_fee)
        form.addRow(self.build_field_label("VAT"), self.spin_vat)
        form.addRow(self.build_field_label("Hệ số giờ cao điểm"), self.spin_peak)
        form.addRow(self.build_field_label("Đơn giá nhà máy"), self.spin_factory_rate)

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

        formula_title = QLabel("Công thức và ghi chú áp dụng")
        formula_title.setProperty("class", "sectionTitle")

        formula_desc = QLabel(
            "Preview tự cập nhật theo tham số đang chọn; ô ghi chú bên dưới được lưu riêng cho từng loại hợp đồng."
        )
        formula_desc.setProperty("class", "sectionDesc")
        formula_desc.setWordWrap(True)

        self.lbl_formula_preview = QLabel()
        self.lbl_formula_preview.setProperty("class", "valueBox")
        self.lbl_formula_preview.setWordWrap(True)

        self.txt_formula = QPlainTextEdit()
        self.txt_formula.setReadOnly(False)
        self.txt_formula.setPlaceholderText("Ghi chú công thức lưu kèm cấu hình biểu giá")
        self.txt_formula.setMinimumHeight(120)

        formula_layout.addWidget(formula_title)
        formula_layout.addWidget(formula_desc)
        formula_layout.addWidget(self.lbl_formula_preview)
        formula_layout.addWidget(self.txt_formula)

        table_card = QFrame()
        table_card.setProperty("class", "card")
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(22, 20, 22, 20)
        table_layout.setSpacing(12)

        table_title = QLabel("Khung giá")
        table_title.setProperty("class", "sectionTitle")

        self.lbl_table_desc = QLabel()
        self.lbl_table_desc.setProperty("class", "sectionDesc")
        self.lbl_table_desc.setWordWrap(True)

        tier_btn_row = QHBoxLayout()
        tier_btn_row.setSpacing(10)
        self.btn_add_tier = QPushButton("Thêm bậc giá")
        self.btn_remove_tier = QPushButton("Xóa bậc đang chọn")
        self.btn_reset_tiers = QPushButton("Khôi phục mặc định")
        for button in [self.btn_add_tier, self.btn_remove_tier, self.btn_reset_tiers]:
            button.setProperty("variant", "secondary")
        self.btn_add_tier.clicked.connect(self.add_price_tier)
        self.btn_remove_tier.clicked.connect(self.remove_selected_price_tier)
        self.btn_reset_tiers.clicked.connect(self.reset_price_tiers)
        tier_btn_row.addWidget(self.btn_add_tier)
        tier_btn_row.addWidget(self.btn_remove_tier)
        tier_btn_row.addWidget(self.btn_reset_tiers)
        tier_btn_row.addStretch()

        self.table_tariff = QTableWidget(0, 0)
        self.table_tariff.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_tariff.verticalHeader().setVisible(False)
        self.table_tariff.setAlternatingRowColors(True)
        self.table_tariff.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_tariff.setMinimumHeight(260)

        table_layout.addWidget(table_title)
        table_layout.addWidget(self.lbl_table_desc)
        table_layout.addLayout(tier_btn_row)
        table_layout.addWidget(self.table_tariff)

        preview_column.addWidget(formula_card)
        preview_column.addWidget(table_card, 1)

        body_row.addWidget(config_card, 4)
        body_row.addLayout(preview_column, 5)

        root.addWidget(intro_card)
        root.addLayout(body_row, 1)

    def build_field_label(self, text):
        label = QLabel(text)
        label.setProperty("class", "fieldLabel")
        return label

    def current_contract_type(self):
        return self.cbo_contract.currentData() or ContractType.HOUSEHOLD

    def is_household_contract(self):
        return self.current_contract_type() == ContractType.HOUSEHOLD

    def default_formula_note(self, contract_type=None):
        contract_type = contract_type or self.current_contract_type()
        if contract_type == ContractType.HOUSEHOLD:
            return (
                "Tiền điện hộ gia đình = Phí cố định + Tổng(kWh từng bậc x đơn giá bậc) + VAT. "
                "Các bậc giá có thể chỉnh trực tiếp trong bảng khung giá."
            )
        return (
            "Tiền điện nhà máy = Phí cố định + (kWh x đơn giá cơ sở x hệ số giờ cao điểm) + VAT. "
            "Điều chỉnh đơn giá cơ sở và hệ số cao điểm để áp dụng cho nhóm sản xuất."
        )

    def refresh_contract_view(self, *_, sync_table=True):
        if self._loading_config:
            return
        if sync_table and self.is_household_contract() and self.table_tariff.columnCount() == 3:
            self.cache_price_tiers_from_table()

        fixed_fee = self.spin_fixed_fee.value()
        vat = self.spin_vat.value()
        peak_coef = self.spin_peak.value()
        factory_rate = self.spin_factory_rate.value()

        if self.is_household_contract():
            self.lbl_contract_badge.setText("Hợp đồng dân cư")
            self.lbl_contract_summary.setText(
                "Áp dụng tính lũy tiến theo bậc kWh. Có thể sửa trực tiếp các khoảng và đơn giá trong bảng."
            )
            self.lbl_table_desc.setText(
                "Nhập số nguyên cho các cột. Để trống cột Đến kWh ở bậc cuối để áp dụng cho phần vượt mức."
            )
            self.lbl_formula_preview.setText(
                "Tiền điện hộ gia đình = Phí cố định + Tổng(kWh từng bậc x đơn giá bậc) + VAT\n\n"
                f"Phí cố định hiện tại: {fixed_fee:,} VND/kỳ\n"
                f"VAT hiện tại: {vat:.1f}%\n"
            )
            headers = ["Từ kWh", "Đến kWh", "Đơn giá (VND/kWh)"]
            rows = self.price_tier_rows()
            editable = True
        else:
            self.lbl_contract_badge.setText("Hợp đồng nhà máy")
            self.lbl_contract_summary.setText(
                "Áp dụng đơn giá cơ sở và hệ số giờ cao điểm cho nhóm sản xuất, nhà máy hoặc đơn vị tiêu thụ lớn."
            )
            self.lbl_table_desc.setText("Bảng bên dưới là giá trị xem trước theo đơn giá cơ sở và hệ số đang chọn.")
            self.lbl_formula_preview.setText(
                "Tiền điện nhà máy = Phí cố định + (kWh x đơn giá cơ sở x hệ số giờ cao điểm) + VAT\n\n"
                f"Phí cố định hiện tại: {fixed_fee:,} VND/kỳ\n"
                f"VAT hiện tại: {vat:.1f}%\n"
                f"Đơn giá cơ sở hiện tại: {factory_rate:,} VND/kWh\n"
                f"Hệ số giờ cao điểm: x{peak_coef:.2f}\n"
            )
            headers = ["Khung giờ", "Hệ số", "Đơn giá xem trước (VND/kWh)"]
            rows = [
                ["Thấp điểm", "0.75", f"{int(factory_rate * 0.75):,}"],
                ["Bình thường", "1.00", f"{factory_rate:,}"],
                ["Cao điểm", f"{peak_coef:.2f}", f"{int(factory_rate * peak_coef):,}"],
            ]
            editable = False

        self.populate_tariff_table(headers, rows, editable)
        for button in [self.btn_add_tier, self.btn_remove_tier, self.btn_reset_tiers]:
            button.setVisible(editable)

    def populate_tariff_table(self, headers, rows, editable):
        self.table_tariff.blockSignals(True)
        self.table_tariff.setColumnCount(len(headers))
        self.table_tariff.setHorizontalHeaderLabels(headers)
        self.table_tariff.setRowCount(len(rows))
        if editable:
            triggers = (
                QAbstractItemView.DoubleClicked
                | QAbstractItemView.SelectedClicked
                | QAbstractItemView.EditKeyPressed
            )
        else:
            triggers = QAbstractItemView.NoEditTriggers
        self.table_tariff.setEditTriggers(triggers)

        for row_index, row_data in enumerate(rows):
            for col_index, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                if not editable:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.table_tariff.setItem(row_index, col_index, item)
        self.table_tariff.blockSignals(False)

    def price_tier_rows(self):
        return [
            [
                str(tier["from_kwh"]),
                "" if tier["to_kwh"] is None else str(tier["to_kwh"]),
                str(tier["rate"]),
            ]
            for tier in self.price_tiers
        ]

    def collect_price_tiers(self, show_errors=True):
        try:
            tiers = []
            expected_from = None
            for row in range(self.table_tariff.rowCount()):
                from_text = self.cell_text(row, 0)
                to_text = self.cell_text(row, 1)
                rate_text = self.cell_text(row, 2)

                if not from_text or not rate_text:
                    raise ValueError("Cột Từ kWh và Đơn giá không được để trống.")

                from_kwh = int(from_text)
                to_kwh = None if to_text == "" else int(to_text)
                rate = int(rate_text.replace(".", "").replace(",", ""))
                lower_bound = max(from_kwh, 1)

                if row == 0 and from_kwh not in (0, 1):
                    raise ValueError("Bậc đầu tiên phải bắt đầu từ 0 hoặc 1 kWh.")
                if expected_from is not None and from_kwh != expected_from:
                    raise ValueError("Các bậc giá phải liên tiếp nhau.")
                if rate <= 0:
                    raise ValueError("Đơn giá phải lớn hơn 0.")
                if to_kwh is None:
                    if row != self.table_tariff.rowCount() - 1:
                        raise ValueError("Chỉ bậc cuối cùng được để trống cột Đến kWh.")
                else:
                    if to_kwh < lower_bound:
                        raise ValueError("Cột Đến kWh phải lớn hơn hoặc bằng cột Từ kWh.")
                    expected_from = to_kwh + 1

                tiers.append({"from_kwh": from_kwh, "to_kwh": to_kwh, "rate": rate})

            if not tiers:
                raise ValueError("Cần có ít nhất một bậc giá.")
            if tiers[-1]["to_kwh"] is not None:
                raise ValueError("Bậc cuối cùng cần để trống cột Đến kWh.")
            return tiers
        except (AttributeError, TypeError, ValueError) as exc:
            if show_errors:
                raise ValueError(str(exc)) from exc
            return None

    def cell_text(self, row, column):
        item = self.table_tariff.item(row, column)
        return item.text().strip() if item else ""

    def cache_price_tiers_from_table(self):
        tiers = self.collect_price_tiers(show_errors=False)
        if tiers:
            self.price_tiers = tiers

    def add_price_tier(self):
        self.cache_price_tiers_from_table()
        tiers = [dict(tier) for tier in (self.price_tiers or default_household_price_tiers())]
        if tiers[-1]["to_kwh"] is None:
            previous_to = tiers[-2]["to_kwh"] if len(tiers) > 1 else 0
            previous_to = int(previous_to or 0)
            new_from = previous_to + 1
            new_to = new_from + 49
            new_rate = int(tiers[-1]["rate"])
            tiers[-1]["from_kwh"] = new_to + 1
            tiers.insert(-1, {"from_kwh": new_from, "to_kwh": new_to, "rate": new_rate})
        else:
            last_to = int(tiers[-1]["to_kwh"])
            tiers.append({"from_kwh": last_to + 1, "to_kwh": None, "rate": int(tiers[-1]["rate"])})
        self.price_tiers = tiers
        self.refresh_contract_view(sync_table=False)

    def remove_selected_price_tier(self):
        self.cache_price_tiers_from_table()
        if len(self.price_tiers) <= 1:
            QMessageBox.warning(self, "Không thể xóa", "Cần giữ lại ít nhất một bậc giá.")
            return
        row = self.table_tariff.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Chưa chọn bậc giá", "Vui lòng chọn một dòng trong bảng.")
            return
        tiers = [dict(tier) for tier in self.price_tiers]
        del tiers[row]
        self.price_tiers = self.normalize_tier_boundaries(tiers)
        self.refresh_contract_view(sync_table=False)

    def normalize_tier_boundaries(self, tiers):
        normalized = []
        next_from = 0 if tiers[0].get("from_kwh") in (0, None) else 1
        for index, tier in enumerate(tiers):
            old_from = max(int(tier.get("from_kwh", 0)), 1)
            old_to = tier.get("to_kwh")
            normalized_tier = {"from_kwh": next_from, "to_kwh": None, "rate": int(tier["rate"])}
            if index != len(tiers) - 1 and old_to is not None:
                width = max(int(old_to) - old_from, 0)
                new_lower = max(next_from, 1)
                normalized_tier["to_kwh"] = new_lower + width
                next_from = normalized_tier["to_kwh"] + 1
            normalized.append(normalized_tier)
        return normalized

    def reset_price_tiers(self):
        self.price_tiers = default_household_price_tiers()
        self.refresh_contract_view(sync_table=False)

    def load_contract_config(self, *_):
        if not self.context:
            self.txt_formula.setPlainText(self.default_formula_note())
            self.refresh_contract_view(sync_table=False)
            return

        contract_type = self.current_contract_type()
        try:
            config = self.context.tariff_service.get_config(contract_type)
        except Exception:
            config = None

        if config:
            self._loading_config = True
            self.spin_fixed_fee.setValue(config.fixed_fee)
            self.spin_vat.setValue(config.vat_percent)
            self.spin_peak.setValue(config.peak_multiplier)
            self.spin_factory_rate.setValue(config.base_rate)
            if contract_type == ContractType.HOUSEHOLD:
                self.price_tiers = config.price_tiers or default_household_price_tiers()
            self.txt_formula.setPlainText(config.formula_note or self.default_formula_note(contract_type))
            self._loading_config = False
        elif contract_type == ContractType.HOUSEHOLD:
            self.price_tiers = default_household_price_tiers()
            self.txt_formula.setPlainText(self.default_formula_note(contract_type))
        else:
            self.txt_formula.setPlainText(self.default_formula_note(contract_type))

        self.refresh_contract_view(sync_table=False)

    def refresh_data(self):
        self.load_contract_config()

    def save_config(self):
        if not self.context:
            return
        contract_type = self.current_contract_type()
        try:
            price_tiers = self.collect_price_tiers() if contract_type == ContractType.HOUSEHOLD else []
            self.context.tariff_service.save_config(
                TariffUpsertDTO(
                    contract_type=contract_type.value,
                    fixed_fee=self.spin_fixed_fee.value(),
                    vat_percent=self.spin_vat.value(),
                    peak_multiplier=self.spin_peak.value(),
                    base_rate=self.spin_factory_rate.value(),
                    formula_note=self.txt_formula.toPlainText(),
                    price_tiers=price_tiers,
                )
            )
            QMessageBox.information(self, "Đã lưu", "Cấu hình biểu giá đã được cập nhật.")
            self.load_contract_config()
        except Exception as exc:
            QMessageBox.warning(self, "Không thể lưu biểu giá", str(exc))
