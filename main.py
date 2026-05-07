import sys
import traceback
from datetime import datetime
from pathlib import Path

from PyQt5.QtWidgets import QApplication, QMessageBox, QStackedWidget

from app.dto.requests import LoginRequestDTO
from app.services.app_context import AppContext
from ui.login import LoginForm
from ui.main_window import MainWindow


MESSAGE_BOX_STYLE = """
    QMessageBox {
        background-color: #ffffff;
        color: #18324b;
        font-family: "Segoe UI";
        font-size: 13px;
    }

    QMessageBox QLabel {
        background: transparent;
        color: #18324b;
        font-size: 13px;
        min-width: 320px;
    }

    QMessageBox QPushButton {
        background-color: #2f80ed;
        color: white;
        border: none;
        border-radius: 10px;
        padding: 8px 18px;
        min-width: 72px;
        font-weight: 700;
    }

    QMessageBox QPushButton:hover {
        background-color: #246bca;
    }
"""


class App(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.context = AppContext()

        self.setWindowTitle("Electric Management")
        self.resize(1365, 768)
        self.setMinimumSize(1100, 680)

        self.login = LoginForm()
        self.main_window = MainWindow(self.context)

        self.addWidget(self.login)
        self.addWidget(self.main_window)

        self.setCurrentWidget(self.login)

        self.login.btn_login.clicked.connect(self.handle_login)
        self.login.input_username.returnPressed.connect(self.handle_login)
        self.login.input_password.returnPressed.connect(self.handle_login)
        self.main_window.btn_logout.clicked.connect(self.handle_logout)

    def handle_login(self):
        try:
            username = self.login.input_username.text().strip()
            password = self.login.input_password.text().strip()
            account = self.context.auth_service.authenticate(LoginRequestDTO(username=username, password=password))
            if account:
                self.main_window.set_user_info(
                    user_id=account.id,
                    display_name=account.display_name,
                    role=account.role,
                )
                self.setCurrentWidget(self.main_window)
                self.login.clear_inputs()
            else:
                QMessageBox.warning(
                    self,
                    "Dang nhap that bai",
                    "Ten dang nhap, mat khau khong dung hoac tai khoan khong co quyen Admin.",
                )
        except Exception as exc:
            self.write_error_log(exc)
            QMessageBox.warning(
                self,
                "Khong the dang nhap",
                f"Ung dung gap loi khi mo man hinh chinh.\n"
                f"Chi tiet da ghi vao data/app_error.log\n\n{exc}",
            )

    def write_error_log(self, exc):
        log_dir = Path(__file__).resolve().parent / "data"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "app_error.log"
        log_file.write_text(
            f"[{datetime.now().isoformat(sep=' ', timespec='seconds')}] {exc}\n"
            f"{traceback.format_exc()}\n",
            encoding="utf-8",
        )

    def handle_logout(self):
        reply = QMessageBox.question(
            self,
            "Xac nhan dang xuat",
            "Ban co chac muon dang xuat khong?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.setCurrentWidget(self.login)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(MESSAGE_BOX_STYLE)
    window = App()
    window.show()
    sys.exit(app.exec_())
