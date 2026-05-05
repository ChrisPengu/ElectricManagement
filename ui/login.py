from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QSizePolicy,
)


class LoginForm(QWidget):
    def __init__(self):
        super().__init__()
        self.build_ui()

    def build_ui(self):
        self.setStyleSheet(
            """
            QWidget {
                font-family: "Segoe UI";
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #edf5ff,
                    stop:0.45 #f4f7fc,
                    stop:1 #e6eef8
                );
            }

            QFrame#heroPanel {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #123d68,
                    stop:1 #1f5f95
                );
                border-radius: 34px;
            }

            QFrame#highlightCard {
                background: rgba(255, 255, 255, 0.10);
                border-radius: 18px;
                border: 1px solid rgba(255, 255, 255, 0.12);
            }

            QLabel#heroTitle {
                color: white;
                font-size: 34px;
                font-weight: 700;
                background: transparent;
            }

            QLabel#heroDesc {
                color: #d3e6f8;
                font-size: 14px;
                line-height: 1.6;
                background: transparent;
            }

            QLabel.heroMetricValue {
                color: white;
                font-size: 24px;
                font-weight: 700;
                background: transparent;
            }

            QLabel.heroMetricLabel {
                color: #cfe0f2;
                font-size: 12px;
                background: transparent;
            }

            QFrame#featureCard {
                background: rgba(255, 255, 255, 0.12);
                border-radius: 18px;
                border: 1px solid rgba(255, 255, 255, 0.12);
            }

            QLabel.featureTitle {
                color: white;
                font-size: 14px;
                font-weight: 700;
                background: transparent;
            }

            QLabel.featureDesc {
                color: #d2e7f8;
                font-size: 12px;
                line-height: 1.5;
                background: transparent;
            }

            QFrame#loginCard {
                background: rgba(255, 255, 255, 0.98);
                border: 1px solid #d8e5f2;
                border-radius: 30px;
            }

            QLabel#cardEyebrow {
                color: #5a7da3;
                font-size: 11px;
                font-weight: 700;
                background: transparent;
            }

            QLabel#cardTitle {
                color: #183d6b;
                font-size: 30px;
                font-weight: 700;
                background: transparent;
            }

            QLabel#cardSubtitle {
                color: #6e8198;
                font-size: 13px;
                background: transparent;
            }

            QLabel.formLabel {
                color: #2d4464;
                font-size: 13px;
                font-weight: 700;
                background: transparent;
            }

            QLineEdit {
                background: #f9fbfe;
                border: 1px solid #d8e1ec;
                border-radius: 16px;
                padding: 14px 18px;
                font-size: 14px;
                color: #2d4464;
                min-height: 24px;
            }

            QLineEdit:focus {
                background: white;
                border: 1px solid #3b82f6;
            }

            QPushButton#loginButton {
                background-color: #183d6b;
                color: white;
                border: none;
                border-radius: 16px;
                padding: 15px 18px;
                font-size: 15px;
                font-weight: 700;
                min-height: 24px;
            }

            QPushButton#loginButton:hover {
                background-color: #113255;
            }

            QLabel#demoText {
                color: #667b95;
                font-size: 12px;
                background: transparent;
            }

            QLabel#loginHint {
                color: #23527f;
                background: #eef6ff;
                border: 1px solid #d4e6f6;
                border-radius: 14px;
                padding: 11px 14px;
                font-size: 12px;
                line-height: 1.5;
            }
        """
        )

        root = QHBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(28)

        hero_panel = QFrame()
        hero_panel.setObjectName("heroPanel")
        hero_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        hero_layout = QVBoxLayout(hero_panel)
        hero_layout.setContentsMargins(30, 28, 30, 28)
        hero_layout.setSpacing(18)

        title = QLabel("Quản lý dịch vụ cung cấp điện tại khu dân cư")
        title.setObjectName("heroTitle")
        title.setWordWrap(True)

        desc = QLabel(
            "Giao diện dành riêng cho Admin để quản lý hộ dùng điện, ghi chỉ số công tơ, "
            "lập hóa đơn, xác nhận thanh toán và theo dõi sự cố."
        )
        desc.setObjectName("heroDesc")
        desc.setWordWrap(True)

        metric_card = QFrame()
        metric_card.setObjectName("highlightCard")
        metric_layout = QHBoxLayout(metric_card)
        metric_layout.setContentsMargins(18, 16, 18, 16)
        metric_layout.setSpacing(18)

        metric_one = self.build_metric("07", "Phân hệ Admin")
        metric_two = self.build_metric("02", "Loại hợp đồng")

        metric_layout.addWidget(metric_one)
        metric_layout.addWidget(metric_two)

        feature_row = QHBoxLayout()
        feature_row.setSpacing(14)
        feature_row.addWidget(
            self.build_feature_card(
                "Quản lý tập trung",
                "Điều phối hồ sơ hộ dùng điện, công tơ, hóa đơn, thanh toán và sự cố trên một màn hình quản trị."
            )
        )
        feature_row.addWidget(
            self.build_feature_card(
                "Biểu giá linh hoạt",
                "Thiết lập công thức tính tiền riêng cho hợp đồng hộ gia đình và đơn vị sản xuất."
            )
        )

        hero_layout.addWidget(title)
        hero_layout.addWidget(desc)
        hero_layout.addWidget(metric_card)
        hero_layout.addLayout(feature_row)
        hero_layout.addStretch()

        card = QFrame()
        card.setObjectName("loginCard")
        card.setMinimumWidth(470)
        card.setMaximumWidth(540)
        card.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(42, 42, 42, 42)
        card_layout.setSpacing(0)

        eyebrow = QLabel("CỔNG ADMIN")
        eyebrow.setObjectName("cardEyebrow")
        eyebrow.setAlignment(Qt.AlignCenter)

        card_title = QLabel("Đăng nhập quản trị")
        card_title.setObjectName("cardTitle")
        card_title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel("Chỉ tài khoản Admin được truy cập các phân hệ quản lý của phần mềm.")
        subtitle.setObjectName("cardSubtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setWordWrap(True)

        card_layout.addWidget(eyebrow)
        card_layout.addSpacing(10)
        card_layout.addWidget(card_title)
        card_layout.addSpacing(10)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(30)

        hint = QLabel("Tài khoản Admin demo: admin / admin123")
        hint.setObjectName("loginHint")
        hint.setWordWrap(True)
        card_layout.addWidget(hint)
        card_layout.addSpacing(28)

        lbl_user = QLabel("Tên đăng nhập")
        lbl_user.setProperty("class", "formLabel")
        card_layout.addWidget(lbl_user)
        card_layout.addSpacing(10)

        self.input_username = QLineEdit()
        self.input_username.setPlaceholderText("Nhập tên đăng nhập")
        card_layout.addWidget(self.input_username)

        card_layout.addSpacing(24)

        lbl_pass = QLabel("Mật khẩu")
        lbl_pass.setProperty("class", "formLabel")
        card_layout.addWidget(lbl_pass)
        card_layout.addSpacing(10)

        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("Nhập mật khẩu")
        self.input_password.setEchoMode(QLineEdit.Password)
        card_layout.addWidget(self.input_password)

        card_layout.addSpacing(24)

        self.btn_login = QPushButton("Đăng nhập")
        self.btn_login.setObjectName("loginButton")
        self.btn_login.setCursor(Qt.PointingHandCursor)
        card_layout.addWidget(self.btn_login)

        card_layout.addSpacing(24)

        demo = QLabel("Phần mềm quản lý dịch vụ cung cấp điện tại khu dân cư")
        demo.setObjectName("demoText")
        demo.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(demo)

        card_layout.addStretch(1)

        root.addWidget(hero_panel, 6)
        root.addWidget(card, 4)

    def build_metric(self, value_text, label_text):
        widget = QFrame()
        widget.setObjectName("featureCard")

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(2)

        value = QLabel(value_text)
        value.setProperty("class", "heroMetricValue")

        label = QLabel(label_text)
        label.setProperty("class", "heroMetricLabel")

        layout.addWidget(value)
        layout.addWidget(label)
        return widget

    def build_feature_card(self, title_text, desc_text):
        card = QFrame()
        card.setObjectName("featureCard")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(6)

        title = QLabel(title_text)
        title.setProperty("class", "featureTitle")

        desc = QLabel(desc_text)
        desc.setProperty("class", "featureDesc")
        desc.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(desc)
        return card

    def clear_inputs(self):
        self.input_username.clear()
        self.input_password.clear()
