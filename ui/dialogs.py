from PyQt5.QtWidgets import QMessageBox


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
        min-width: 360px;
        padding: 4px;
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


def show_warning(parent, title: str, message: str) -> None:
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Warning)
    box.setWindowTitle(title)
    box.setText(message)
    box.setStandardButtons(QMessageBox.Ok)
    box.setStyleSheet(MESSAGE_BOX_STYLE)
    box.exec_()


def show_info(parent, title: str, message: str) -> None:
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Information)
    box.setWindowTitle(title)
    box.setText(message)
    box.setStandardButtons(QMessageBox.Ok)
    box.setStyleSheet(MESSAGE_BOX_STYLE)
    box.exec_()
