import sys
from PyQt5.QtWidgets import QApplication, QStackedWidget, QMessageBox
from app.dto.requests import LoginRequestDTO
from app.services.app_context import AppContext
from ui.login import LoginForm
from ui.main_window import MainWindow


class App(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.context = AppContext()

        self.setWindowTitle("Phần mềm quản lý dịch vụ cung cấp điện tại khu dân cư")
        self.resize(1365, 768)
        self.setMinimumSize(1100, 680)

        self.login = LoginForm()
        self.main_window = MainWindow()

        self.addWidget(self.login)
        self.addWidget(self.main_window)

        self.setCurrentWidget(self.login)

        self.login.btn_login.clicked.connect(self.handle_login)
        self.login.input_username.returnPressed.connect(self.handle_login)
        self.login.input_password.returnPressed.connect(self.handle_login)
        self.main_window.btn_logout.clicked.connect(self.handle_logout)

    def handle_login(self):
        username = self.login.input_username.text().strip()
        password = self.login.input_password.text().strip()
        account = self.context.auth_service.authenticate(LoginRequestDTO(username=username, password=password))
        if account:
            self.main_window.set_user_info(
                display_name=account.display_name,
                role=account.role
            )
            self.setCurrentWidget(self.main_window)
            self.login.clear_inputs()
        else:
            QMessageBox.warning(
                self,
                "Đăng nhập thất bại",
                "Tên đăng nhập, mật khẩu không đúng hoặc tài khoản không có quyền Admin."
            )

    def handle_logout(self):
        reply = QMessageBox.question(
            self,
            "Xác nhận đăng xuất",
            "Bạn có chắc muốn đăng xuất không?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.setCurrentWidget(self.login)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec_())    
