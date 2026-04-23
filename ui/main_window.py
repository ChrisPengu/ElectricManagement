from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QFrame,
)

from ui.hodan import HoDanForm
from ui.congto import CongToForm
from ui.hoadon import HoaDonForm
from ui.thanhtoan import ThanhToanForm
from ui.suco import SuCoForm
from ui.report import ReportForm
from ui.tariff import TariffForm


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.display_name = "Người dùng"
        self.role = "Nhân viên"
        self.menu_buttons = []
        self.page_meta = []
        self.build_ui()

    def build_ui(self):
        self.setStyleSheet(
            """
            QWidget {
                font-family: "Segoe UI";
                background-color: #eef4fb;
            }

            QFrame#sidebar {
                background-color: #123c67;
                border-radius: 30px;
            }

            QLabel#brand {
                color: white;
                font-size: 24px;
                font-weight: 700;
                background: transparent;
            }

            QLabel#brandSub {
                color: #b8d1ea;
                font-size: 12px;
                background: transparent;
            }

            QFrame#sessionCard {
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 18px;
            }

            QLabel#userInfo {
                color: white;
                font-size: 14px;
                font-weight: 700;
                background: transparent;
            }

            QLabel#userSubInfo {
                color: #b9d5ef;
                font-size: 12px;
                background: transparent;
            }

            QLabel#sidebarHint {
                color: #9fc1e3;
                font-size: 12px;
                line-height: 1.5;
                background: transparent;
            }

            QPushButton.menuButton {
                background-color: transparent;
                color: #e8f1fa;
                text-align: left;
                padding: 14px 16px;
                border-radius: 14px;
                font-size: 13px;
                font-weight: 600;
                border: none;
            }

            QPushButton.menuButton:hover {
                background-color: rgba(255, 255, 255, 0.12);
            }

            QPushButton.menuButtonActive {
                background-color: white;
                color: #123c67;
                text-align: left;
                padding: 14px 16px;
                border-radius: 14px;
                font-size: 13px;
                font-weight: 700;
                border: none;
            }

            QPushButton#logoutButton {
                background-color: #f16464;
                color: white;
                border: none;
                border-radius: 14px;
                padding: 12px 16px;
                font-size: 13px;
                font-weight: 700;
            }

            QPushButton#logoutButton:hover {
                background-color: #d95555;
            }

            QLabel#eyebrow {
                color: #4d7caa;
                font-size: 11px;
                font-weight: 700;
                background: transparent;
            }

            QLabel#headerTitle {
                font-size: 30px;
                font-weight: 700;
                color: #163b63;
                background: transparent;
            }

            QLabel#headerSub {
                font-size: 14px;
                color: #6f8295;
                background: transparent;
            }

            QLabel#headerBadge {
                color: #1d5b8f;
                background: #edf6ff;
                border: 1px solid #d1e5f7;
                border-radius: 14px;
                padding: 8px 12px;
                font-size: 12px;
                font-weight: 700;
            }

            QFrame#topCard {
                background-color: white;
                border-radius: 22px;
                border: 1px solid #d8e5f2;
            }

            QFrame#miniStat {
                background: #f6fbff;
                border-radius: 18px;
                border: 1px solid #dce8f4;
            }

            QLabel#helloText {
                font-size: 18px;
                font-weight: 700;
                color: #173b63;
                background: transparent;
            }

            QLabel#roleText {
                font-size: 13px;
                color: #70869e;
                background: transparent;
            }

            QLabel#statLabel {
                font-size: 12px;
                color: #6d849b;
                background: transparent;
            }

            QLabel#statValue {
                font-size: 20px;
                font-weight: 700;
                color: #163b63;
                background: transparent;
            }

            QFrame#contentCard {
                background-color: white;
                border-radius: 24px;
                border: 1px solid #d8e5f2;
            }
        """
        )

        root = QHBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(18)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(300)

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(22, 22, 22, 22)
        sidebar_layout.setSpacing(14)

        brand = QLabel("Electric Management")
        brand.setObjectName("brand")

        brand_sub = QLabel("Điều phối dịch vụ điện dân cư và sản xuất trên một giao diện thống nhất.")
        brand_sub.setObjectName("brandSub")
        brand_sub.setWordWrap(True)

        session_card = QFrame()
        session_card.setObjectName("sessionCard")
        session_layout = QVBoxLayout(session_card)
        session_layout.setContentsMargins(16, 16, 16, 16)
        session_layout.setSpacing(6)

        self.user_info = QLabel("Người dùng")
        self.user_info.setObjectName("userInfo")

        self.user_sub_info = QLabel("Vai trò: Nhân viên")
        self.user_sub_info.setObjectName("userSubInfo")

        session_hint = QLabel("Màn hình mới đã bổ sung phân hệ biểu giá điện và cấu hình loại hợp đồng.")
        session_hint.setObjectName("sidebarHint")
        session_hint.setWordWrap(True)

        session_layout.addWidget(self.user_info)
        session_layout.addWidget(self.user_sub_info)
        session_layout.addSpacing(6)
        session_layout.addWidget(session_hint)

        sidebar_layout.addWidget(brand)
        sidebar_layout.addWidget(brand_sub)
        sidebar_layout.addWidget(session_card)
        sidebar_layout.addSpacing(6)

        self.stack = QStackedWidget()
        self.hodan = HoDanForm()
        self.congto = CongToForm()
        self.hoadon = HoaDonForm()
        self.thanhtoan = ThanhToanForm()
        self.suco = SuCoForm()
        self.report = ReportForm()
        self.tariff = TariffForm()

        self.page_meta = [
            {
                "title": "Quản lý hộ dân",
                "subtitle": "Theo dõi hồ sơ hộ sử dụng điện, tìm kiếm nhanh và chuẩn bị dữ liệu cho các phân hệ liên quan.",
                "widget": self.hodan,
            },
            {
                "title": "Quản lý công tơ",
                "subtitle": "Tối ưu thao tác ghi chỉ số mới cho từng kỳ, không nhập lại chỉ số cũ khi dữ liệu sẽ do database cung cấp.",
                "widget": self.congto,
            },
            {
                "title": "Quản lý hóa đơn",
                "subtitle": "Kiểm soát kỳ hóa đơn, trạng thái thanh toán và các thao tác xem chi tiết hoặc in chứng từ.",
                "widget": self.hoadon,
            },
            {
                "title": "Quản lý thanh toán",
                "subtitle": "Xác nhận thanh toán nhanh, theo dõi trạng thái hóa đơn và chuẩn bị biên lai cho khách hàng.",
                "widget": self.thanhtoan,
            },
            {
                "title": "Quản lý sự cố",
                "subtitle": "Ghi nhận yêu cầu kỹ thuật, phân loại sự cố và giám sát tiến độ xử lý theo từng hộ dân.",
                "widget": self.suco,
            },
            {
                "title": "Báo cáo - thống kê",
                "subtitle": "Xem nhanh tổng quan doanh thu, hóa đơn và hiệu quả vận hành trong từng giai đoạn.",
                "widget": self.report,
            },
            {
                "title": "Biểu giá & hợp đồng",
                "subtitle": "Thiết lập công thức tính tiền điện, cấu hình phụ phí và phân loại hợp đồng hộ gia đình hoặc nhà máy.",
                "widget": self.tariff,
            },
        ]

        for meta in self.page_meta:
            self.stack.addWidget(meta["widget"])
            button = QPushButton(meta["title"])
            button.setCursor(Qt.PointingHandCursor)
            button.setProperty("class", "menuButton")
            button.setStyleSheet("")
            button.clicked.connect(
                lambda _checked=False, m=meta, b=button: self.switch_page(m["widget"], m["title"], m["subtitle"], b)
            )
            self.menu_buttons.append(button)
            sidebar_layout.addWidget(button)

        sidebar_layout.addStretch()

        self.btn_logout = QPushButton("Đăng xuất")
        self.btn_logout.setObjectName("logoutButton")
        self.btn_logout.setCursor(Qt.PointingHandCursor)
        sidebar_layout.addWidget(self.btn_logout)

        right_layout = QVBoxLayout()
        right_layout.setSpacing(16)

        self.header_eyebrow = QLabel("TRUNG TÂM ĐIỀU HÀNH")
        self.header_eyebrow.setObjectName("eyebrow")

        title_row = QHBoxLayout()
        title_row.setSpacing(12)

        title_block = QVBoxLayout()
        title_block.setSpacing(5)

        self.header_title = QLabel("Quản lý hộ dân")
        self.header_title.setObjectName("headerTitle")

        self.header_sub = QLabel("Theo dõi hồ sơ hộ sử dụng điện, tìm kiếm nhanh và chuẩn bị dữ liệu cho các phân hệ liên quan.")
        self.header_sub.setObjectName("headerSub")
        self.header_sub.setWordWrap(True)

        title_block.addWidget(self.header_title)
        title_block.addWidget(self.header_sub)

        self.header_badge = QLabel("Phiên giao diện 2.0")
        self.header_badge.setObjectName("headerBadge")
        self.header_badge.setAlignment(Qt.AlignCenter)

        title_row.addLayout(title_block, 1)
        title_row.addWidget(self.header_badge, 0, Qt.AlignTop)

        top_card = QFrame()
        top_card.setObjectName("topCard")
        top_card_layout = QHBoxLayout(top_card)
        top_card_layout.setContentsMargins(20, 18, 20, 18)
        top_card_layout.setSpacing(14)

        left_info = QVBoxLayout()
        left_info.setSpacing(4)

        self.hello_text = QLabel("Xin chào, Quản trị viên")
        self.hello_text.setObjectName("helloText")

        self.role_text = QLabel("Vai trò: Admin")
        self.role_text.setObjectName("roleText")

        left_info.addWidget(self.hello_text)
        left_info.addWidget(self.role_text)
        left_info.addStretch()

        stat_one = self.build_stat_card("Phân hệ đang mở", "07")
        stat_two = self.build_stat_card("Loại hợp đồng", "02")
        stat_three = self.build_stat_card("Trạng thái app", "Demo")

        top_card_layout.addLayout(left_info, 2)
        top_card_layout.addWidget(stat_one, 1)
        top_card_layout.addWidget(stat_two, 1)
        top_card_layout.addWidget(stat_three, 1)

        content_card = QFrame()
        content_card.setObjectName("contentCard")
        content_card_layout = QVBoxLayout(content_card)
        content_card_layout.setContentsMargins(14, 14, 14, 14)
        content_card_layout.addWidget(self.stack)

        right_layout.addWidget(self.header_eyebrow)
        right_layout.addLayout(title_row)
        right_layout.addWidget(top_card)
        right_layout.addWidget(content_card, 1)

        root.addWidget(sidebar)
        root.addLayout(right_layout, 1)

        first_meta = self.page_meta[0]
        self.switch_page(first_meta["widget"], first_meta["title"], first_meta["subtitle"], self.menu_buttons[0])

    def build_stat_card(self, label_text, value_text):
        card = QFrame()
        card.setObjectName("miniStat")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(2)

        label = QLabel(label_text)
        label.setObjectName("statLabel")

        value = QLabel(value_text)
        value.setObjectName("statValue")

        layout.addWidget(label)
        layout.addWidget(value)

        return card

    def switch_page(self, widget, title, subtitle, active_button):
        self.stack.setCurrentWidget(widget)
        self.header_title.setText(title)
        self.header_sub.setText(subtitle)

        for btn in self.menu_buttons:
            if btn == active_button:
                btn.setProperty("class", "menuButtonActive")
            else:
                btn.setProperty("class", "menuButton")

            btn.style().unpolish(btn)
            btn.style().polish(btn)
            btn.update()

    def set_user_info(self, display_name, role):
        self.display_name = display_name
        self.role = role
        self.user_info.setText(display_name)
        self.user_sub_info.setText(f"Vai trò: {role}")
        self.hello_text.setText(f"Xin chào, {display_name}")
        self.role_text.setText(f"Vai trò: {role}")
