from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFrame,
)
from PySide6.QtCore import Qt
from .dashboard import make_icon


class ExitConfirmDialog(QDialog):
    def __init__(self, required_phrase: str, parent=None):
        super().__init__(parent)
        self._phrase = required_phrase

        self.setWindowTitle("停止专注模式")
        self.setWindowIcon(make_icon())
        self.setMinimumSize(620, 280)
        self.resize(620, 280)
        self.setModal(True)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(16)

        layout.addWidget(self._build_header())

        prompt = QLabel("要停止当前专注流程，请输入下面这段确认文字。")
        prompt.setObjectName("mutedLabel")
        layout.addWidget(prompt)

        phrase_card = QFrame()
        phrase_card.setObjectName("phraseCard")
        phrase_layout = QVBoxLayout(phrase_card)
        phrase_layout.setContentsMargins(16, 14, 16, 14)

        phrase_label = QLabel(f'"{required_phrase}"')
        phrase_label.setObjectName("phraseLabel")
        phrase_label.setWordWrap(True)
        phrase_layout.addWidget(phrase_label)

        self._input = QLineEdit()
        self._input.setMinimumHeight(42)
        self._input.setPlaceholderText("输入确认文字")
        self._input.textChanged.connect(self._on_text_changed)
        self._input.returnPressed.connect(self._submit_if_ready)

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        self._btn_ok = QPushButton("停止专注")
        self._btn_ok.setMinimumSize(120, 40)
        self._btn_ok.setEnabled(False)
        self._btn_ok.setObjectName("dangerButton")
        self._btn_ok.setAutoDefault(False)
        self._btn_ok.setDefault(False)
        self._btn_ok.clicked.connect(self._submit_if_ready)

        btn_cancel = QPushButton("取消")
        btn_cancel.setMinimumSize(100, 40)
        btn_cancel.setObjectName("secondaryButton")
        btn_cancel.setAutoDefault(False)
        btn_cancel.setDefault(False)
        btn_cancel.clicked.connect(self.reject)

        btn_row.addWidget(self._btn_ok)
        btn_row.addWidget(btn_cancel)

        layout.addWidget(phrase_card)
        layout.addWidget(self._input)
        layout.addLayout(btn_row)

        self.setStyleSheet(self._dialog_style())
        self._on_text_changed()

    def _build_header(self) -> QFrame:
        header = QFrame()
        header.setObjectName("headerCard")

        layout = QVBoxLayout(header)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(4)

        title = QLabel("停止专注")
        title.setObjectName("headerTitle")

        subtitle = QLabel("这一步只会结束当前专注流程并解除限制，不会退出程序。")
        subtitle.setObjectName("headerSubtitle")
        subtitle.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        return header

    def _on_text_changed(self):
        self._btn_ok.setEnabled(self._input.text().strip() == self._phrase.strip())

    def _submit_if_ready(self):
        if self._btn_ok.isEnabled():
            self.accept()

    @staticmethod
    def _dialog_style() -> str:
        return """
            QDialog, QWidget {
                background-color: #f4f7fb;
                color: #0f172a;
                font-family: "Microsoft YaHei UI";
                font-size: 13px;
            }
            QLabel {
                background: transparent;
                border: none;
            }
            QFrame#headerCard {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #1e293b, stop: 1 #334155
                );
                border-radius: 20px;
            }
            QLabel#headerTitle {
                background: transparent;
                font-size: 20px;
                font-weight: 700;
                color: #ffffff;
            }
            QLabel#headerSubtitle {
                background: transparent;
                color: rgba(255, 255, 255, 0.84);
            }
            QLabel#mutedLabel {
                color: #64748b;
            }
            QFrame#phraseCard {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 16px;
            }
            QLabel#phraseLabel {
                font-size: 14px;
                font-weight: 700;
                color: #b91c1c;
            }
            QLineEdit {
                background-color: #ffffff;
                border: 1px solid #dbe2ea;
                border-radius: 14px;
                padding: 10px 12px;
            }
            QLineEdit:focus {
                border-color: #6366f1;
            }
            QPushButton {
                border-radius: 14px;
                padding: 10px 18px;
                border: 1px solid #dbe2ea;
                background-color: #ffffff;
                color: #1e293b;
                font-weight: 600;
            }
            QPushButton:hover {
                border-color: #c7d2fe;
                background-color: #f8fbff;
            }
            QPushButton#dangerButton {
                border: none;
                color: #ffffff;
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #dc2626, stop: 1 #f97316
                );
            }
            QPushButton#dangerButton:hover {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #ef4444, stop: 1 #fb923c
                );
            }
            QPushButton#dangerButton:disabled {
                background: #fecaca;
                color: #fff7ed;
            }
        """
