PAGE_STYLE = """
    QWidget {
        background: transparent;
        color: #18324b;
        font-family: "Segoe UI";
    }

    QFrame.card {
        background: #ffffff;
        border: 1px solid #d8e4f2;
        border-radius: 22px;
    }

    QFrame.softCard {
        background: #f6fbff;
        border: 1px solid #d8e7f5;
        border-radius: 18px;
    }

    QLabel.sectionEyebrow {
        color: #4c75a1;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1px;
        background: transparent;
    }

    QLabel.sectionTitle {
        color: #15385f;
        font-size: 21px;
        font-weight: 700;
        background: transparent;
    }

    QLabel.sectionDesc {
        color: #6f849b;
        font-size: 13px;
        line-height: 1.5;
        background: transparent;
    }

    QLabel.fieldLabel {
        color: #35516e;
        font-size: 13px;
        font-weight: 700;
        background: transparent;
    }

    QLabel.infoPill {
        color: #255d90;
        background: #edf6ff;
        border: 1px solid #cfe3f5;
        border-radius: 12px;
        padding: 7px 12px;
        font-size: 12px;
        font-weight: 700;
    }

    QLabel.metricLabel {
        color: #67829f;
        font-size: 12px;
        background: transparent;
    }

    QLabel.metricValue {
        color: #13375e;
        font-size: 22px;
        font-weight: 700;
        background: transparent;
    }

    QLabel.valueBox {
        color: #1f456d;
        background: #f7fbff;
        border: 1px solid #d7e5f4;
        border-radius: 14px;
        padding: 12px 14px;
        font-size: 13px;
        font-weight: 600;
    }

    QLineEdit,
    QComboBox,
    QDateEdit,
    QSpinBox,
    QDoubleSpinBox,
    QPlainTextEdit {
        background: #fbfdff;
        border: 1px solid #d5e1ee;
        border-radius: 14px;
        padding: 10px 14px;
        font-size: 13px;
        color: #18324b;
        min-height: 22px;
    }

    QLineEdit:focus,
    QComboBox:focus,
    QDateEdit:focus,
    QSpinBox:focus,
    QDoubleSpinBox:focus,
    QPlainTextEdit:focus {
        background: #ffffff;
        border: 1px solid #2f80ed;
    }

    QComboBox::drop-down,
    QDateEdit::drop-down {
        border: none;
        width: 26px;
    }

    QPushButton {
        color: white;
        border: none;
        border-radius: 14px;
        padding: 11px 16px;
        font-size: 13px;
        font-weight: 700;
        background-color: #2f80ed;
        min-height: 22px;
    }

    QPushButton:hover {
        background-color: #246bca;
    }

    QPushButton[variant="secondary"] {
        color: #23496f;
        background-color: #eef5fb;
        border: 1px solid #d2e2f1;
    }

    QPushButton[variant="secondary"]:hover {
        background-color: #dfeefa;
    }

    QPushButton[variant="accent"] {
        background-color: #143d68;
    }

    QPushButton[variant="accent"]:hover {
        background-color: #0f3154;
    }

    QTableWidget {
        border: none;
        background: #ffffff;
        gridline-color: #edf2f8;
        alternate-background-color: #f8fbfe;
        selection-background-color: #dcecff;
        selection-color: #14385e;
        font-size: 13px;
        border-radius: 14px;
    }

    QHeaderView::section {
        background: #eef5fb;
        color: #163d66;
        padding: 11px 8px;
        border: none;
        font-size: 12px;
        font-weight: 700;
    }
"""
